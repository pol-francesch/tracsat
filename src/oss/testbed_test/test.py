# This is the main file for the gopigo test
# We want to go forward with the camera and lidar saving data
# We want to save their data to files
# Then once the test is over, we will read the files in a separate Python script and do some cool stuff with it

from lidar import Lidar
from video import Video
import time
from tqdm import tqdm

# Data we want to store:
# Camera: as bytes
# LIDAR: raw data
# LIDAR: for the object determination

# Initialize components
lidar = Lidar()
video = Video()

# Initialize settings
compression = False
color = "8bit"
dim = (640,480)
addtl = "_no_8bit"

video.setColor(color)
video.setDim(dim)

# Initialize file writing
source = input('Type 0 for PYNQ. Type 1 for Pol\'s PC: ')
path_xilinx = "/home/xilinx/tracsat/src/oss/testbed_test/data/"
path_pc = "/home/polfr/Documents/tracsat/src/oss/testbed_test/data/"

if source == '0':
    path = path_xilinx
elif source == '1':
    path = path_pc
else:
    print('That is not an option!')
    exit(0)

video_file = open(path + "video_out" + addtl + ".txt", "w")
raw_file = open(path + "lidar_raw" + addtl + ".txt", "w")
obj_file = open(path + "obj_data" + addtl + ".txt", "w")

_=input("write")

# End time
t_end = time.time() + 10 # Runs for 30s

# Create arrays here
frames = []
raws = []
objs = []

# Loop
while time.time() < t_end:
    try:
        print("Running")
        # Get video frame
        if compression:
            frame = video.getFrameBitCompressed()
        else:
            frame = video.getFrameBitsFast()

        # Write video frame to file
        frames.append(frame)

        # Get LIDAR data
        raw_data = lidar.get_scan()
        obj_data = lidar.get_obs_data()

        # Write LIDAR data
        raws.append(raw_data)
        objs.append(obj_data)

    except KeyboardInterrupt:
        break

# Write to files
print("File writing - video")

for i in tqdm(range(0,len(frames))):
    frame = frames[i]

    # Have to reformat array so it will be able to be written to file
    frame_string = [str(1 if bit else 0) for bit in frame]
    frame_string = ",".join(frame_string)

    # Write to file
    video_file.write(frame_string + "\n")

print("File writing - lidar")
for raw in raws:
    raw_string = ",".join([str(i) for i in raw])
    raw_file.write(raw_string + "\n")

for obj in objs:
    obj_string = ",".join([str(i) for i in obj])
    obj_file.write(obj_string + "\n")

# Close files
print("Closing all files")
video_file.close()
raw_file.close()
obj_file.close()
