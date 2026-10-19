// Browser port of dragraceSim.py, so the page can run as a static site (GitHub Pages).
// Keep this in sync with dragraceSim.py if the model changes.

function topGradeSpeed(Cd, Cr, g, rhoAir, frontArea, mass, grade, velocity, wheelRadius) {
    const Froll = Cr * mass * g;
    const Fdrag = Cd * frontArea * rhoAir * velocity ** 2 / 2;
    const Fincl = mass * g * grade;
    const Ftrac = Froll + Fdrag + Fincl;
    return Ftrac * wheelRadius;
}

// closed form of the linsolve in dragraceSim.tractionMax
function tractionMax(mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire) {
    if (driveWheel === 'AWD') {
        return mass * g * muTire;
    } else if (driveWheel === 'FWD') {
        return muTire * mass * g * (1 - wtRearFrac) * wheelbase / (wheelbase + muTire * cgh);
    }
    // RWD case
    return muTire * mass * g * wtRearFrac * wheelbase / (wheelbase - muTire * cgh);
}

function accelerateVehicle(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                           desiredAccTime, muTire, wheelRadius) {
    // some constants
    const rhoAir = 1.2;
    const g = 9.81;
    const Cr = 0.01;
    const transLoss = 0.99 ** 3;

    // limit v1 max
    const vmax = 151.0 / 3.6;
    if (v1 > vmax) {
        v1 = vmax;
    }

    const wheelForceMax = tractionMax(mass, g, wtRearFrac, wheelbase, cgh, driveWheel, muTire);

    let power = 5e3;
    let simAccTime = 1e2;
    const timeTol = 0.01;
    const timeStep = 0.01;
    // guard so a non-converging input can't freeze the browser tab
    const maxIterations = 500;

    let times = [];
    let velocities = [];
    let torques = [];

    for (let iter = 0; Math.abs(simAccTime - desiredAccTime) > timeTol; iter++) {
        if (iter >= maxIterations) {
            throw new Error('Simulation did not converge');
        }
        let iterStep = 1;
        let vCur = v0;

        const timeratio = (simAccTime - desiredAccTime) / desiredAccTime;
        power = power + power * timeratio;

        times = [];
        velocities = [];
        torques = [];

        while (vCur < v1) {
            const wheelForce = vCur > 0 ? Math.min(wheelForceMax, power / vCur) : wheelForceMax;

            const tGS = topGradeSpeed(Cd, Cr, g, rhoAir, frontArea,
                                      mass, grade, vCur, wheelRadius) / wheelRadius;

            if (wheelForce - tGS <= 10) {
                break;
            }
            const loadDiff = wheelForce - tGS;

            const fDiff = Math.min(loadDiff * transLoss, wheelForceMax);
            const acceleration = fDiff / mass;
            const tCur = iterStep * timeStep;
            vCur = vCur + acceleration * timeStep;
            times.push(tCur);
            velocities.push(vCur);
            torques.push(wheelForce * wheelRadius);

            iterStep += 1;
        }
        simAccTime = iterStep * timeStep;

        if (power > 2e6) {
            console.warn('Reqd power > 2 MW, its not gonna happen');
            break;
        }
    }
    const missionPass = !(power / v1 > wheelForceMax);
    return { times, torques, velocities, power, missionPass };
}

// equivalent of dragraceSim.sim_json, returns the struct the charts expect
function simJson(Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
                 desiredAccTime, muTire, wheelRadius, name) {
    const { times, torques, velocities, power, missionPass } = accelerateVehicle(
        Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel,
        desiredAccTime, muTire, wheelRadius);

    if (velocities.length === 0) {
        throw new Error('Vehicle cannot accelerate with these inputs');
    }

    // only keep every 20th value to keep Chart.js animations smooth
    const outslice = 20;
    const every = (arr) => arr.filter((_, i) => i % outslice === 0).concat([arr[arr.length - 1]]);
    const vel = every(velocities);
    const tq = every(torques);
    const time = every(times);
    const pwr = vel.map((v, i) => v * tq[i] / wheelRadius / 1e3);

    return {
        Modelname: name,
        Power: power * 1e-3,
        SolutionFound: missionPass,
        torquespeed: vel.map((v, i) => ({ x: v, y: tq[i] })),
        timespeed: time.map((t, i) => ({ x: t, y: vel[i] })),
        powerspeed: vel.map((v, i) => ({ x: v, y: pwr[i] })),
    };
}

if (typeof module !== 'undefined') {
    module.exports = { tractionMax, accelerateVehicle, simJson };
}
