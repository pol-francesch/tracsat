from scipy.ndimage import gaussian_filter1d
import numpy as np
import math
import time
import board
import busio
import adafruit_bno055

def getWaypoints(x,y,threshold):
    xW = np.array()
    yW = np.array()

    deriv2 = np.array([])

    for i in range(0, len(x) - 2):
        #take three points and rotate about first point until first and third points are on the x-axis
        x13 = x[i + 2] - x[i]
        y13 = y[i + 2] - y[i]
        r13 = np.array([x13,y13,0])

        x12 = x[i + 1] - x[i]
        y12 = y[i + 1] - y[i]
        r12 = np.array([x12,y12,0])

        crossP = np.cross(r12,r13)
        crossPMag = np.sqrt(np.dot(crossP,crossP))

        r13Mag = np.sqrt(np.dot(r13,r13))

        x1temp = 0
        y1temp = 0

        y2temp = crossPMag/r13Mag
        x2temp = np.sqrt(np.dot(r12,r12)-(y2temp*y2temp))

        x3temp = r13Mag
        y3temp = 0

        #approximate the second derivative
        a = np.array([2/((x2temp-x1temp)*(x3temp-x1temp)), -2/((x3temp-x2temp)*(x2temp-x1temp)), 2/((x3temp-x2temp)*(x3temp-x1temp))])
        b = np.array([y1temp, y2temp, y3temp])
        deriv2 = np.append(deriv2, np.dot(a,b))

    #abs of all second derivatives and take exponential for finer control of waypoint threshold
    deriv2 = np.absolute(deriv2)
    deriv2 = np.exp(deriv2)

    #adds first point on path to waypoints
    xW = np.append(xW, x[0])
    yW = np.append(yW, y[0])


    spacer = 0
    for i in range(0, len(deriv2)): #finds running sum and sets a waypoint when the sum meets some threshold value
        spacer += deriv2[i]
        if spacer >= threshold:
            xW = np.append(xW, x[i])
            yW = np.append(yW, y[i])
            spacer = 0

    xW = np.append(xW, x[-1]) #adds last path point to waypoints
    yW = np.append(yW, y[-1])

    return xW,yW

def pid(objectPos,satPos,satVel,integrals,gains,prevErrors,waypointsX,waypointsY,waypointEdges,t0,sensor,f):
    thrusters = np.zeros(6) #number of thrusters, [+x,-x,+y,-y,+z,-z], 0 means off, 1 means on

    KpS = gains[0][0]
    KiS = gains[0][1]
    KdS = gains[0][2]

    KpR = gains[1][0]
    KiR = gains[1][1]
    KdR = gains[1][2]

    KpT = gains[2][0]
    KiT = gains[2][1]
    KdT = gains[2][2]

    uTolerance = .1

    xW = waypointsX
    yW = waypointsY

    objectX = objectPos[0]
    objectY = objectPos[1]

    xPos = satPos[0]
    yPos = satPos[1]

    xVel = satVel[0]
    yVel = satVel[1]

    startWaypoint = waypointEdges[0]
    endWaypoint = waypointEdges[1]

    #store previous error for derivative
    prevErrorS = prevErrors[0]
    prevErrorR = prevErrors[1]
    prevErrorT = prevErrors[2]

    integralS = integrals[0]
    integralR = integrals[1]
    integralT = integrals[2]

    phi = math.atan2((yW[endWaypoint]-yW[startWaypoint]),(xW[endWaypoint]-xW[startWaypoint])) #angle of checkpoint line wrt horizontal
    if phi < 0:
        phi += 2*math.pi

    waypointDist = math.sqrt(((yW[endWaypoint]-yW[startWaypoint])**2+(xW[endWaypoint]-xW[startWaypoint])**2)) #distance between checkpoints

    #get euler angle
    accX, accY, accZ = sensor.linear_acceleration
    euler1, euler2, euler3 = sensor.euler

    euler1 = euler1 * math.pi/180

    t1 = time.time()

    xPos, yPos, xVel, yVel = updateKinematics(xPos,yPos,xVel,yVel,euler1,accX,accY,t0,t1)

    errorS = waypointDist - (math.cos(phi)*(xPos - xW[startWaypoint]) + math.cos(phi)*(yPos - yW[startWaypoint])) #error along path
    errorR = -math.sin(phi)*(xPos - xW[startWaypoint]) + math.cos(phi)*(yPos - yW[startWaypoint]) #error perpendicular to path
    rT = math.atan2((objectY - yPos),(objectX - xPos)) #rotation setpoint
    if rT < 0:
        rT += math.pi*2
    errorT = rT - euler1 #rotation error

    #approximate all integrals
    integralS += errorS * (t1-t0)
    integralR += errorR * (t1-t0)
    integralT += errorT * (t1-t0)

    #PID calculations
    uS = errorS * KpS + integralS * KiS + (errorS - prevErrorS) / (t1-t0) * KdS
    uR = errorR * KpR + integralR * KiR + (errorR - prevErrorR) / (t1-t0) * KdR
    uT = errorT * KpT + integralT * KiT + (errorT - prevErrorT) / (t1-t0) * KdT

    t0 = t1

    #convert errors to body coordinates
    uX = math.cos(euler1 - phi) * uS + math.sin(euler1 - phi) * uR
    uY = -math.sin(euler1 - phi) * uS + math.cos(euler1 - phi) * uR

    #determine x thrusters
    if uX > uTolerance:
        thrusters[0] = 1
    elif uX < -uTolerance:
        thrusters[1] = 1

    #determine y thrusters
    if uY > uTolerance:
        thrusters[2] = 1
    elif uY < -uTolerance:
        thrusters[3] = 1

    #determine spin thrusters
    if uT > uTolerance:
        thrusters[4] = 1
    elif uT < -uTolerance:
        thrusters[5] = 1

    if errorS < .5 * waypointDist: #go to next checkpoint pair if tracsat has moved halway through current checkpoint pair
        waypointEdges[0] += 0
        waypointEdges[1] += 0

    integrals[0] = integralS
    integrals[1] = integralR
    integrals[2] = integralT

    satPos[0] = xPos
    satPos[1] = yPos

    satVel[0] = xVel
    satVel[1] = yVel

    prevErrors[0] = errorS
    prevErrors[1] = errorR
    prevErrors[2] = errorT

    f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(t0,xPos,yPos,xVel,yVel,accX,accY,euler1,errorS,errorR,errorT,thruster[0],thruster[1],thruster[2],thruster[3],thruster[4],thruster[5],uS,uR,uT))

    return thrusters,satPos,satVel,integrals,prevErrors,waypointEdges,t0

def updateKinematics(currentX,currentY,currentVx,currentVy,euler1,accX,accY,t0,t1):
    #convert body accelerations to inertial accelerations
    accXI = accX * math.cos(euler1) - accY * math.sin(euler1)
    accYI = accX * math.sin(euler1) + accY * math.cos(euler1)

    #approximate new velocity
    newVx = currentVx + accXI * (t1-t0)
    newVy = currentVy + accYI * (t1-t0)

    #approximate new position
    newX = currentX + currentVx * (t1-t0) + .5 * accXI * (t1-t0)**2
    newY = currentY + currentVy * (t1-t0) + .5 * accYI * (t1-t0)**2

    return newX,newY,newVx,newVy
