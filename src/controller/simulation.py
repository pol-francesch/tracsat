import math
import time
import numpy as np

# Simulate IMU data to test controller

def sim_sensor_data(thrusters,t0,t1,euler1,ang_vel):

    # Euler angle
    #t = time.time()
    dt = t1 - t0
    mass = 10    # kg??
    r = 0.2        # meters
    force = 0.1  # mN
    torque = r * (thrusters[4] - thrusters[5]) * force
    I = 0.5 * mass * r ** 2  # moment of inertia -> assume solid cylinder
    ang_accel = torque / I
    #
    ang_vel = ang_vel + ang_accel * dt
    euler1 = euler1 + (ang_vel * dt) + (0.5 * ang_accel * dt ** 2)

    # acceleration is instantaneous --> take components of force
    accX = (thrusters[0] * force / mass) - (thrusters[1] * force / mass)
    accY = (thrusters[2] * force / mass) - (thrusters[3] * force / mass)

    return accX, accY, euler1, ang_vel

# def calcOvershoot(accX, accY, euler):
#     # convert body acceleraition to inertial acceleration to find position overshoot
#     t1 = time.time()
#
#     accXI = accX * math.cos(euler1) - accY * math.sin(euler1)
#     accYI = accX * math.sin(euler1) + accY * math.cos(euler1)
#
#     newVx = lastVx + accXI * (t1-last_t)
#     newVy = lastVy + accYI * (t1-last_t)
#
#     newX = lastX + lastVx * (t1-last_t) + .5 * accXI * (t1-last_t) ** 2
#     newY = lastY + lastVy * (t1-last_t) + .5 * accYI * (t1-last_t) ** 2
#
#     lastX = newX
#     lastY = newY
#     lastVx = newVx
#     laxtVy = newVy
#     totalX += newX - lastX
#     totalY += newY - lastY
#
#     last_t = t1
#
#     positionDiff =
#
#     overshoot.append()
#
#     return


# def runSim(thrusters):
#     #env = simpy.Environment()
#
#     currentAcceleration, currentEuler = sim_sensor_data(thrusters)
#     overshoot.append(currentEuler[0])
#
#     return [accX = currentAcceleration[0], accY = currentAcceleration[1], euler1 = currentEuler[0]]

    # some plotting? i think the controller code should be doing this
