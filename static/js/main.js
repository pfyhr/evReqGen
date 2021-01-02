// the javascript file that makes plots, gets data and so on.
//get data from jsonfiles
const leaf_real = './static/json/leafRealData.json';
const i3_real = './static/json/i3RealData.json';
const egolf_sim = '.static/json/egolfSimData.json';
const model3_sim = './static/json/model3SimData.json';
//cars

//some colorconfig from chart.js
var color = Chart.helpers.color;

window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};

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
            //console.log(velocity, torque);
        });
    } catch (error) {
        console.log(error);
    }
    return {xvals, yvals}
}

async function getJSON(csvstring) {
    const res = await fetch(csvstring);
    //console.log(res)
    const textdata = await res.json();
    console.log(textdata)
    return textdata
}
async function makecarstruct(car) {
    var cardata = await getJSON(car);
    var carstruct = {
        label: cardata.Modelname,
        type: 'line',
        borderColor: window.chartColors.red,
        data: cardata.xydata
    };
    return carstruct
}

async function makevehicledata() {
    var leaf = await makecarstruct(leaf_real);
    var egolf = await makecarstruct(i3_real);
    //put the vehicle data in a struct that config understands
    var vehicledatas = {
        datasets: [
            leaf,
            egolf
        ]
    };
    return vehicledatas
}

async function makeconfig() {
    vehicledatas = await makevehicledata();
    var config = {
        type: 'scatter',
        data: vehicledatas,
        options: {
            //responsive: true,
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


window.onload = async function() {
    var config = await makeconfig();
    console.log(config)
    var ctx = document.getElementById('plot').getContext('2d');
    window.theplot = new Chart(ctx, config);
};

        
document.getElementById('removeData').addEventListener('click', function() {
    //console.log(vehicledatas.datasets.length)
    var element = vehicledatas.datasets.pop();
    //console.log(element)
    //var leafxy = getJSON('./static/json/leafRealData.json');
    //console.log(leafxy.xydata)
    window.theplot.update();
}); 

document.getElementById('addData').addEventListener('click', async function() {
    var newstruct = await makecarstruct(model3_sim);
    vehicledatas.datasets.push(newstruct);
    console.log(newstruct)
    //var leafxy = getJSON('./static/json/leafRealData.json');
    //console.log(leafxy.xydata)
    window.theplot.update();
}); 