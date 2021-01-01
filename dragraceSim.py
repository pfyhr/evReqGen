
import sympy as sym
from sympy.solvers.solveset import linsolve
import numpy as np

import time


def topGradeSpeed(Cd, Cr, g, rhoAir, frontArea, mass, grade, velocity, wheelRadius):
    Froll = Cr * mass * g
    Fdrag = Cd*frontArea*rhoAir*(velocity)**2/2
    Fincl = mass * g * grade
    Ftrac = Froll + Fdrag + Fincl
    wheelTorque = Ftrac*wheelRadius

    return wheelTorque


def tractionMax(mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire):
    Fr = sym.Symbol('Fr')
    Ff = sym.Symbol('Ff')
    Fa = sym.Symbol('Fa')

    if driveWheel == 'AWD':
        wheelForceMax = mass*g*muTire
    elif driveWheel == 'FWD':
        eq1 = Fr + Ff - mass*g
        eq2 = Fr*(1-wtRearFrac)*wheelbase - Ff*wtRearFrac*wheelbase - Fa*cgh
        eq3 = Fa - Ff*muTire

        X = linsolve([eq1, eq2, eq3], (Fr, Ff, Fa))
        # extract the solution for eq3
        wheelForceMax = X.args[0][2]
    else:

        eq1 = Fr + Ff - mass*g
        eq2 = Fr*(1-wtRearFrac)*wheelbase - Ff*wtRearFrac*wheelbase - Fa*cgh
        eq3 = Fa - Fr*muTire

        X = linsolve([eq1, eq2, eq3], (Fr, Ff, Fa))
        # extract the solution for eq3
        wheelForceMax = X.args[0][2]

    # cast to float for speed
    return float(wheelForceMax)


def accelerateVehicle(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                      desiredAccTime, muTire, wheelRadius):

    # some constantas
    rhoAir = 1.2
    g = 9.81
    Cr = 0.01
    transLoss = 0.99**3

    # limit v1 max to
    vmax = 151.0/3.6
    if v1 > vmax:
        v1 = vmax

    # initial value
    acceleration = 0.

    # call wheelforcemax
    wheelForceMax = tractionMax(
        mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire)

    wheelTorqueMax = wheelForceMax * wheelRadius

    # start search for optimal wheeltorque curve given constraints.
    # initialize power and time with some high values
    #prevpower = 2.5e3
    power = 5e3
    simAccTime = 1e2
    timeTol = 0.01
    timeStep = 0.01

    while abs(simAccTime - desiredAccTime) > timeTol:
        # initialize temporary variables
        iterStep = 1
        vCur = v0
        pCar = 0.  #position!

        #try to come up with some nicer way to converge to the correct solution
        #store two previous powers, and use some linear extrapolation from that

        #some ratio of the previous and most recently tried power
        #below will be some factor with sign if power should increase or decrease
        timeratio = (simAccTime - desiredAccTime)/desiredAccTime
        #store back prev before overwriting
        prevpower = power
        power = prevpower + (prevpower * timeratio)

        print('power=', power*1e-3)
        velocities = []
        torques = []

        while vCur < v1:
            if vCur > 0:
                wheelForce = min(wheelForceMax, power/vCur)
            else:
                wheelForce = wheelForceMax

            tGS = topGradeSpeed(Cd, Cr, g, rhoAir, frontArea,
                                mass, grade, vCur, wheelRadius)/wheelRadius

            if wheelForce - tGS <= 10:
                break
            else:
                loadDiff = wheelForce - tGS

            fDiff = min(loadDiff*transLoss, wheelForceMax)
            acceleration = fDiff / mass
            vCur = vCur + acceleration*timeStep
            velocities.append(vCur)
            torques.append(wheelForce*wheelRadius)
            pCar = pCar + vCur * timeStep

            # all done, go to next timestep
            iterStep += 1
        # when a time is found, update the simulated acceleration time
        simAccTime = iterStep*timeStep

        if power > 2e6:
            print('Reqd power > 2 MW, its not gonna happen')
            break

    return torques, velocities, power


if __name__ == "__main__":
    mass = 1800.
    Cd = 0.3
    frontArea = 2.
    grade = 0.
    v0 = 0.
    v1 = 100.0/3.6
    cgh = 0.6
    wtRearFrac = 0.56
    wheelbase = 2.5
    driveWheel = 'RWD'
    desiredAccTime = 9.
    muTire = 0.9
    wheelRadius = 0.3

    start_time = time.time()
    torques, velocities, power = accelerateVehicle(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                                                   desiredAccTime, muTire, wheelRadius)
    dt = (time.time()-start_time)
    print("Solution found {:.3f} kW in {:.3f} s".format(power*1e-3, dt))
