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
const xvals = [];
const yvals = [];

async function getData() {
    let url = './static/csv/torques126kW.csv';
    try {
        const res = await fetch(url);
        const textdata = await (await res.text()).trim();
        //console.log(textdata);
        
        const labels = textdata.split('\n').slice(0,1); //put labels here
        const table = textdata.split('\n').slice(1); //keep datarows only
        table.forEach(row => {
            const columns = row.split(',')
            const velocity = columns[0];
            const torque = columns[1];
            xvals.push(velocity);
            yvals.push(torque);
            console.log(velocity, torque);
        });
    } catch (error) {
        console.log(error);
    }
}

async function makePlot() {
    await getData();
    const ctx = document.getElementById('plot').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: xvals,
            datasets: [{
                label: 'Generated torques',
                data: yvals
                }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            } 
        }
    });
};

makePlot();