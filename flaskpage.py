from flask import Flask, render_template, url_for, request
import dragraceSim
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        arguments = request.form['content']
        
        try:
            #a bit ugly oneliner to split input arguments, map them to floats, put them in a list
            chunks = list(map(float, arguments.split(',')))
            print(chunks)
            if len(chunks) == 12:
                torques, velocities, power = dragraceSim.accelerateVehicle(chunks[0], chunks[1], \
                    chunks[2], chunks[3], chunks[4], chunks[5], chunks[6], chunks[7], chunks[8], 'RWD', \
                        chunks[9], chunks[10], chunks[11])
            else:
                torques, velocities, power = dragraceSim.accelerateVehicle(0.35, 2, 1300, 0, 0, 33, 0.5, 0.4, 2.5, 'RWD', \
                    6, 0.95, 0.3)
                print(power)
        except:
            return 'some issue occured'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)