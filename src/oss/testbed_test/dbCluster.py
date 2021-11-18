import numpy as np
#import pandas as pd
import math
from sklearn.cluster import DBSCAN
from sklearn import metrics
import matplotlib.pyplot as plt

# Need to call Pol's code to get lidar data, but waiting to see if Jack wants
# to handle that control with lidar data instead
# meanwhile csv files for distance and angle have been copied into this branch
# in testbed_test

# Plotting function but technically you don't need it
# def plotObject(labels, X, sample_cores, min_obj_pts, max_obj_pts):
#
#     objXY = [0,0]
#
#     colours = ['red','blue','green','yellow','cyan','magenta','orange','aqua','pink']
#
#     # Black removed and is used for noise instead.
#     unique_labels = set(labels)
#     for k, col in zip(unique_labels, colours):
#         if k == -1:
#             # Black used for noise.
#             col = [0, 0, 0, 1]
#
#         class_member_mask = (labels == k)
#
#         xy = X[class_member_mask & sample_cores]
#         #print(xy)
#         #print(col)
#
#         # Identify object and get average vector
#         if (len(xy) >= min_obj_pts and len(xy) < max_obj_pts):
#             objXY = sum(xy) / len(xy)
#             return objXY
#
#         plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=(col),
#                  markeredgecolor=(col), markersize=3)
#
#         xy_noise = X[class_member_mask & ~sample_cores]
#         plt.plot(xy_noise[:, 0], xy_noise[:, 1], 'o', markerfacecolor=(col),
#                  markeredgecolor=(col), markersize=3)
#
#     # # # Comment out if display is unwanted # # #
#     plt.grid()
#     plt.show()
#
#     return objXY

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

def findObject(distance_file, angle_file):

    # Call csv file parser
    distance, alpha = parseDataFiles(distance_file, angle_file)

    alpha = (np.linspace(-135,135,811)*np.pi/180.0).tolist()
    x = [distance[i] * math.cos(alpha[i]) for i in range(0, len(distance))]
    y = [distance[i] * math.sin(alpha[i]) for i in range(0, len(distance))]
    X_list = [[x[i], y[i]] for i in range(len(distance))]

    # Make X into an array
    X = np.array(X_list)

    # minimum data points that the object takes up at the maximum distance
    min_obj_pts = 9
    max_obj_pts = 30

    # Compute DBSCAN
    db = DBSCAN(eps=0.3, min_samples=min_obj_pts)

    # Fit model
    model = db.fit(X)
    labels = model.labels_

    # Identify the points which make up core points
    sample_cores = np.zeros_like(labels, dtype=bool)
    sample_cores[db.core_sample_indices_] = True

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    objXY = [0,0]

    colours = ['red','blue','green','yellow','cyan','magenta','orange','aqua','pink']

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    for k, col in zip(unique_labels, colours):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = X[class_member_mask & sample_cores]

        # Identify object and get average vector
        if (len(xy) >= min_obj_pts and len(xy) < max_obj_pts):
            objXY = sum(xy) / len(xy)
            return objXY

    # Display object location
    # objXY = plotObject(labels, X, sample_cores, min_obj_pts, max_obj_pts)
    # return objXY
    return [0,0]

# function call by Jack
[objX, objY] = findObject('distance_obstacle_9.csv', 'angle_obstacle_9.csv')
print(objX)
print(objY)
