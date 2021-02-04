# This is the main file for the gopigo test
# We want to go forward with the camera and lidar saving data
# We want to save their data to files
# Then once the test is over, we will read the files in a separate Python script and do some cool stuff with it

from lidar import Lidar
from video import Video
import time
# Data we want to store:
# Camera: as bytes
# LIDAR: raw data
# LIDAR: for the object determination

# Initialize components
# lidar = Lidar()
video = Video()

# Initialize file writing
video_file = open("/home/xilinx/tracsat/src/oss/testbed_test/video_out.txt", "w")
raw_file = open("/home/xilinx/tracsat/src/oss/testbed_test/lidar_raw_data.txt", "w")
obj_file = open("/home/xilinx/tracsat/src/oss/testbed_test/obj_data.txt", "w")

# End time
t_end = time.time() + 60 * 5 # Runs for 1 minute

# Create arrays here
frames = []
raws = []
objs = []

# Loop
while time.time() < t_end:
    try:
        print("Running")
        # Get video frame
        frame = video.getFrame()
        # frame_string = ",".join(frame)

        # Write video frame to file
        # frames.append(frame_string)

        # Get LIDAR data
        # raw_data = lidar.get_scan()
        # obj_data = lidar.get_obs_data()

        # raw_data_string = ",".join([str(i) for i in raw_data])
        # obj_data_string = ",".join([str(i) for i in obj_data])

        # Write LIDAR data
        # raws.append(raw_data_string)
        # objs.append(obj_data_string)

    except KeyboardInterrupt:
        break

# Write to files
print("File writing")
for frame in frames:
    video_file.write(frame + "\n")
for raw in raws:
    raw_file.write(raw + "\n")
for obj in objs:
    obj_file.write(obj + "\n")

# Close files
print("Closing all files")
video_file.close()
raw_file.close()
obj_file.close()
