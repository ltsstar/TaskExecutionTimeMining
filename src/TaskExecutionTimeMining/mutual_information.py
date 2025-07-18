import numpy as np
from scipy.stats import gaussian_kde
from tqdm.notebook import tqdm
from numba import cuda
from joblib import parallel_backend
import multiprocessing as mp
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KernelDensity
import math

def cross_validation_kde(vals, n_sub=2500, cv=3, n_runs=5, backend='threading'):
    # If input shape is (n_features, n_samples), transpose it to (n_samples, n_features)
    if vals.ndim == 2 and vals.shape[0] < vals.shape[1]:
        vals = vals.T  # transpose to (samples, features)
    
    # Ensure 2D, float64, C-contiguous
    vals = np.require(vals, dtype=np.float64, requirements=['C', 'W', 'O'])
    if vals.ndim == 1:
        vals = vals.reshape(-1, 1)
    elif vals.ndim > 2:
        raise ValueError("Input array must be 1D or 2D")

    n_samples = vals.shape[0]
    bandwidth_list = []
    for _ in range(n_runs):
        # Subsample for bandwidth selection if needed
        if n_samples > n_sub:
            idx = np.random.choice(n_samples, n_sub, replace=False)
            vals_sub = vals[idx]
        else:
            vals_sub = vals

        # Compute rule-of-thumb bandwidth (Silverman's rule)
        d = vals_sub.shape[1]  # Number of dimensions
        rule_of_thumb = n_sub ** (-1 / (d + 4))
        #print(f"Rule of thumb bandwidth: {rule_of_thumb}")
        
        # Define a focused bandwidth grid
        bandwidths = np.logspace(
            np.log10(rule_of_thumb / 5),
            np.log10(rule_of_thumb * 5),
            50
        )
        bandwidths = np.logspace(-3, 0, 50) # standardized data
        adjusted_cv = min(cv, len(vals_sub))  # Adjust cv to not exceed number of bandwidths

        with parallel_backend(backend, n_jobs=-1):
            # Grid search on subset
            grid = GridSearchCV(
                estimator=KernelDensity(kernel='gaussian'),
                param_grid={'bandwidth': bandwidths},
                cv=adjusted_cv,
                n_jobs=-1
            )
            grid.fit(vals_sub)
            bandwidth_list.append(grid.best_params_['bandwidth'])
    avg_bandwidth = np.mean(bandwidth_list)
    kde = KernelDensity(kernel='gaussian', bandwidth=avg_bandwidth)
    kde.fit(vals_sub)
    #kde.fit(vals)  # Refit on full data with best bandwidth
    #kde = grid.best_estimator_
    print(f"Best bandwidth: {avg_bandwidth}")
    def pdf(x):
        x = np.asarray(x, dtype=np.float64)
        # Handle 1D array shape
        if x.ndim == 1:
            x = x[:, np.newaxis]
        # Handle 2D input shape possibly transposed
        elif x.ndim == 2:
            if x.shape[0] == vals.shape[1] and x.shape[1] != vals.shape[1]:
                x = x.T
        else:
            raise ValueError("Input to pdf must be 1D or 2D array")
        return np.exp(kde.score_samples(x))
    pdf.covariance = np.cov(vals, rowvar=False)  # Store covariance for MI calculations
    return pdf


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
    p_y_grid   = p_y_grid / (np.sum(p_y_grid) * (grid[1] - grid[0]))  # Normalize
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

def H_continuous(df, col, gridsize=1024, eps=1e-12, padding=0.05,
                 kde=gaussian_kde, enable_tqdm=False):
    x_vals = df[col].to_numpy()

    kde = kde(x_vals)
    x_min, x_max = x_vals.min(), x_vals.max()
    x_padding = padding * (x_max - x_min)

    x_grid = np.linspace(x_min - x_padding, x_max + x_padding, gridsize)
    probs = kde(x_grid)
    probs = probs[probs > 0]  # avoid log(0)
    dx = x_grid[1] - x_grid[0]
    return -np.sum(probs * np.log2(probs)) * dx


