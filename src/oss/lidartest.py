# Import pysicktim library as "lidar"
import lidar_lib as lidar
# import pysicktim as lidar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Setting up video stage
fig = plt.figure()
fig.canvas.set_window_title('TiM561 LIDAR Monitor')
lidar_polar = plt.subplot(polar=True)

# Define constants
lidar.scan()                                        # Run once to get constants
min_angle = int(lidar.scan.dist_start_ang)
angle_res = float(lidar.scan.dist_angle_res)
points = int(lidar.scan.dist_data_amnt)
max_angle = (angle_res * points) - min_angle
max_distance = 5
min_distance = 0.002

# FOV parameters
max_distance_fov = 2.4384                           # m, (= 8ft)
max_width_fov = 0.6096                              # m, (= 2ft)
min_width_fov = 0.3048                              # m, (= 1ft)

# Counter to screen isn't over loaded with prints
count = 0

def animate(i):
    # Getting our count variable
    global count

    lidar.scan()
    distances = lidar.scan.distances

    theta = np.linspace(min_angle, max_angle, points)
    theta = (np.pi/180.0) * theta                       # Convert to radians
    theta = [float(x) for x in theta]

    # Check if any items in list are larger than max_distance
    if max(distances) > max_distance or min(distances) < min_distance:
        # Iterate through list and set any integers larger than max_distance to max_distance
        for i in range(len(distances)):
            if distances[i] > max_distance:		    # if larger than max_distance
                distances[i] = max_distance	        # set equal to max_distance

            if distances[i] <= min_distance:		# if larger than max_distance
                distances[i] = max_distance	        # set equal to max_distance
    
    # Exclude stuff outside of FOV 
    distances_fov = distances[int(points/3):points - int(points/3)]
    theta_fov = theta[int(points/3):points - int(points/3)]

    obs = []
    angles = []
    for (distance, angle) in zip(distances_fov, theta_fov):
        if distance > min_distance and distance < max_distance_fov:
            obs.append(distance)
            angles.append(angle)

    if (len(obs) > 0):    
        # Get RMS distance to Obs
        rms = calc_rms(obs)

        # Get width of Obs
        angle_res_rad = np.pi/180.0 * float(angle_res)
        width = len(obs) * rms * np.tan(angle_res_rad)

        # Get angle to obstacle (where 0 deg is mid point of LiDAR)
        # Assume middle of angles is middle of object
        zero_point = theta_fov[int(len(theta_fov) / 2)]
        mid_point_obs = angles[int(len(angles)/ 2)]
        angl_to_obs = (zero_point - mid_point_obs) * 180.0 / np.pi
    else:
        rms = None
        width = None
        angl_to_obs = None

    # Print results
    if count % 10 == 0:
        print("RMS Distance to Obstacle: " + str(rms))
        print("Obstacle Width: " + str(width))
        print("Angle to Obstacle: " + str(angl_to_obs))
        print()
    count += 1

    # Plot LiDAR data
    lidar_polar.clear()
    lidar_polar.set_thetamax(45)
    lidar_polar.set_thetamin(315)
    plt.fill_between(theta, distances, alpha=0.2)
    lidar_polar.scatter(theta, distances, s=1, c=distances)     # Colored points


def calc_rms(vals):
    if len(vals) > 0:
        mean_square = 0
        for val in vals:
            mean_square = mean_square + val**2
        
        mean_square = mean_square / len(vals)
        rms = np.sqrt(mean_square)

        return rms
    
    return 0

ani = animation.FuncAnimation(fig, animate)
plt.show()