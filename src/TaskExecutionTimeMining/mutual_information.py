import numpy as np
from scipy.stats import gaussian_kde
import statsmodels.api as sm
from tqdm.notebook import tqdm

def cross_validation_kde(vals):
    settings = sm.nonparametric.EstimatorSettings(efficient=True,
                                                  randomize=True,
                                                  n_sub=1000,
                                                  n_res=10,
                                                  return_only_bw=True,
                                                  n_jobs=1)
    if len(vals.shape) == 1:
        # KDEUnivariate does not support cv_ls, therefore we use KDEMultivariate
        vals = np.array(vals, dtype=np.float64, order='C', copy=True).reshape(-1, 1).copy()        #find best bandwidth using cross-validation
        kde = sm.nonparametric.KDEMultivariate(vals, 'c', bw='cv_ls', defaults=settings)
        bandwidth = kde.bw
        # fit kde model on all samples using the best bandwidth
        kde = sm.nonparametric.KDEMultivariate(vals, 'c', bw=bandwidth)
        return lambda x: kde.pdf(x)
    else:
        #find best bandwidth using cross-validation
        kde = sm.nonparametric.KDEMultivariate(vals, 'cc', bw='cv_ls', defaults=settings)
        bandwidth = kde.bw
        # fit kde model on all samples using the best bandwidth
        kde = sm.nonparametric.KDEMultivariate(vals, 'cc', bw=bandwidth)
        # return a function that evaluates the pdf at given points
        return lambda x: kde.pdf(x)


def MI_discrete_continuous(df, col, target_col='duration_seconds',
                gridsize=4096,  # power of two → cheap FFT in KDE
                eps=1e-12,
                padding=0.05,
                kde=gaussian_kde,
                enable_tqdm = False):
    """
    Mutual information I(col ; target_col) for a *discrete* X=col and
    a *continuous* Y=target_col, using Gaussian KDE + log‑space integration.
    """
    # ------------------  Pre‑compute pieces that do not depend on x  ----------
    y_vals = df[target_col].to_numpy()
    y_min, y_max = y_vals.min(), y_vals.max()
    padding = padding * (y_max - y_min)

    # Fixed grid avoids adaptive sampling where the KDE is unstable
    grid = np.linspace(y_min - padding, y_max + padding, gridsize)

    # p(y) and its log once
    kde_y      = kde(y_vals)
    p_y_grid   = np.clip(kde_y(grid), eps, None)
    log_p_y    = np.log(p_y_grid)

    # p(x) for every category, with log once
    p_x        = df[col].value_counts(normalize=True)
    log_p_x    = np.log(p_x)

    # ------------------  Loop over each category of X  -----------------------
    mi = 0.0
    for x, log_px in tqdm(log_p_x.items(), disable=not enable_tqdm, desc='Calculating MI', total=log_p_x.shape[0]):
        subset = df.loc[df[col] == x, target_col]
        if len(subset.unique()) < 2:
            continue
        # KDE for p(y | x)  ≡  p(x,y) / p(x)
        kde_xy     = kde(df.loc[df[col] == x, target_col])
        p_xy_grid = kde_xy(grid)

        p_joint_grid = p_xy_grid * p_x[x]
        p_joint_grid = np.clip(p_joint_grid, eps, None)

        log_p_joint = np.log(p_joint_grid)

        # integrand:  p_xy * (log p_xy − log p_x − log p_y)
        # do *all* log/exp algebra first, then multiply once
        integrand  = p_joint_grid * (log_p_joint - log_px - log_p_y)

        # trapz is deterministic, vectorised, and perfectly fine in 1‑D
        mi         += np.trapezoid(integrand, grid, dx=grid[1] - grid[0])

    return mi

def MI_continuous_continuous(df, col, target_col='duration_seconds',
                             gridsize=4096,  # power of two → cheap FFT in KDE
                             eps=1e-12,
                             padding=0.05,
                             kde=gaussian_kde,
                             enable_tqdm = False):
    """
    Mutual information I(col ; target_col) for a *continuous* X=col and
    a *continuous* Y=target_col, using Gaussian KDE + log‑space integration.
    """
    if enable_tqdm:
        pbar = tqdm(total=3, desc='Calculating MI')
    # ------------------  Pre‑compute pieces that do not depend on x  ----------
    x_vals = df[col].to_numpy()
    y_vals = df[target_col].to_numpy()
    x_min, x_max = x_vals.min(), x_vals.max()
    y_min, y_max = y_vals.min(), y_vals.max()
    x_padding = padding * (x_max - x_min)
    y_padding = padding * (y_max - y_min)

    x_grid = np.linspace(x_min - x_padding, x_max + x_padding, gridsize)
    y_grid = np.linspace(y_min - y_padding, y_max + y_padding, gridsize)

    dx = x_grid[1] - x_grid[0]
    dy = y_grid[1] - y_grid[0]

    kde_x     = kde(x_vals)
    if enable_tqdm:
        pbar.update(1)
    kde_y     = kde(y_vals)
    if enable_tqdm:
        pbar.update(1)

    p_x_grid  = np.clip(kde_x(x_grid), eps, None)
    p_y_grid  = np.clip(kde_y(y_grid), eps, None)

    log_p_x   = np.log(p_x_grid)
    log_p_y    = np.log(p_y_grid)

    # Bivariate KDE
    kde_xy = kde(np.vstack([x_vals, y_vals]))
    if enable_tqdm:
        pbar.update(1)
    x_mesh, y_mesh = np.meshgrid(x_grid, y_grid, indexing='ij')  # Shape: (gridsize, gridsize)
    xy_samples = np.vstack([x_mesh.ravel(), y_mesh.ravel()])
    p_xy = np.clip(kde_xy(xy_samples), eps, None).reshape(gridsize, gridsize)
    log_p_xy = np.log(p_xy)

    # Compute MI: ∬ p(x, y) * (log p(x, y) - log p(x) - log p(y)) dx dy
    log_p_x_mesh = log_p_x[:, np.newaxis]  # shape (gridsize, 1)
    log_p_y_mesh = log_p_y[np.newaxis, :]  # shape (1, gridsize)

    integrand = p_xy * (log_p_xy - log_p_x_mesh - log_p_y_mesh)
    mi = np.sum(integrand) * dx * dy

    if enable_tqdm:
        pbar.close()
    return mi

def MI_discrete_discrete(df, col, target_col):
    p_x = df[col].value_counts(normalize=True)
    p_y = df[target_col].value_counts(normalize=True)
    joint_counts = df.groupby([col, target_col]).size()
    p_xy = joint_counts / len(df)

    mi = 0.0
    for (x, y), pxy in p_xy.items():
        px = p_x[x]
        py = p_y[y]
        mi += pxy * np.log(pxy / (px * py))
    return mi
