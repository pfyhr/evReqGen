// the javascript file that makes plots, gets data and so on.

//get data from jsonfiles
//this seems to only work on *nix at the moment.
const leaf_real = './static/json/leafRealData.json';
const i3_real = './static/json//i3RealData.json';
const egolf_sim = './static/json//egolfSimData.json';
const model3_sim = './static/json/model3SimData.json';

//Want to make a color-rotating function soon to make the plots look nicer.
// shamelessly stole a color from: https://nagix.github.io/chartjs-plugin-colorschemes/
const Paired12 = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928'];

var currentColorIndex = 0;
const colorIndexLength = Paired12.length;

function getColor() {
    var color = Paired12[currentColorIndex]; 
    if (currentColorIndex >= colorIndexLength) {
        currentColorIndex = 0;
        }
    else {
        currentColorIndex = currentColorIndex+1;
        }
    return color;
}

//make a jsondata from a CSVfile, not used anymore.
async function getData(csvstring) {
    const xvals = [];
    const yvals = [];
    let url = csvstring;
    try {
        const res = await fetch(url);
        const textdata = (await res.text()).trim();
        //console.log(textdata);
        
        const labels = textdata.split('\n').slice(0,1); //put labels here
        const table = textdata.split('\n').slice(1); //keep datarows only
        table.forEach(row => {
            const columns = row.split(',')
            const velocity = columns[0];
            const torque = columns[1];
            xvals.push(parseFloat(velocity).toFixed(0)); //this is horribly ill nested
            yvals.push(parseFloat(torque));
        });
    } catch (error) {
        console.log(error);
    }
    return {xvals, yvals}
};

//fetch some JSON file from disk
async function getJSON(csvstring) {
    const res = await fetch(csvstring);
    //console.log(res)
    const textdata = await res.json();
    console.log(textdata)
    return textdata
};

//make a json for one car, passed as function input
async function makecarstruct(cardata, title, color) {
    console.log('is wheeltq true', (title=='Wheel torque'))
    console.log('is wheelpwr true', (title=='Wheel power'))
    var carstruct = {
        label: cardata.Modelname,
        type: 'line',
        borderColor: color,
        data: (title=='Wheel torque') ? cardata.torquespeed : (title=='Wheel power') ? cardata.powerspeed : cardata.timespeed 
    };
    console.log('data is', carstruct.data)
    return carstruct
};

//create a vehicle dataset, containing two vehicles
async function makevehicledata(title) {
    var leaf = await makecarstruct( await getJSON(leaf_real), title);
    //var egolf = await makecarstruct(getJSON(i3_real));
    //put the vehicle data in a struct that config understands
    var vehicledatas = {
        datasets: []
    };
    return vehicledatas
};

//make the config json for the vehicle data above
async function makeconfig(title, xlabel, ylabel, dataname) {
    var config = {
        type: 'scatter',
        data: dataname,
        options: {
            title: {
                display: true,
                text: title 
            },
            scales: {
                 xAxes: [{
                    //type: 'data',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: xlabel 
                    },
                    ticks: {
                        major: {
                            fontStyle: 'bold',
                            fontColor: '#FF0000'
                        }
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: ylabel 
                    }
                }]
            }
        }
    }
        return config;
    };

//create speedtorque chart
window.onload = async function() {
    torque = await makevehicledata('Wheel torque');
    var config = await makeconfig('Wheel torque', 'Speed [m/s]', 'Torque [Nm]', torque);
    console.log(config)
    var ctx = document.getElementById('speedtorque').getContext('2d');
    window.torquespeed = new Chart(ctx, config);
    //chart2
    speed = await makevehicledata('Vehicle speed');
    var config2 = await makeconfig('Vehicle speed', 'Time [s]', 'Speed [m/s]', speed);
    console.log(config2)
    var ctx2 = document.getElementById('timespeed').getContext('2d');
    window.timespeed = new Chart(ctx2, config2);
    //chart3
    power = await makevehicledata('Wheel power');
    var config3 = await makeconfig('Wheel power', 'Speed [m/s]', 'Power [kW]', power);
    console.log(config3)
    var ctx3 = document.getElementById('speedpower').getContext('2d');
    window.powerspeed = new Chart(ctx3, config3);
};

//this pops the last added data from the chart        
document.getElementById('removeData').addEventListener('click', function() {
    torque.datasets.pop();
    speed.datasets.pop();
    power.datasets.pop();
    //console.log(element) //if you want to look at what you popped
    torquespeed.update();
    timespeed.update();
    powerspeed.update();
}); 

//this tries to take the returned simfile and push it to the chart
async function addsimresult(simresult) {
    console.log(simresult)
    color =  getColor();
    var torquestruct = await makecarstruct(simresult, 'Wheel torque', color);
    torque.datasets.push(torquestruct);
    var speedstruct = await makecarstruct(simresult, 'Vehicle speed', color);
    speed.datasets.push(speedstruct);
    var powerstruct = await makecarstruct(simresult, 'Wheel power', color)
    //console.log(simstruct)
    torquespeed.update();
    timespeed.update();
    powerspeed.update();
};

// This selects "a form any form" on the page. which is not great. 
// These are from the very great MDN page
var formElem = document.querySelector('form');
// console.log(formElem)

formElem.addEventListener('submit', (e) => {
    // on form submission, prevent default
    e.preventDefault();

    // construct a FormData object, which fires the formdata event
    new FormData(formElem);
});

formElem.addEventListener('formdata', (e) => {
    // Get the form data from the event object
    let data = e.formData;
    //try to submit via fetch, which seems to work better than xhttpreq :) 
    fetch('/runsim', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(result => {
        console.log('Success:', result);
        //add the data to the plot window
        addsimresult(result);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


