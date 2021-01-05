// the javascript file that makes plots, gets data and so on.

//get data from jsonfiles
//this seems to only work on *nix at the moment.
const leaf_real = './static/json/leafRealData.json';
const i3_real = './static/json//i3RealData.json';
const egolf_sim = './static/json//egolfSimData.json';
const model3_sim = './static/json/model3SimData.json';

//some colorconfig from chart.js
//Want to make a color-rotating function soon to make the plots look nicer.

// shamelessly stole a color from: https://nagix.github.io/chartjs-plugin-colorschemes/
const Paired12 = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928'];

var currentColorIndex = 0;
const colorIndexLength = 12;

function getColor() {
    var color = Paired12[currentColorIndex]; 
    console.log(color)
    if (currentColorIndex >= colorIndexLength) {
        console.log('inside if')
        currentColorIndex = 0;
        }
    else {
        console.log('inside else')
        currentColorIndex = currentColorIndex+1;
        console.log(currentColorIndex)
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
async function makecarstruct(car) {
    var cardata = car; // await getJSON(car);
    var carstruct = {
        label: cardata.Modelname,
        type: 'line',
        borderColor: getColor(),
        data: cardata.xydata
    };
    return carstruct
};

//create a vehicle dataset, containing two vehicles
async function makevehicledata() {
    var leaf = await makecarstruct(getJSON(leaf_real));
    var egolf = await makecarstruct(getJSON(i3_real));
    //put the vehicle data in a struct that config understands
    var vehicledatas = {
        datasets: [
            leaf,
            egolf
        ]
    };
    return vehicledatas
};

//make the config json for the vehicle data above
async function makeconfig() {
    vehicledatas = await makevehicledata();
    var config = {
        type: 'scatter',
        data: vehicledatas,
        options: {
            // plugins: {
            //     colorschemes: {
            //         scheme: 'tableau.Winter10'
            //     }
            // },
            title: {
                display: true,
                text: 'Wheel torque data'
            },
            scales: {
                 xAxes: [{
                    //type: 'data',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Velocity [m/s]'
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
                        labelString: 'Torque [Nm]'
                    }
                }]
            }
        }
    }
        return config;
    };

//finally create the chart, using the generated config
window.onload = async function() {
    var config = await makeconfig();
    console.log(config)
    var ctx = document.getElementById('plot').getContext('2d');
    window.theplot = new Chart(ctx, config);
};

//this pops the last added data from the chart        
document.getElementById('removeData').addEventListener('click', function() {
    var element = vehicledatas.datasets.pop();
    //console.log(element) //if you want to look at what you popped
    window.theplot.update();
}); 

//this adds a predetermined data at the moment
document.getElementById('addData').addEventListener('click', async function() {
    var newstruct = await makecarstruct(model3_sim);
    vehicledatas.datasets.push(newstruct);
    console.log(newstruct)
    window.theplot.update();
});

//this tries to take the returned simfile and push it to the chart
async function addsimresult(simresult) {
    console.log(simresult)
    var simstruct = await makecarstruct(simresult);
    vehicledatas.datasets.push(simstruct);
    //console.log(simstruct)
    window.theplot.update();
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


