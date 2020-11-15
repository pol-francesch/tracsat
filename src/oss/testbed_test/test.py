# This is the main file for the gopigo test
# We want to go forward with the camera and lidar saving data
# We want to save their data to files
# Then once the test is over, we will read the files in a separate Python script and do some cool stuff with it

from classes.lidar import Lidar
from classes.video import Video

# Data we want to store:
# Camera: as bytes
# LIDAR: raw data
# LIDAR: for the object determination

# Initialize components
lidar = Lidar()
video = Video()

# Initialize file writing
video_file = open("video_out.txt", "w")
raw_file = open("lidar_raw_data.txt", "w")
obj_file = open("obj_data.txt", "w")

# Loop
while True:
    try: 
        # Get video frame
        frame = video.getFrameBits()

        # TODO: Write video frame to file

        # Get LIDAR data
        raw_data = lidar.get_scan()
        obj_data = lidar.get_obs_data()

        # TODO: Write LIDAR data

    except KeyboardInterrupt:
        break

# Close files
print("Closing all files")
video_file.close()
raw_file.close()
obj_file.close()