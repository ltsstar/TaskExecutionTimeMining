#!/usr/bin/env python
"""Fast prefix-to-duration predictions using the trained stochastic LSTM model.

This module mirrors the notebook logic in ``test.ipynb`` but exposes a reusable,
scriptable interface that can be invoked millions of times without reloading the
model or encoder stack each time.

Typical usage (after activating the repository environment):

>>> predictor = PrefixDurationPredictor()
>>> prefix = [
...     {
...         "Case ID": "Case_123",
...         "Complete Timestamp_start": "2012-01-03 11:25:00.000",
...         "Activity_start": "Register",
...         "Resource_start": "clerk_7",
...         "seconds_in_day": 41100,
...         "day_in_week": 1,
...         "duration_seconds": 3600,
...     },
...     {
...         "Case ID": "Case_123",
...         "Complete Timestamp_start": "2012-01-03 12:05:00.000",
...         "Activity_start": "Examine",
...         "Resource_start": "clerk_4",
...         "seconds_in_day": 43500,
...         "day_in_week": 1,
...         "duration_seconds": 5400,
...     },
... ]
>>> predictor.predict(prefix)
>>> predictor.sample_training_case(case_index=0)  # helper if you prefer real cases

Each prediction accepts a list of dictionaries (one per event of a case) and
returns the mean and standard deviation for the next activity duration in
seconds. The heavy artifacts (model checkpoint, encoder/decoder, and training
log) are loaded once during class construction to keep repeated invocations
fast.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import types
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableSequence, Optional, Sequence

import torch
import pandas as pd

NOTEBOOK_DIR = Path(__file__).resolve().parent
LSTM_ROOT = (NOTEBOOK_DIR / "../..").resolve()
LOADER_DIR = (NOTEBOOK_DIR / "../../../../load/event_log_loader").resolve()
ENCODED_DIR = (NOTEBOOK_DIR / "../../../../load/encoded_data").resolve()
TRANSFORMED_LOG_DIR = (NOTEBOOK_DIR / "../../../../../transformed_event_logs").resolve()
MODEL_DIR = (NOTEBOOK_DIR / "../training_variational_dropout/Helpdesk").resolve()

TRAIN_DATA_PATH = (ENCODED_DIR / "helpdesk_all_1_train.pkl").resolve()
DEFAULT_EVENT_LOG_PROPERTIES = {
    "case_name": "Case ID",
    "concept_name": "Activity_start",
    "timestamp_name": "Complete Timestamp_start",
    "date_format": "%Y-%m-%d %H:%M:%S.%f",
    "time_since_case_start_column": "",
    "time_since_last_event_column": "",
    "day_in_week_column": "day_in_week",
    "seconds_in_day_column": "seconds_in_day",
    "min_suffix_size": 1,
    "train_validation_size": 0.15,
    "test_validation_size": 0.0,
    "window_size": "auto",
    "categorical_columns": ["Activity_start", "Resource_start"],
    "continuous_columns": ["seconds_in_day", "day_in_week", "duration_seconds"],
    "continuous_positive_columns": [],
}
DEFAULT_SELECTED_CAT_ATTRIBUTES = ("Activity_start", "Resource_start")
DEFAULT_SELECTED_NUM_ATTRIBUTES = ("seconds_in_day", "day_in_week")

for extra_path in (LSTM_ROOT, LOADER_DIR):
    if str(extra_path) not in sys.path:
        sys.path.insert(0, str(extra_path))

try:  # pragma: no cover - defensive shim for minimal environments
    import tqdm as _tqdm  # type: ignore
except ModuleNotFoundError:  # noqa: F841
    tqdm_module = types.ModuleType("tqdm")
    notebook_module = types.ModuleType("tqdm.notebook")

    def _identity_tqdm(iterable: Iterable, *_, **__) -> Iterable:
        return iterable

    notebook_module.tqdm = _identity_tqdm  # type: ignore[attr-defined]
    tqdm_module.notebook = notebook_module  # type: ignore[attr-defined]
    sys.modules["tqdm"] = tqdm_module
    sys.modules["tqdm.notebook"] = notebook_module

import new_event_log_loader  # type: ignore  # noqa: E402
from stochasticLSTM.model import StochasticLSTM  # type: ignore  # noqa: E402


@dataclass(slots=True)
class Prediction:
    """Container for a single prefix prediction."""

    case_id: str
    prefix_length: int
    predicted_mean_seconds: float
    predicted_std_seconds: float
    predicted_mean_minutes: float
    predicted_std_minutes: float
    true_duration_seconds: Optional[float] = None
    true_duration_minutes: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PrefixDurationPredictor:
    """Loads the trained LSTM artifacts once and serves fast predictions."""

    def __init__(
        self,
        *,
        train_loader_path: Path = TRAIN_DATA_PATH,
        model_dir: Path = MODEL_DIR,
        model_path: Optional[Path] = None,
        event_log_properties: Mapping[str, Any] = DEFAULT_EVENT_LOG_PROPERTIES,
        selected_cat_attributes: Sequence[str] = DEFAULT_SELECTED_CAT_ATTRIBUTES,
        selected_num_attributes: Sequence[str] = DEFAULT_SELECTED_NUM_ATTRIBUTES,
        device: Optional[str] = None,
    ) -> None:
        self.train_loader_path = train_loader_path
        self.event_log_properties = dict(event_log_properties)
        self.selected_cat_attributes = tuple(selected_cat_attributes)
        self.selected_num_attributes = tuple(selected_num_attributes)
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        self._validate_files_exist(train_loader_path, model_dir)


        self.train_dataset = torch.load(train_loader_path, map_location="cpu", weights_only=False)
        self.encoder_decoder = self.train_dataset.encoder_decoder
        self.case_name_col = self.encoder_decoder.case_name
        self.timestamp_col = self.event_log_properties["timestamp_name"]
        if not hasattr(self.encoder_decoder, "timestamp_name"):
            # Older pickles did not persist the timestamp attribute. Keep the
            # encoder backward compatible by injecting it at runtime.
            self.encoder_decoder.timestamp_name = self.timestamp_col

        self.selected_cat_ids = [
            idx
            for idx, feature in enumerate(self.train_dataset.all_categories[0])
            if feature[0] in self.selected_cat_attributes
        ]
        self.selected_num_ids = [
            idx
            for idx, feature in enumerate(self.train_dataset.all_categories[1])
            if feature[0] in self.selected_num_attributes
        ]
        self.duration_seconds_id = [
            idx
            for idx, feature in enumerate(self.train_dataset.all_categories[1])
            if feature[0] == "duration_seconds"
        ][0]

        self.duration_scaler = self.encoder_decoder.continuous_encoders["duration_seconds"]
        self.duration_scale = float(self.duration_scaler.scale_[0])
        self.duration_mean = float(self.duration_scaler.mean_[0])

        checkpoint_to_load = model_path or self._latest_checkpoint(model_dir)
        self.model = self._load_lstm_checkpoint(checkpoint_to_load)
        self._disable_dropout_in_model()

        self.required_columns = self._collect_required_columns()

    def _disable_dropout_in_model(self) -> None:
        p_logit = torch.full([1], -30.0).to(self.device)
        self.model.first_layer.p_logit = p_logit
        for lstm_cell in self.model.hidden_layers:
            lstm_cell.p_logit = p_logit


    def _validate_files_exist(self, *paths: Path) -> None:
        missing = [str(p) for p in paths if not Path(p).exists()]
        if missing:
            raise FileNotFoundError(
                "Missing required artifact(s): \n" + "\n".join(missing)
            )

    def _latest_checkpoint(self, model_dir: Path) -> Path:
        checkpoints = sorted(model_dir.glob("*.pkl"), key=lambda p: p.stat().st_mtime)
        if not checkpoints:
            raise FileNotFoundError(f"No model checkpoints found in {model_dir}")
        return checkpoints[-1]

    def _load_lstm_checkpoint(self, checkpoint_path: Path) -> StochasticLSTM:
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        checkpoint["kwargs"].pop("input_size", None)
        checkpoint["kwargs"]["device"] = str(self.device)
        model_instance = StochasticLSTM(**checkpoint["kwargs"])
        model_instance.load_state_dict(checkpoint["model_state_dict"])
        return model_instance.to(self.device).eval()

    def _collect_required_columns(self) -> tuple[str, ...]:
        columns = {self.case_name_col, self.timestamp_col, self.event_log_properties["concept_name"]}
        for col in self.encoder_decoder.categorical_columns:
            columns.add(col)
        for col in self.encoder_decoder.continuous_columns + self.encoder_decoder.continuous_positive_columns:
            columns.add(col)
        return tuple(columns)

    def _coerce_prefix_dataframe(
        self, prefix_events: Sequence[Mapping[str, Any]] | pd.DataFrame
    ) -> pd.DataFrame:
        """Return a defensive copy of the incoming prefix as a DataFrame."""
        if isinstance(prefix_events, pd.DataFrame):
            # Work on a shallow copy so we can safely mutate columns without
            # touching the caller's frame.
            return prefix_events.copy(deep=True)

        if isinstance(prefix_events, Sequence):
            if not prefix_events:
                raise ValueError("prefix_events must contain at least one event dictionary")
            return pd.DataFrame(prefix_events)

        raise TypeError(
            "prefix_events must be either a pandas DataFrame or a sequence of mapping objects"
        )

    def predict(
        self,
        prefix_events: Sequence[Mapping[str, Any]] | pd.DataFrame,
        *,
        case_id: Optional[str] = None,
    ) -> Prediction:
        encoded_sample, prefix_df = self._encode_prefix(prefix_events, case_id=case_id)
        model_input, nums_batched = self._prepare_model_payload(encoded_sample)

        with torch.no_grad():
            pred_mean_norm, pred_logvar_norm = self.model(model_input)

        pred_mean_norm = float(pred_mean_norm.squeeze().item())
        pred_logvar_norm = float(pred_logvar_norm.squeeze().item())

        pred_mean_seconds = pred_mean_norm * self.duration_scale + self.duration_mean
        pred_std_seconds = math.sqrt(math.exp(pred_logvar_norm)) * self.duration_scale

        return pred_mean_seconds, pred_std_seconds
        '''
        true_duration = self._extract_true_duration(prefix_df)

        return Prediction(
            case_id=str(prefix_df[self.case_name_col].iloc[-1]),
            prefix_length=len(prefix_df),
            predicted_mean_seconds=pred_mean_seconds,
            predicted_std_seconds=pred_std_seconds,
            predicted_mean_minutes=pred_mean_seconds / 60.0,
            predicted_std_minutes=pred_std_seconds / 60.0,
            true_duration_seconds=true_duration,
            true_duration_minutes=(true_duration / 60.0) if true_duration is not None else None,
        )
        '''

    def predict_all_prefixes(
        self,
        prefix_events: Sequence[Mapping[str, Any]] | pd.DataFrame,
        *,
        case_id: Optional[str] = None,
    ) -> list[Prediction]:
        encoded_sample, prefix_df = self._encode_prefix(prefix_events, case_id=case_id)
        cats_full, nums_full, _ = encoded_sample
        predictions: list[Prediction] = []

        for prefix_len in range(1, cats_full[0].shape[0] + 1):
            cats_prefix = [tensor[:prefix_len] for tensor in cats_full]
            nums_prefix = [tensor[:prefix_len] for tensor in nums_full]
            batched_cats = [tensor.unsqueeze(0) for tensor in cats_prefix]
            batched_nums = [tensor.unsqueeze(0) for tensor in nums_prefix]
            selected_cats = [batched_cats[idx] for idx in self.selected_cat_ids]
            selected_nums = [batched_nums[idx] for idx in self.selected_num_ids]

            with torch.no_grad():
                pred_mean_norm, pred_logvar_norm = self.model({"cats": selected_cats, "nums": selected_nums})

            pred_mean_norm = float(pred_mean_norm.squeeze().item())
            pred_logvar_norm = float(pred_logvar_norm.squeeze().item())
            pred_mean_seconds = pred_mean_norm * self.duration_scale + self.duration_mean
            pred_std_seconds = math.sqrt(math.exp(pred_logvar_norm)) * self.duration_scale

            predictions.append(
                Prediction(
                    case_id=str(prefix_df[self.case_name_col].iloc[-1]),
                    prefix_length=prefix_len,
                    predicted_mean_seconds=pred_mean_seconds,
                    predicted_std_seconds=pred_std_seconds,
                    predicted_mean_minutes=pred_mean_seconds / 60.0,
                    predicted_std_minutes=pred_std_seconds / 60.0,
                    true_duration_seconds=self._extract_true_duration(prefix_df) if prefix_len == len(prefix_df) else None,
                    true_duration_minutes=(
                        self._extract_true_duration(prefix_df) / 60.0 if prefix_len == len(prefix_df) and self._extract_true_duration(prefix_df) is not None else None
                    ),
                )
            )
        return predictions

    def _encode_prefix(
        self,
        prefix_events: Sequence[Mapping[str, Any]] | pd.DataFrame,
        *,
        case_id: Optional[str] = None,
    ) -> tuple[tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...], tuple[str, ...]], pd.DataFrame]:
        prefix_df = self._coerce_prefix_dataframe(prefix_events)

        if self.case_name_col not in prefix_df.columns:
            inferred_case_id = case_id or "inference_case"
            prefix_df[self.case_name_col] = inferred_case_id
        elif case_id is not None:
            prefix_df[self.case_name_col] = case_id

        prefix_df = prefix_df.sort_values(self.timestamp_col).reset_index(drop=True)
        self._ensure_required_columns(prefix_df)

        encoded_case, _ = self.encoder_decoder.encode_df(prefix_df)
        case_cat_tensors, case_num_tensors, case_ids = encoded_case
        sample_idx = len(case_ids) - 1
        encoded_sample = (
            tuple(t[sample_idx] for t in case_cat_tensors),
            tuple(t[sample_idx] for t in case_num_tensors),
            case_ids[sample_idx],
        )
        return encoded_sample, prefix_df

    def _ensure_required_columns(self, prefix_df: pd.DataFrame) -> None:
        missing_cols = [col for col in self.required_columns if col not in prefix_df.columns]
        if missing_cols:
            raise ValueError(
                "Prefix data missing required column(s): " + ", ".join(missing_cols)
            )

        for col in self.encoder_decoder.categorical_columns:
            prefix_df[col] = prefix_df[col].apply(lambda x: x if pd.isna(x) else str(x)).astype(object)

        for col in self.encoder_decoder.continuous_columns + self.encoder_decoder.continuous_positive_columns:
            prefix_df[col] = pd.to_numeric(prefix_df[col], errors="coerce").astype("float32")

    def _prepare_model_payload(
        self, encoded_sample: tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...], Any]
    ) -> tuple[dict[str, list[torch.Tensor]], list[torch.Tensor]]:
        cats_full, nums_full, _ = encoded_sample
        cats_batched = [tensor.unsqueeze(0) for tensor in cats_full]
        nums_batched = [tensor.unsqueeze(0) for tensor in nums_full]
        selected_cats = [cats_batched[idx] for idx in self.selected_cat_ids]
        selected_nums = [nums_batched[idx] for idx in self.selected_num_ids]
        return {"cats": selected_cats, "nums": selected_nums}, nums_batched

    def _extract_true_duration(self, prefix_df: pd.DataFrame) -> Optional[float]:
        if "duration_seconds" not in prefix_df.columns:
            return None
        value = prefix_df["duration_seconds"].iloc[-1]
        if pd.isna(value):
            return None
        return float(value)