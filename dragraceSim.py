
import sympy as sym
from sympy.solvers.solveset import linsolve
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

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
        #extract the solution for eq3
        wheelForceMax = X.args[0][2]
    else:

        eq1 = Fr + Ff - mass*g
        eq2 = Fr*(1-wtRearFrac)*wheelbase - Ff*wtRearFrac*wheelbase - Fa*cgh
        eq3 = Fa - Fr*muTire

        X = linsolve([eq1, eq2, eq3], (Fr, Ff, Fa))
        #extract the solution for eq3
        wheelForceMax = X.args[0][2]
    
    return wheelForceMax

def accelerateVehicle(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel, \
desiredAccTime, muTire, wheelRadius):
    #debug output
    print(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, \
        wheelbase, driveWheel, \
        desiredAccTime, muTire, wheelRadius) 
    #some constantas
    rhoAir      = 1.2
    g           = 9.81
    Cr          = 0.01
    transLoss   = 0.99**3
    timeTol  = 0.1

    #limit v1 max to
    vmax = 151.0/3.6
    if v1 > vmax:
        v1 = vmax
    
    #initial value
    acceleration = 0

    #call wheelforcemax
    wheelForceMax  = tractionMax(mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire)
    wheelTorqueMax = wheelForceMax * wheelRadius

    #start search for optimal wheeltorque curve given constraints.
    #initialize power and time with some high values
    power       = 10.0e3
    simAccTime  = 1.0e6

    while abs(simAccTime - desiredAccTime) > timeTol:
        #initialize temporary variables
        iterStep = 1
        timeStep = 0.01
        vCur     = v0
        pCar     = 0 #momentum?

        if simAccTime > desiredAccTime+timeTol:
            power = power * (1+np.sqrt(5))/2
        else:
            power = power * 0.75
        ### print intermediate outputs by uncommenting below
        print('power=',power*1e-3) 
        velocities  = []
        torques     = []

        while vCur < v1:
            if vCur > 0:
                wheelForce = min(wheelForceMax, power/vCur)
            else:
                wheelForce = wheelForceMax 

            if wheelForce - topGradeSpeed(Cd, Cr, g, rhoAir, frontArea, mass, grade, vCur, wheelRadius)/wheelRadius <= 10:
                break
            else:
                loadDiff = wheelForce - topGradeSpeed(Cd, Cr, g, rhoAir, frontArea, mass, grade, vCur, wheelRadius)/wheelRadius
            fDiff = min(loadDiff*transLoss, wheelForceMax)
            acceleration = fDiff / mass
            vCur = vCur + acceleration*timeStep
            velocities.append(vCur)
            torques.append(wheelForce*wheelRadius)
            pCar = pCar + vCur * timeStep

            #all done, go to next timestep
            iterStep += 1
        #when a time is found, update the simulated acceleration time
        simAccTime = iterStep*timeStep
        
        if power > 2e6:
            print('Reqd power > 2 MW, its not gonna happen')
            break

    return torques, velocities, power

def plot_png(xs, ys):
    setdpi=600
    plt.plot(xs, ys, label=f'{power/1e3:.0f} kW')
    plt.xlabel('Velocity [m/s]')
    plt.ylabel('Torque [Nm]')
    plt.legend(loc='best')
    plt.ylim(bottom=0)
    plt.savefig('static/images/torque.png', dpi=setdpi)
    return 'plotting done, see disk'

def output_json(torques, velocities, power):
    #this will be the ugliest workaround ever.
    output_csv(torques, velocities, power)
    df = pd.read_csv(f'static/csv/torques{power/1e3:.0f}kW.csv')
    df.to_json(f'static/json/torques{power/1e3:.0f}kW.json')
    return 'done printing json'


def output_csv(torques, velocities, power):
    with open(f'static/csv/torques{power/1e3:.0f}kW.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', \
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['velocity[m/s], torque[Nm]'])
        for i, val in enumerate(torques):
            writer.writerow([velocities[i], torques[i]])
    return 'done printing csv'

if __name__ == "__main__":
    mass = 1500.0
    Cd = 0.3
    frontArea = 2.0
    grade = 0.0
    v0 = 0.0
    v1 = 100.0/3.6
    cgh = 0.6
    wtRearFrac = 0.56
    wheelbase = 2.5
    driveWheel = 'RWD'
    desiredAccTime = 6.0
    muTire = 0.9
    wheelRadius = 0.3

    #an example string: 0.3, 2, 1300, 0, 0, 33, 0.5, 0.4, 2.5, 6, 0.95, 0.3

    torques, velocities, power = accelerateVehicle(Cd, frontArea, mass, grade, v0,\
         v1, cgh, wtRearFrac, wheelbase, driveWheel, \
         desiredAccTime, muTire, wheelRadius)

    message = plot_png(velocities, torques)
    print(message)
    message = output_json(torques, velocities, power)
    print(message)
    message = output_csv(torques, velocities, power)
    print(message)

    print(f'Power is {power*1e-3} kW')
