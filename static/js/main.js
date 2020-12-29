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
                label: textdata.power,
                type: 'line',
                borderColor: "#8e5ea2",
                data: textdata.i3real
            },
            {
                label: otherdata.Leaf_real,
                type: 'line',
                borderColor: '#f7347a',
                data: otherdata.name
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