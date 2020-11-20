import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from cv2 import cv2

# This file is here to read the output data, and create plots or video

# TODO: Read data from files
video_file = open("/home/polfr/Documents/tracsat/src/oss/testbed_test/video_out.txt", "r")
raw_file = open("/home/polfr/Documents/tracsat/src/oss/testbed_test/lidar_raw_data.txt", "r")
obj_file = open("/home/polfr/Documents/tracsat/src/oss/testbed_test/obj_data.txt", "r")

# TODO: Show video from data
cap = cv2.VideoCapture(0)

def show_video():
    lines = video_file.readlines()

    cv2.namedWindow("TracSat", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("TracSat", 640*2, 480*2)

    for line in lines:
        # Convert to desired data type
        data = [np.uint8(int(byte, 2)) for byte in line.split(',')]
        arr = np.array(data)
        arr2d = np.reshape(arr, (-1, 640))

        # Show in video
        cv2.imshow('TracSat', arr2d)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# TODO: Show animation of lidar from data
fig = plt.figure(figsize=(15,10))
fig.canvas.set_window_title('TiM561 LIDAR Monitor')
lidar_polar = plt.subplot(polar=True)

def animate(i):
    # Get data
    data_string = raw_file.readline()
    data = [float(idx) for idx in data_string.split(',')]

    # Create theta
    theta = np.linspace(45, 315, len(data))
    theta = (np.pi/180.0) * theta                       # Convert to radians
    theta = [float(x) for x in theta]

    # Plot
    lidar_polar.clear()
    lidar_polar.set_thetamax(315)
    lidar_polar.set_thetamin(45)
    plt.fill_between(theta, data, alpha=0.2)
    lidar_polar.scatter(theta, data, s=1, c=data)

def show_raw_data():
    ani = animation.FuncAnimation(fig, animate)
    plt.show()

# TODO: Show plot of obs information that PYNQ derived from data
def show_obs():
    lines = obj_file.readlines()

    # Variables
    distance = np.zeros(len(lines))
    width = np.zeros(len(lines))
    angle = np.zeros(len(lines))
    time = np.arange(0, 60, 60/len(lines))
    i = 0

    # Break down data
    for line in lines:
        data = [float(point) for point in line.split(',')]
        distance[i] = data[0]
        width[i] = data[1]
        angle[i] = data[2]
        i = i + 1
    
    # Plot
    fig, ax = plt.subplots(3)
    fig.tight_layout(pad=3.0)

    ax[0].plot(time, distance)
    ax[0].set_title('Distance over time')
    ax[0].set_ylabel('Distance (m)')

    ax[1].plot(time, width)
    ax[1].set_title('Width over time')
    ax[1].set_ylabel('Width (m)')

    ax[2].plot(time, angle)
    ax[2].set_title('Angle over time')
    ax[2].set_ylabel("Angle (deg)")

    plt.show()
    

# TODO: Main control
if __name__ == '__main__':
    # Run code for video
    # show_video()

    # Run code for LIDAR raw data
    show_raw_data()

    # Run code for LIDAR object data
    # show_obs()