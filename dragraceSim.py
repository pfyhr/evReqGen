import sympy as sym
from sympy.solvers.solveset import linsolve
import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd
import csv

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
        print('AWD')
        wheelForceMax = mass*g*muTire
    elif driveWheel == 'FWD':
        print('FWD')
        eq1 = Fr + Ff - mass*g
        eq2 = Fr*(1-wtRearFrac)*wheelbase - Ff*wtRearFrac*wheelbase - Fa*cgh
        eq3 = Fa - Ff*muTire

        X = linsolve([eq1, eq2, eq3], (Fr, Ff, Fa))
        # extract the solution for eq3
        wheelForceMax = X.args[0][2]
    else: #RWD case

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

    #call tractionForceMax
    wheelForceMax  = tractionMax(mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire)
    #wheelTorqueMax = wheelForceMax * wheelRadius

    # start search for optimal wheeltorque curve given constraints.
    # initialize power and time with some gues values, maybe
    # here the guess should be based on one run...
    # the while loop below should be broken out into a function.
    # that removes the optimizing bit and just runs "a vehicle" with
    # whatever power is chosen.
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
                wheelForce = np.minimum(wheelForceMax, power/vCur)
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
            #acceleration limited by friction
    if power/v1 > wheelForceMax:
        mission_pass = False
    else:
        mission_pass = True
    return torques, velocities, power, mission_pass

def plot_png(xs, ys):
    setdpi=600
    plt.plot(xs, ys, label=f'{power/1e3:.0f} kW')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Torque [Nm]')
    plt.legend(loc='best')
    plt.ylim(bottom=0)
    plt.savefig('static/images/torque.png', dpi=setdpi)
    return 'plotting done, see disk'

def output_csv(torques, velocities, power):
    with open(f'static/csv/torques{power/1e3:.0f}kW.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', \
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['velocity[m/s], torque[Nm]'])
        for i, val in enumerate(torques):
            writer.writerow([velocities[i], torques[i]])
    return 'done printing csv'

def sim_json(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                                                   desiredAccTime, muTire, wheelRadius, name):
    #run the simulation
    torques, velocities, power, mission_pass = accelerateVehicle(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                                                   desiredAccTime, muTire, wheelRadius)

    # make a zip of it, iterate over things in the zip and stuff them into a dict.
    # the [::10] returns only each 10th value, to save the Chart.JS some effort and make
    # the plot animations a bit smoother.
    xys = [{'x':i, 'y':j} for i,j in zip(velocities[::20], torques[::20])] 
    string_dict = {'xydata': xys, 'Power': power*1e-3, 'Modelname': name, 'SolutionFound': mission_pass}
    return string_dict

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
    name = 'mainsim'

    start_time = time.time()
    json = sim_json(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel, \
                                                  desiredAccTime, muTire, wheelRadius, name)
    dt = (time.time()-start_time)
    
    print("Solution found {:.3f} kW in {:.3f} s".format(json['Power'], dt))
    #print(json)
