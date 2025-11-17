import torch
from torch.utils.data import DataLoader
from tqdm.notebook import tqdm


class Training:
    def __init__(
        self,
        model,
        device,
        data_train,
        data_val,
        selected_features,
        concept_name_id,
        duration_seconds_id,
        loss_obj,
        optimize_values,
        writer,
        save_model_n_th_epoch: int = 0,
        saving_path: str = "model.pkl",
    ):

        self.device = device
        print("Device: ", device)
        self.data_train = data_train
        self.data_val = data_val
        self.selected_features = selected_features

        self.selected_cat_ids = [i for i, f in enumerate(self.data_train.all_categories[0]) if f[0] in self.selected_features[0]]
        self.selected_num_ids = [i for i, f in enumerate(self.data_train.all_categories[1]) if f[0] in self.selected_features[1]]

        self.concept_name_id = concept_name_id
        self.duration_seconds_id = duration_seconds_id

        self.model = model.to(self.device)

        self.loss_obj = loss_obj

        # Standard Optimization parameters
        self.optimize_values = optimize_values
        self.optimizer = optimize_values["optimizer"]
        print("Optimizer: ", self.optimizer)
        self.scheduler = optimize_values["scheduler"]
        print("Scheduler: ", self.scheduler)
        self.epochs = optimize_values["epochs"]
        print("Epochs: ", self.epochs)
        self.mini_batches = optimize_values["mini_batches"]
        print("Mini baches: ", self.mini_batches)
        self.shuffle = optimize_values["shuffle"]
        print("Shuffle batched dataset: ", self.shuffle)

        # TensorBoard
        self.writer = writer

        # Model saving
        self.save_model_n_th_epoch = save_model_n_th_epoch
        self.saving_path = saving_path

    def split_input_target(self, cats, nums):
        """
        Split input data into prefixes and target.
        
        Args:
            cats: List of categorical feature tensors
            nums: List of numerical feature tensors
        
        Returns:
            prefixes: Dictionary with 'cats' and 'nums' excluding duration_seconds from last timestep
            target: Duration seconds values from the last timestep
        """
        # Move tensors to device
        selected_cats = [cats[i].to(self.device) for i in self.selected_cat_ids]
        selected_nums = [nums[i].to(self.device) for i in self.selected_num_ids]
        
        # Extract target: duration_seconds from the last timestep
        # Find the duration_seconds tensor and extract from last timestep
        # Shape: [batch_size]
        target = nums[self.duration_seconds_id][:, -1]
        target = target.unsqueeze(-1)  # Shape: [batch_size, 1]

        prefixes = {
            'cats': selected_cats,
            'nums': selected_nums
        }
        
        return prefixes, target

    def train(self):
        self.model.train()

        train_losses_unc = []

        val_losses_std = []
        val_losses_unc = []

        # Validation dataloader
        val_dataloader = DataLoader(
            dataset=self.data_val,
            batch_size=self.mini_batches,
            shuffle=self.shuffle,
            num_workers=4,
            pin_memory=False,
        )

        for epoch in tqdm(range(self.epochs)):#range(self.epochs): #
            self.model.train()

            # Train dataloader
            train_dataloader = DataLoader(
                dataset=self.data_train,
                batch_size=self.mini_batches,
                shuffle=self.shuffle,
                num_workers=4,
                pin_memory=False,
            )

            total_unc = 0
            num_batches = 0

            for i, train_cases in tqdm(enumerate(train_dataloader), total=len(train_dataloader)):#enumerate(train_dataloader):
                cats, nums, _ = train_cases

                # Get the prefixes to process, the target case elapsed time, and the new batch size as zero tensors are skipped:
                prefixes, target = self.split_input_target(cats, nums)
                target = target.to(self.device)

                # Prediction:
                means, logvars = self.model(input=prefixes)

                # per‑sample losses, shape [V]
                loss_unc = self.loss_obj.regression_heteroscedastic_loss(
                    true=target, mean=means, log_var=logvars
                )

                weight_reg, bias_reg = self.model.regularizer()
                reg_term = weight_reg + bias_reg

                loss_unc = loss_unc + reg_term.to(self.device)

                # backward on the total hetero loss
                loss_unc.backward()

                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                self.optimizer.step()

                self.optimizer.zero_grad()

                # Mean loss over all samples in batch of size V
                total_unc += loss_unc.item()
                num_batches += 1

            # epoch averages train loss:
            epoch_unc = total_unc / num_batches

            # Current learning rate
            current_lr = self.scheduler.optimizer.param_groups[0]["lr"]

            # Prints per Epoch:
            tqdm.write(f"Epoch [{epoch+1}/{self.epochs}], Learning Rate: {current_lr}")

            tqdm.write(f"Training: Avg Attenuated Training Loss: {epoch_unc:.4f}")

            train_losses_unc.append(epoch_unc)

            epoch_loss_val_std, epoch_loss_val_unc = self._validate(
                loader=val_dataloader
            )

            tqdm.write(
                f"Validation: Avg Standard Validation Loss: {epoch_loss_val_std:.4f}"
            )
            tqdm.write(
                f"Validation: Avg Attenuated Validation Loss: {epoch_loss_val_unc:.4f}"
            )

            val_losses_std.append(epoch_loss_val_std)
            val_losses_unc.append(epoch_loss_val_unc)

            # Tensorboard writer:
            # Hyperparameters
            self.writer.add_scalars(
                "Hyperparameter:",
                {
                    "Learning Rate": current_lr,
                },
                epoch + 1,
            )

            # Total losses
            self.writer.add_scalars(
                "Total Losses",
                {
                    "Training Total": epoch_unc,
                    "Stdandard Validation Total": epoch_loss_val_std,
                    "Uncertainty Validation Total": epoch_loss_val_unc,
                },
                epoch + 1,
            )

            # Adjust the learning rate if necessary
            tqdm.write(f"Validation Loss for Scheduler: {epoch_loss_val_std:.4f}")

            # Adjust learning rate
            self.scheduler.step(epoch_loss_val_std)

            if (i + 1) % self.save_model_n_th_epoch == 0:
                tqdm.write("saving model")
                self.model.save(self.saving_path)

        print("Training complete.")

        self.model.save(self.saving_path)
        tqdm.write(f"Model saved to path: {self.saving_path}")

    def _validate(self, loader):
        self.model.eval()

        total_std = total_unc = 0
        num_batches = 0
        with torch.no_grad():
            for cats, nums, _ in loader:
                prefixes, target = self.split_input_target(cats, nums)
                target = target.to(self.device)

                means, logvars = self.model(input=prefixes)
                loss_unc = self.loss_obj.regression_heteroscedastic_loss(
                    true=target, mean=means, log_var=logvars
                )

                loss_std = self.loss_obj.regression_homoscedastic_loss(
                    true=target, mean=means
                )

                total_unc += loss_unc.item()
                total_std += loss_std.item()
                num_batches += 1

        return total_std / num_batches, total_unc / num_batches
