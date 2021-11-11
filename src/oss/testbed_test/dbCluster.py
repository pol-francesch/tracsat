import numpy as np
#import pandas as pd
import math
from sklearn.cluster import DBSCAN
from sklearn import metrics
import matplotlib.pyplot as plt

def parseDataFiles(distance_file, angle_file):
    with open(distance_file, 'r') as d:
        distance = d.readlines()
    with open(angle_file, 'r') as a:
        alpha = a.readlines()

    for i in range(0, len(distance)):
        distance[i] = float(distance[i])
    for i in range(0, len(alpha)):
        alpha[i] = float(alpha[i])

    return distance, alpha

#distance, alpha = parseDataFiles('data/distance_closetowall_15.csv', 'data/angle_closetowall_15.csv')
distance, alpha = parseDataFiles('data_ellen/distance_obstacle_18.csv', 'data_ellen/angle_obstacle_18.csv')
alpha = (np.linspace(-135,135,811)*np.pi/180.0).tolist()
print(alpha)
x = [distance[i] * math.cos(alpha[i]) for i in range(0, len(distance))]
y = [distance[i] * math.sin(alpha[i]) for i in range(0, len(distance))]
X_list = [[x[i], y[i]] for i in range(len(distance))]

# Make X into an array
X = np.array(X_list)

# Compute DBSCAN
db = DBSCAN(eps=0.3, min_samples=7)

# Fit model
model = db.fit(X)
labels = model.labels_

# Identify the points which make up core points
sample_cores = np.zeros_like(labels, dtype=bool)
sample_cores[db.core_sample_indices_] = True

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

colours = ['red','blue','green','yellow','cyan','magenta','orange','aqua','pink']

# Black removed and is used for noise instead.
unique_labels = set(labels)
for k, col in zip(unique_labels, colours):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = X[class_member_mask & sample_cores]
    print(xy)
    print(col)
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=(col),
             markeredgecolor=(col), markersize=3)

    xy = X[class_member_mask & ~sample_cores]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=(col),
             markeredgecolor=(col), markersize=3)

plt.grid()
plt.show()