def MI_continuous_continuous(df, col, target_col='duration_seconds',
                             gridsize=256,  # power of two → cheap FFT in KDE
                             eps=1e-12,
                             padding=0.05,
                             kde=gaussian_kde,
                             return_densities = False,
                             enable_tqdm = False):
    """
    Mutual information I(col ; target_col) for a *continuous* X=col and
    a *continuous* Y=target_col, using Gaussian KDE + log‑space integration.
    """
    if col == target_col:
        return H_continuous(df, col, gridsize=gridsize, eps=eps, padding=padding, kde=kde, enable_tqdm=enable_tqdm)
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
    p_x_grid = p_x_grid / (np.sum(p_x_grid) * dx)
    p_y_grid  = np.clip(kde_y(y_grid), eps, None)
    p_y_grid = p_y_grid / (np.sum(p_y_grid) * dy)

    log_p_x   = np.log(p_x_grid)
    log_p_y    = np.log(p_y_grid)

    # Bivariate KDE
    kde_xy = kde(np.vstack([x_vals, y_vals]))
    if enable_tqdm:
        pbar.update(1)
    x_mesh, y_mesh = np.meshgrid(x_grid, y_grid, indexing='ij')  # Shape: (gridsize, gridsize)
    xy_samples = np.vstack([x_mesh.ravel(), y_mesh.ravel()])
    p_xy = np.clip(kde_xy(xy_samples), eps, None).reshape(gridsize, gridsize)
    p_xy = p_xy / (np.sum(p_xy) * dx * dy)  # Normalize
    log_p_xy = np.log(p_xy)

    # Compute MI: ∬ p(x, y) * (log p(x, y) - log p(x) - log p(y)) dx dy
    log_p_x_mesh = log_p_x[:, np.newaxis]  # shape (gridsize, 1)
    log_p_y_mesh = log_p_y[np.newaxis, :]  # shape (1, gridsize)

    integrand = p_xy * (log_p_xy - log_p_x_mesh - log_p_y_mesh)
    mi = np.sum(integrand) * dx * dy

    if enable_tqdm:
        pbar.close()
    if return_densities:
        return mi, p_x_grid, p_y_grid, p_xy
    else:
        return mi


