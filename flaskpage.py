from flask import Flask, request, send_from_directory
import dragraceSim

app = Flask(__name__)

# the page itself is a static site (also served on GitHub Pages), see index.html

@app.route('/', methods=['POST', 'GET'])
def index():
    return send_from_directory(app.root_path, 'index.html')

@app.route('/runsim', methods=['POST', 'GET'])
def sim():
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
        name            = request.form['Name']
        #ata = request.data
        print('running with:', Cd, frontArea, mass, grade, v0, v1, cgh, wtRearFrac, \
             wheelbase, driveWheel, desiredAccTime, muTire, wheelRadius, name)
        
        try:
            simfile = dragraceSim.sim_json(Cd, frontArea, mass, \
                grade, v0, v1, cgh, wtRearFrac, wheelbase, driveWheel, desiredAccTime, muTire, wheelRadius, name)
            
            return simfile
            
        except:
            return 'some issue occured'

    else:
        return send_from_directory(app.root_path, 'index.html')

if __name__ == "__main__":
    app.run(debug=True)