# -*- coding: utf-8 -*-
"""Clustering.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/144rZ_oMm8zwldnzUCFfIH58PBCkf-GkP

<br>
<font>
<!-- <img src="https://cdn.freebiesupply.com/logos/large/2x/sharif-logo-png-transparent.png" alt="SUT logo" width=300 height=300 align=left class="saturate"> -->
<div dir=ltr align=center>
<img src="https://cdn.freebiesupply.com/logos/large/2x/sharif-logo-png-transparent.png" width=200 height=200>
<br>
<font color=0F5298 size=7>
Machine Learning <br>
<font color=2565AE size=5>
Electrical Engineering Department <br>
Spring 2024<br>
<font color=3C99D size=5>
Practical Assignment 4 <br>
<font color=696880 size=4>
<!-- <br> -->


____

# Personal Data
"""

student_number = '400100746'
first_name = 'Hossein'
last_name = 'Anjidani'

"""# Introduction

In this assignment, we will be performing clustering on Spotify songs.

# Data Preprocessing

In the next cell, import the libraries you'll need.
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

"""In the `spotify.csv` file, load the data. Exclude unrelated features and retain only the track name and the features you believe are relevant."""

folder_path = '/content/drive/MyDrive/UNI/Sem 6/ML/CHW4/Q2'
# Read a CSV file from Drive
file_path = os.path.join(folder_path, 'spotify.csv')
data = pd.read_csv(file_path)

# Display the first few rows of the dataframe
data.head()

"""In this cell, you should implement a standard scalar function from scratch and applying it to your data. Explian importance behind using a standard scalar and the potential complications that could arise in clustering if it's not employed. (you can't use `sklearn.preprocessing.StandardScaler` but you are free to use `sklearn.preprocessing.LabelEncoder`)

**Answer:**
Importance of Standardizing Data
1. Equal Weight: Standardization ensures that each feature contributes equally to the distance measurements used in clustering algorithms. This prevents features with larger ranges from dominating the results.
2. Convergence: Many clustering algorithms, such as K-Means, converge faster when the data is standardized. Non-standardized data can lead to poor performance and longer training times.
3. Interpretability: Standardized data makes it easier to interpret the distances and the results of the clustering, as all features are on the same scale.

Complications Without Standardization
1. Dominant Features: Features with larger scales can dominate the distance metric, making the clustering algorithm biased towards these features.
2. Distorted Clusters: The shape and size of the clusters can be distorted if the features are on different scales.
3. Inefficient Algorithms: The efficiency and effectiveness of algorithms can be severely impacted, leading to suboptimal clustering results.

Implementing Standard Scaler
Let's implement a standard scaler from scratch and apply it to the spotify.csv dataset.

Steps:
1. Load the Data: Load the dataset from the CSV file.
2. Implement Standard Scaler: Write a function to standardize the data.
3. Apply the Scaler: Apply the scaler to the dataset.
"""

class StandardScalerFromScratch:
    def __init__(self):
        self.means = None
        self.stds = None

    def fit(self, X):
        # Calculate the mean and standard deviation for each feature
        self.means = X.mean(axis=0)
        self.stds = X.std(axis=0)

    def transform(self, X):
        # Standardize the data using the mean and std
        return (X - self.means) / self.stds

    def fit_transform(self, X):
        # Fit to the data and then transform it
        self.fit(X)
        return self.transform(X)

# Select numerical columns for standardization
numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns
numerical_data = data[numerical_columns]

# Create an instance of the scaler and apply it to the numerical data
scaler = StandardScalerFromScratch()
standardized_data = scaler.fit_transform(numerical_data)

# Convert the standardized data back to a DataFrame
standardized_df = pd.DataFrame(standardized_data, columns=numerical_columns)

# Display the first few rows of the standardized data
standardized_df.head()

"""# Dimensionality Reduction

One method for dimensionality reduction is Principal Component Analysis (PCA). Use its implementation from the `sklearn` library to reduce the dimensions of your data. Then, by using an appropriate cut-off for the `_explained_variance_ratio_` in the PCA algorithm, determine the number of principal components to retain.

**Answer:**
Principal Component Analysis (PCA) is a popular technique for reducing the dimensionality of datasets while preserving as much variability as possible. This is achieved by transforming the original variables into a new set of variables, the principal components, which are orthogonal and capture the maximum variance in the data.

Steps:
1. Standardize the Data: Ensure that the data is standardized.
2. Apply PCA: Use PCA to reduce the dimensions of the data.
3. Determine the Number of Components: Use the explained variance ratio to determine the number of principal components to retain.

