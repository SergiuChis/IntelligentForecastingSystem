import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import sqlite3
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering


def create_array_for_kmeans(current_values, voltage_values):
    arr = []
    for value in current_values:
        arr.append([value[0]])
    i = 0
    for value in voltage_values:
        arr[i].append(value[0])
        i += 1
    return arr


def kmeans_clustering(arr):
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300
    }

    sse = []
    silhouette_coefficients = []

    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(arr)
        sse.append(kmeans.inertia_)
        score = silhouette_score(arr, kmeans.labels_)
        silhouette_coefficients.append(score)

    plt.style.use("fivethirtyeight")
    plt.plot(range(2, 11), sse)
    plt.xticks(range(2, 11))
    plt.xlabel("Number of Clusters")
    plt.ylabel("SSE")
    plt.show()

    plt.plot(range(2, 11), silhouette_coefficients)
    plt.xticks(range(2, 11))
    plt.xlabel("Number of clusters")
    plt.ylabel("Silhouette Coefficient")
    plt.show()

    kl = KneeLocator(range(2, 11), sse, curve="convex", direction="decreasing")

    print("Elbow point:", kl.elbow)


if __name__ == "__main__":
    database = sqlite3.connect("Saves/SQL_grouped/data_for_training.sqlite")
    current_values = database.execute("select value from current")
    voltage_values = database.execute("select value from voltage")
    arr = create_array_for_kmeans(current_values, voltage_values)
    database.close()

    # kmeans_clustering(arr)

    print(len(arr))
    hc = AgglomerativeClustering(compute_full_tree=True)
    y_hc = hc.fit(arr)
    print(y_hc)
