# Import pysicktim library as "lidar"
import pysicktim as lidar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Define constants
lidar.scan()                                        # Run once to get constants
min_angle = int(lidar.scan.dist_start_ang)
angle_res = float(lidar.scan.dist_angle_res)
points = int(lidar.scan.dist_data_amnt)
max_angle = (angle_res * points) - min_angle
max_distance = 5
min_distance = 0.002

theta = np.linspace(min_angle, max_angle, points)
theta = (np.pi/180.0) * theta                       # Convert to radians
theta = [float(x) for x in theta]

# FOV parameters
max_distance_fov = 2.4384                           # m, (= 8ft)
max_width_fov = 0.6096                              # m, (= 2ft)
min_width_fov = 0.3048                              # m, (= 1ft)


while(True):
    lidar.scan()
    distances = lidar.scan.distances

    # Check if any items in list are larger than max_distance
    if max(distances) > max_distance or min(distances) < min_distance:
        # Iterate through list and set any integers larger than max_distance to max_distance
        for i in range(len(distances)):
            if distances[i] > max_distance:		    # if larger than max_distance
                distances[i] = max_distance	        # set equal to max_distance

            if distances[i] <= min_distance:		# if larger than max_distance
                distances[i] = max_distance	        # set equal to max_distance
    
    # Get items that are within the FOV

