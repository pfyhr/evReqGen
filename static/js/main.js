// the javascript file that makes plots, gets data and so on.

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

async function makevehicledata() {
    
    //get data from jsonfiles
    const leaf = './static/json/leafRealData.json';
    const i3 = './static/json/i3RealData.json';
    var leafdata = await getJSON(leaf);
    var i3data = await getJSON(i3);

    //put the vehicle data in a struct that config understands
    var vehicledatas = {
        datasets: [{
            label: leafdata.Modelname,
            type: 'line',
            borderColor: "#8e5ea2",
            data: leafdata.xydata
        },
        {
            label: i3data.Modelname,
            type: 'line',
            borderColor: '#f7347a',
            data: i3data.xydata
        }]
    };
    return vehicledatas
}

async function makeconfig() {
    vehicledatas = await makevehicledata();
    var config = {
        type: 'scatter',
        data: vehicledatas,
        options: {
            // responsive: true,
            // title: {
            //     display: true,
            //     text: 'Wheel torque data'
            // },
            // scales: {
            //     xAxes: [{
            //         type: 'data',
            //         display: true,
            //         scaleLabel: {
            //             display: true,
            //             labelString: 'Velocity [m/s]'
            //         },
            //         ticks: {
            //             major: {
            //                 fontStyle: 'bold',
            //                 fontColor: '#FF0000'
            //             }
            //         }
            //     }],
            //     yAxes: [{
            //         display: true,
            //         scaleLabel: {
            //             display: true,
            //             labelString: 'Torque [Nm]'
            //         }
            //     }]
            // }
        }
    };
    return config;
}

window.onload = async function() {
    var config = await makeconfig();
    console.log(config)
    var ctx = document.getElementById('plot').getContext('2d');
    window.theplot = new Chart(ctx, config);
};


// document.getElementById('randomizeData').addEventListener('click', function() {
//     console.log(vehicledatas.datasets[0])
//     var leafxy = getJSON('./static/json/leafRealData.json');
//     console.log(leafxy.xydata)
//     window.theplot.update();
// }); 

