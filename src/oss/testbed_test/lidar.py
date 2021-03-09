import lidar_lib as tim
import numpy as np

def calc_rms(vals):
    if len(vals) > 0:
        mean_square = 0
        for val in vals:
            mean_square = mean_square + val**2
        
        mean_square = mean_square / len(vals)
        rms = np.sqrt(mean_square)

        return rms
    
    return 0

class Lidar:
    def __init__(self, fov=3):
        # Lidar just needs to be initialized
        self.lidar = tim
        self.lidar.scan()

        # Define constants
        self.min_angle = int(self.lidar.scan.dist_start_ang)
        self.angle_res = float(self.lidar.scan.dist_angle_res)
        self.points = int(self.lidar.scan.dist_data_amnt)
        self.max_angle = (self.angle_res * self.points) - self.min_angle
        self.max_distance = 5
        self.min_distance = 0.002

        # Set fov
        self.fov = fov
        self.max_distance_fov = 1.524                           # m, (= 5ft)
        self.max_width_fov = 0.6096                              # m, (= 2ft)
        self.min_width_fov = 0.3048                              # m, (= 1ft)

        # Set angular data
        self.theta = np.linspace(self.min_angle, self.max_angle, self.points)
        self.theta = (np.pi/180.0) * self.theta                       # Convert to radians
        self.theta = [float(x) for x in self.theta]
    
    def get_scan(self):
        self.lidar.scan()
        distances = self.lidar.scan.distances

        # Check if any items in list are larger than max_distance
        if max(distances) > self.max_distance or min(distances) < self.min_distance:
            # Iterate through list and set any integers larger than max_distance to max_distance
            for i in range(len(distances)):
                if distances[i] > self.max_distance:		    # if larger than max_distance
                    distances[i] = self.max_distance	        # set equal to max_distance

                if distances[i] <= self.min_distance:		    # if larger than max_distance
                    distances[i] = self.max_distance	        # set equal to max_distance
        
        return distances
    
    def get_scan_fov(self):
        distances = self.get_scan()

        # Convert to desired FOV
        distances_fov = distances[int(self.points/self.fov):self.points - int(self.points/self.fov)]
        theta_fov = self.theta[int(self.points/self.fov):self.points - int(self.points/self.fov)]

        return distances_fov, theta_fov
    
    def get_obs_list(self):
        distances_fov, theta_fov = self.get_scan_fov()

        obs = []
        angles = []
        for (distance, angle) in zip(distances_fov, theta_fov):
            if distance > self.min_distance and distance < self.max_distance_fov:
                obs.append(distance)
                angles.append(angle)
        
        return obs, angles

    def get_obs_rms(self):
        obs,_ = self.get_obs_list()

        if len(obs) > 0:
            return calc_rms(obs)
        else:
            return None
    
    def get_obs_width(self):
        obs,_ = self.get_obs_list()

        if len(obs) > 0:
            angle_res_rad = np.pi/180.0 * float(self.angle_res)
            rms = self.get_obs_rms()

            return len(obs) * rms * np.tan(angle_res_rad)
        else:
            return None
    
    def get_obs_angle(self):
        obs, angles = self.get_obs_list()
        _, theta_fov = self.get_scan_fov()

        if len(obs) > 0:
            zero_point = theta_fov[int(len(theta_fov) / 2)]
            mid_point_obs = angles[int(len(angles)/ 2)]
            return (zero_point - mid_point_obs) * 180.0 / np.pi
        else:
            return None
    
    def get_obs_data(self):
        rms = self.get_obs_rms()
        width = self.get_obs_width()
        angle = self.get_obs_angle()

        return rms, width, angle

if __name__ == '__main__':
    lidar = Lidar(fov=3)

    data = lidar.get_obs_data()

    print(data)
