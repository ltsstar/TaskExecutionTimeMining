
from information_bottleneck import *

def divide_and_conquer_ib(
        transformed_event_log,
        categorical_columns,
        continuous_columns,
        target_column,
        n_clusters=32,
        n_bins_y=512,
        n_bins_x=128
):
    max_mi = 0.0
    best_cluster = None
    # start with categorical because it reduces min_mi and is faster
    for categorical_column in categorical_columns:
        print(f"Clustering {categorical_column}")
        cluster_assignments, cluster_ranges, development = \
             information_bottleneck_clustering(transformed_event_log[categorical_column],
                                               transformed_event_log[target_column].to_numpy(),
                                               x_is_discrete=True,
                                               n_clusters=n_clusters,
                                               n_bins_y=n_bins_y,
                                               min_mi=max_mi)
        current_mi = development[-1][1]
        if current_mi > max_mi:
            max_mi = current_mi
            best_cluster = categorical_column, cluster_assignments, cluster_ranges, development
            print(f"New best MI: {max_mi} for column {categorical_column}")

    for continuous_column in continuous_columns:
        print(f"Clustering {continuous_column}")
        cluster_assignments, cluster_ranges, development = \
             information_bottleneck_clustering(transformed_event_log[continuous_column].to_numpy(),
                                               transformed_event_log[target_column].to_numpy(),
                                               n_clusters=n_clusters,
                                               n_bins_x=n_bins_x,
                                               n_bins_y=n_bins_y,
                                               min_mi=max_mi)
        current_mi = development[-1][1]
        if current_mi > max_mi:
            max_mi = current_mi
            best_cluster = continuous_column, cluster_assignments, cluster_ranges, development
            print(f"New best MI: {max_mi} for column {continuous_column}")

    return best_cluster