from flask import Flask, render_template, url_for, request
import dragraceSim

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        Cd              = float(request.form['Cd'])
        frontArea       = float(request.form['frontArea'])
        mass            = float(request.form['mass'])
        grade           = float(request.form['grade'])
        v0              = float(request.form['v0'])
        v1              = float(request.form['v1'])
        cgh             = float(request.form['cgh'])
        wtRearFrac      = float(request.form['wtRearFrac'])
        wheelbase       = float(request.form['wheelbase'])
        driveWheel      = request.form['driveWheel']
        desiredAccTime  = float(request.form['desiredAccTime'])
        muTire          = float(request.form['muTire'])
        wheelRadius     = float(request.form['wheelRadius'])

        try:
            #a bit ugly oneliner to split input arguments, map them to floats, put them in a list
            #chunks = list(map(float, arguments.split(',')))
            #print(chunks)
            #if len(chunks) == 12:
            print('running with:', Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, \
                 wheelbase, driveWheel, desiredAccTime, muTire, wheelRadius)

            torques, velocities, power = dragraceSim.accelerateVehicle(Cd, frontArea, mass, \
                 grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel, desiredAccTime, muTire, wheelRadius)
            
            print(power/1e3)
            #message = dragraceSim.plot_png(velocities, torques)
            #print(message)
            return render_template('index.html')
        except:
            return 'some issue occured'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)