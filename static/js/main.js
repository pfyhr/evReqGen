/*fetch("./static/json/torques126kW.json")
    .then(response => {
        return response.json();
    })
.then(jsondata => console.log(jsondata));*/

/*async function getData() {
    let url = './static/json/torques126kW.json';
    try {
        const res = await fetch(url);
        const jsondata =  await res.json();
        const textdata = await res.text();
        console.log(jsondata)
    } catch (error) {
        console.log(error);
    }
}*/

// Empty arrays for the data to be plotted

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

// [{
//             label: 'Dataset with string point data',
//             backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
//             borderColor: window.chartColors.red,
//             fill: false,
//             data: [{
//                 x: newDateString(0),
//                 y: randomScalingFactor()
//             }, {
//                 x: newDateString(2),
//                 y: randomScalingFactor()
//             }, {
//                 x: newDateString(4),
//                 y: randomScalingFactor()
//             }, {
//                 x: newDateString(5),
//                 y: randomScalingFactor()
//             }],
//         },

var color = Chart.helpers.color;
var config = {
    type: 'line',
    data: {
        datasets:  [{
            label: 'Dataset with date object point data',
            backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
            borderColor: window.chartColors.blue,
            fill: false,
            data: [{
                x: newDate(0),
                y: randomScalingFactor()
            }, {
                x: newDate(2),
                y: randomScalingFactor()
            }, {
                x: newDate(4),
                y: randomScalingFactor()
            }, {
                x: newDate(5),
                y: randomScalingFactor()
            }]
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Chart.js Time Point Data'
        },
        scales: {
            xAxes: [{
                type: 'data',
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
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Torque [Nm]'
                }
            }]
        }
    }
};

window.onload = function() {
			var ctx = document.getElementById('canvas').getContext('2d');
			window.myLine = new Chart(ctx, config);
		};

document.getElementById('addData').addEventListener('click', function() {
			if (config.data.datasets.length > 0) {
				config.data.datasets[0].data.push({
					x: newDateString(config.data.datasets[0].data.length + 2),
					y: randomScalingFactor()
				});
				config.data.datasets[1].data.push({
					x: newDate(config.data.datasets[1].data.length + 2),
					y: randomScalingFactor()
				});

				window.myLine.update();
			}
        });

document.getElementById('removeData').addEventListener('click', function() {
			config.data.datasets.forEach(function(dataset) {
				dataset.data.pop();
			});

			window.myLine.update();
		});

async function makePlot(csvstring, csv2) {
    //const datastore = await getData(csvstring);
    //const i3store = await getData(secondcsv);
    textdata = await getJSON(csvstring)
    otherdata = await getJSON(csv2)
    
    const ctx = document.getElementById('plot').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            //labels: datastore.xvals,
            datasets: [ {
                label: textdata.Modelname,
                type: 'line',
                borderColor: "#8e5ea2",
                data: textdata.xydata
            },
            {
                label: otherdata.Modelname,
                type: 'line',
                borderColor: '#f7347a',
                data: otherdata.xydata
            }
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    //labelString: 'Torque [Nm]'
                    ticks: {
                        beginAtZero: true
                    }
                }]
            } 
        }
    });
    //return myChart
};

function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();
}

const leaf = './static/json/leafRealData.json';
const filepath = './static/json/i3RealData.json';
makePlot(filepath, leaf);
//const newdata = getData(i3path)
//console.log(newdata)
//addData(myChart, 'i3', newdata );