Let's proceed with the implementation using the spotify.csv dataset.
"""

# Apply PCA
pca = PCA()
pca.fit(standardized_df)

# Calculate explained variance ratio
explained_variance_ratio = pca.explained_variance_ratio_

# Plot the explained variance ratio to determine the number of components
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio.cumsum(), marker='o', linestyle='--')
plt.xlabel('Number of Principal Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Explained Variance by Principal Components')
plt.grid(True)
plt.show()

# Determine the number of components to retain (e.g., 95% explained variance)
explained_variance_cutoff = 0.95
cumulative_variance = explained_variance_ratio.cumsum()
num_components = next(i for i, total_variance in enumerate(cumulative_variance) if total_variance >= explained_variance_cutoff) + 1

print(f"Number of principal components to retain for {explained_variance_cutoff * 100}% explained variance: {num_components}")

# Transform the data using the determined number of components
pca = PCA(n_components=num_components)
reduced_data = pca.fit_transform(standardized_data)

# Display the shape of the reduced data
print(f"Shape of the reduced data: {reduced_data.shape}")

"""**Summary:**
* Standardization: The data was standardized to ensure that each feature
contributes equally to the PCA.
* PCA Application: PCA was applied to the standardized data.
* Explained Variance Ratio: The explained variance ratio was plotted to visually determine the number of components to retain.
* Component Selection: The number of principal components needed to retain 95% of the explained variance was determined.
* Transformation: The data was transformed using the selected number of components.

This process reduces the dimensionality of the dataset while retaining the majority of the variability, making subsequent analyses, such as clustering, more efficient and effective.

# Clustering

Implement K-means for clustering from scratch.
**Answer**
Implementing the K-means clustering algorithm from scratch involves several steps:

1. Initialize Centroids: Randomly initialize k centroids.
2. Assign Clusters: Assign each data point to the nearest centroid.
3. Update Centroids: Recompute the centroids as the mean of all data points assigned to each cluster.
4. Repeat: Repeat steps 2 and 3 until convergence (i.e., the centroids no longer change significantly).
Implementing K-means from Scratch

Let's proceed with the implementation using the spotify.csv dataset.

Steps:
1. Load the Data: Load and preprocess the data (standardization and PCA as previously done).
2. Implement K-means: Write a function to perform K-means clustering from scratch.
3. Apply K-means: Apply the K-means function to the reduced dataset.

First, we'll define the necessary functions for the K-means algorithm.
"""

class KMeansFromScratch:
    def __init__(self, n_clusters, max_iter=300, tol=1e-4):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X):
        n_samples, n_features = X.shape

        # Initialize centroids randomly from the data points
        np.random.seed(42)
        initial_indices = np.random.permutation(n_samples)[:self.n_clusters]
        self.centroids = X[initial_indices]

        for i in range(self.max_iter):
            # Assign clusters
            self.labels = self._assign_clusters(X)

            # Compute new centroids
            new_centroids = np.array([X[self.labels == j].mean(axis=0) for j in range(self.n_clusters)])

            # Check for convergence
            if np.all(np.abs(new_centroids - self.centroids) < self.tol):
                break

            self.centroids = new_centroids

    def _assign_clusters(self, X):
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)

    def predict(self, X):
        return self._assign_clusters(X)

# Create an instance of KMeansFromScratch and fit it to the reduced data
kmeans = KMeansFromScratch(n_clusters=3)
kmeans.fit(reduced_data)

# Get the cluster labels
labels = kmeans.predict(reduced_data)

# Add the cluster labels to the DataFrame
data['Cluster'] = labels

# Display the first few rows of the dataset with the cluster labels
data.head()

plt.figure(figsize=(10, 6))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=50)
plt.scatter(kmeans.centroids[:, 0], kmeans.centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('K-means Clustering')
plt.legend()
plt.grid(True)
plt.show()

"""Using the function you've created to execute the K-means algorithm eight times on your data, with the number of clusters ranging from 2 to 9. For each run, display the genre of each cluster using the first two principal components in a plot."""