def MI_continuous_continuous_CUDA(df, col, target_col='duration_seconds',
                                  gridsize=1024, eps=1e-12, padding=0.05,
                                  kde=gaussian_kde, enable_tqdm=False):
    if col == target_col:
        return H_continuous(df, col, gridsize=gridsize, eps=eps, padding=padding, 
                           kde=kde, enable_tqdm=enable_tqdm)
    if enable_tqdm:
        from tqdm import tqdm
        pbar = tqdm(total=3, desc='Calculating MI')

    # Extract data and create grids
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

    # Compute 1D KDEs (still on CPU for simplicity; see optimization note below)
    kde_x = kde(x_vals)
    if enable_tqdm:
        pbar.update(1)
    kde_y = kde(y_vals)
    if enable_tqdm:
        pbar.update(1)
    p_x_grid = np.clip(kde_x(x_grid), eps, None)
    p_y_grid = np.clip(kde_y(y_grid), eps, None)
    log_p_x = np.log(p_x_grid)
    log_p_y = np.log(p_y_grid)

    # Bivariate KDE setup
    xy_samples = np.vstack([x_vals, y_vals])
    kde_xy = kde(xy_samples)
    if enable_tqdm:
        pbar.update(1)

    # Extract covariance and compute GPU parameters
    covariance = kde_xy.covariance
    inv_cov = np.linalg.inv(covariance)
    det_cov = np.linalg.det(covariance)
    norm_factor = 1 / (len(x_vals) * (2 * np.pi) * np.sqrt(det_cov))

    # Transfer data to GPU
    d_x_vals = cuda.to_device(x_vals.astype(np.float64))
    d_y_vals = cuda.to_device(y_vals.astype(np.float64))
    d_x_grid = cuda.to_device(x_grid.astype(np.float64))
    d_y_grid = cuda.to_device(y_grid.astype(np.float64))
    d_inv_cov = cuda.to_device(inv_cov.astype(np.float64))
    d_norm_factor = cuda.to_device(np.array([norm_factor], dtype=np.float64))
    d_eps = cuda.to_device(np.array([eps], dtype=np.float64))
    d_p_xy = cuda.device_array((gridsize, gridsize), dtype=np.float64)

    # Define 2D KDE kernel
    @cuda.jit
    def kde_2d_kernel(x_grid, y_grid, x_vals, y_vals, inv_cov, norm_factor, eps, p_xy):
        # Get grid indices
        i, j = cuda.grid(2)
        if i >= x_grid.shape[0] or j >= y_grid.shape[0]:
            return

        # Initialize sum for this grid point
        p_sum = 0.0
        n_samples = x_vals.shape[0]
        x_i = x_grid[i]
        y_j = y_grid[j]

        # Compute KDE contribution from each data point
        for k in range(n_samples):
            dx = x_i - x_vals[k]
            dy = y_j - y_vals[k]
            # Compute (x - x_k)^T * inv_cov * (x - x_k)
            exponent = -0.5 * (
                inv_cov[0, 0] * dx * dx +
                inv_cov[0, 1] * dx * dy +
                inv_cov[1, 0] * dy * dx +
                inv_cov[1, 1] * dy * dy
            )
            p_sum += math.exp(exponent)

        # Normalize and store result
        p_xy[i, j] = max(p_sum * norm_factor[0], eps[0])

    # Launch KDE kernel
    block_dim = (16, 16)
    grid_dim = ((gridsize + block_dim[0] - 1) // block_dim[0],
                (gridsize + block_dim[1] - 1) // block_dim[1])
    kde_2d_kernel[grid_dim, block_dim](d_x_grid, d_y_grid, d_x_vals, d_y_vals,
                                       d_inv_cov, d_norm_factor, d_eps, d_p_xy)

    # Compute log(p_xy) on GPU
    d_log_p_xy = cuda.device_array((gridsize, gridsize), dtype=np.float64)
    
    @cuda.jit
    def log_kernel(d_array, d_log_array):
        i, j = cuda.grid(2)
        if i < d_array.shape[0] and j < d_array.shape[1]:
            d_log_array[i, j] = math.log(d_array[i, j])
    
    log_kernel[grid_dim, block_dim](d_p_xy, d_log_p_xy)

    # Transfer 1D arrays to GPU
    d_log_p_x = cuda.to_device(log_p_x.astype(np.float64))
    d_log_p_y = cuda.to_device(log_p_y.astype(np.float64))

    # Define and launch MI kernel (unchanged)
    @cuda.jit
    def compute_mi_kernel(p_xy, log_p_xy, log_p_x, log_p_y, partial_sums):
        tx = cuda.threadIdx.x
        ty = cuda.threadIdx.y
        bx = cuda.blockIdx.x
        by = cuda.blockIdx.y
        block_size_x = cuda.blockDim.x
        block_size_y = cuda.blockDim.y
        i = bx * block_size_x + tx
        j = by * block_size_y + ty
        shared = cuda.shared.array(shape=(256,), dtype=np.float64)
        shared_idx = tx + ty * block_size_x
        if i < p_xy.shape[0] and j < p_xy.shape[1]:
            integrand = p_xy[i, j] * (log_p_xy[i, j] - log_p_x[i] - log_p_y[j])
        else:
            integrand = 0.0
        shared[shared_idx] = integrand
        cuda.syncthreads()
        stride = (block_size_x * block_size_y) // 2
        while stride > 0:
            if shared_idx < stride and shared_idx + stride < block_size_x * block_size_y:
                shared[shared_idx] += shared[shared_idx + stride]
            cuda.syncthreads()
            stride //= 2
        if tx == 0 and ty == 0:
            partial_sums[bx, by] = shared[0]

    d_partial_sums = cuda.device_array(grid_dim, dtype=np.float64)
    compute_mi_kernel[grid_dim, block_dim](d_p_xy, d_log_p_xy, d_log_p_x, d_log_p_y, d_partial_sums)

    # Compute result
    partial_sums_host = d_partial_sums.copy_to_host()
    mi = np.sum(partial_sums_host) * dx * dy
    if enable_tqdm:
        pbar.close()
    return mi

def H_discrete(df, col):
    """
    Entropy H(X) for a *discrete* variable X=col.
    """
    p_x = df[col].value_counts(normalize=True)
    return -np.sum(p_x * np.log2(p_x + 1e-12))  # small epsilon to avoid log(0)

def MI_discrete_discrete(df, col, target_col):
    if col == target_col:
        return H_discrete(df, col)
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
