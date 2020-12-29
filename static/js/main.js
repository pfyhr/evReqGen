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

async function makePlot(csvstring) {
    //const datastore = await getData(csvstring);
    //const i3store = await getData(secondcsv);

    const res = await fetch(csvstring);
    console.log(res)
    const textdata = await res.json();
    console.log(textdata)
    const ctx = document.getElementById('plot').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            //labels: datastore.xvals,
            datasets: [{
                label: 'Generated torques',
                type: 'line',
                borderColor: "#8e5ea2",
                data: textdata.i3real
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

const i3path = './static/csv/i3SimData.csv';
const filepath = './static/json/i3RealData.json';
makePlot(filepath);
//const newdata = getData(i3path)
//console.log(newdata)
//addData(myChart, 'i3', newdata );