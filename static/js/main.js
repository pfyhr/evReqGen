/*fetch("./static/json/torques126kW.json")
    .then(response => {
        return response.json();
    })
.then(jsondata => console.log(jsondata));*/

async function getData() {
    let url = './static/json/torques126kW.json';
    try {
        let res = await fetch(url);
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

let jsondata = getData()

const ctx = document.getElementById('plot').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: [{
                x: jsondata.velocity,
                y: jsondata.torque
            }]
        }]
    },
    options: {
        scales: {
            xAxes: [{
                type: 'linear',
                position: 'bottom'
            }]
        }
    }
});