genres = data['genre'] if 'genre' in data.columns else None
for n_clusters in range(2, 10):
    kmeans = KMeansFromScratch(n_clusters=n_clusters)
    kmeans.fit(reduced_data)
    labels = kmeans.predict(reduced_data)

    # Plot the results
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=50)
    plt.scatter(kmeans.centroids[:, 0], kmeans.centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title(f'K-means Clustering with {n_clusters} Clusters')
    plt.legend()
    plt.grid(True)

    # Annotate with genres if available
    if genres is not None:
        for i in range(n_clusters):
            # Find the indices of points in this cluster
            indices = np.where(labels == i)[0]
            # Find the most common genre in this cluster
            common_genre = genres.iloc[indices].mode()[0]
            # Place the genre label near the cluster centroid
            centroid = kmeans.centroids[i]
            plt.text(centroid[0], centroid[1], common_genre, fontsize=12, ha='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    plt.show()

"""The Silhouette score and the Within-Cluster Sum of Squares (WSS) score are two metrics used to assess the quality of your clustering. You can find more information about these two methods [here](https://medium.com/analytics-vidhya/how-to-determine-the-optimal-k-for-k-means-708505d204eb). Plot the Silhouette score and the WSS score for varying numbers of clusters, and use these plots to determine the optimal number of clusters (k)."""

def calculate_wss(X, labels, centroids):
    wss = 0
    for i, centroid in enumerate(centroids):
        cluster_points = X[labels == i]
        wss += np.sum((cluster_points - centroid) ** 2)
    return wss

silhouette_scores = []
wss_scores = []
k_values = range(2, 10)

for k in k_values:
    kmeans = KMeansFromScratch(n_clusters=k)
    kmeans.fit(reduced_data)
    labels = kmeans.predict(reduced_data)

    # Calculate Silhouette Score
    silhouette_avg = silhouette_score(reduced_data, labels)
    silhouette_scores.append(silhouette_avg)

    # Calculate WSS
    wss = calculate_wss(reduced_data, labels, kmeans.centroids)
    wss_scores.append(wss)

# Plot Silhouette Scores
plt.figure(figsize=(12, 6))
plt.plot(k_values, silhouette_scores, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score for Varying Number of Clusters')
plt.grid(True)
plt.show()

# Plot WSS Scores
plt.figure(figsize=(12, 6))
plt.plot(k_values, wss_scores, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Within-Cluster Sum of Squares (WSS)')
plt.title('WSS for Varying Number of Clusters')
plt.grid(True)
plt.show()

"""# Checking Output

To see how good was our clustering we will use a sample check and t-SNE method.

first randomly select two song from every cluster and see how close these two songs are.
"""

n_clusters = 3  # For example, choose 3 clusters
kmeans = KMeansFromScratch(n_clusters=n_clusters)
kmeans.fit(reduced_data)
labels = kmeans.predict(reduced_data)

# Add cluster labels to the original data
data['Cluster'] = labels

# Randomly select two songs from each cluster and calculate the distance
def random_sample_distance(data, labels, cluster):
    cluster_data = data[labels == cluster]
    if len(cluster_data) < 2:
        return None, None, None
    sample = cluster_data.sample(2, random_state=42)
    song1 = sample.iloc[0]
    song2 = sample.iloc[1]
    distance = np.linalg.norm(song1 - song2)
    return song1, song2, distance

# Calculate distances for each cluster
distances = {}
for cluster in range(n_clusters):
    song1, song2, distance = random_sample_distance(pd.DataFrame(reduced_data), labels, cluster)
    if song1 is not None and song2 is not None:
        distances[cluster] = distance
        print(f"Cluster {cluster}: Distance between selected songs: {distance}")

# Apply t-SNE for visualization
tsne = TSNE(n_components=2, random_state=42)
tsne_data = tsne.fit_transform(standardized_data)

# Plot the t-SNE results
plt.figure(figsize=(10, 6))
scatter = plt.scatter(tsne_data[:, 0], tsne_data[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=50)
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.title('t-SNE Visualization of Clusters')
plt.legend(handles=scatter.legend_elements()[0], labels=set(labels))
plt.grid(True)
plt.show()

"""Using t-SNE reduce dimension of data pointe to 2D and plot it to check how good datapoints are clustered (implementing this part is optional and have extra points)"""

# Apply K-means clustering
n_clusters = 3  # For example, choose 3 clusters
kmeans = KMeansFromScratch(n_clusters=n_clusters)
kmeans.fit(reduced_data)
labels = kmeans.predict(reduced_data)

# Add cluster labels to the original data
data['Cluster'] = labels

# Randomly select two songs from each cluster and calculate the distance
def random_sample_distance(data, labels, cluster):
    cluster_data = data[labels == cluster]
    if len(cluster_data) < 2:
        return None, None, None
    sample = cluster_data.sample(2, random_state=42)
    song1 = sample.iloc[0]
    song2 = sample.iloc[1]
    distance = np.linalg.norm(song1 - song2)
    return song1, song2, distance

# Calculate distances for each cluster
distances = {}
for cluster in range(n_clusters):
    song1, song2, distance = random_sample_distance(pd.DataFrame(reduced_data), labels, cluster)
    if song1 is not None and song2 is not None:
        distances[cluster] = distance
        print(f"Cluster {cluster}: Distance between selected songs: {distance}")

# Apply t-SNE for visualization
tsne = TSNE(n_components=2, random_state=42)
tsne_data = tsne.fit_transform(standardized_data)

# Plot the t-SNE results
plt.figure(figsize=(10, 6))
scatter = plt.scatter(tsne_data[:, 0], tsne_data[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=50)
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.title('t-SNE Visualization of Clusters')
plt.legend(handles=scatter.legend_elements()[0], labels=set(labels))
plt.grid(True)
plt.show()