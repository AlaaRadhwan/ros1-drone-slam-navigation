
var latitudes = [];
var longitudes = [];

var latData = {
    labels: [0],
    datasets: [

        {
            label: 'Latitude Differences',
            data: [0],
            borderColor: 'rgb(119, 145, 169)',
            lineTension: 0.5
        }
    ]
};

var lngData = {
    labels: [0],
    datasets: [
        {
            label: 'Longitude Differences',
            data: [0],
            borderColor: 'rgb(189, 145, 199)',
            lineTension: 0.5
        }
    ]
};

var latConfig = {
    type: 'line',
    data: latData,
};

var lngConfig = {
    type: 'line',
    data: lngData,
};

var latChart = new Chart(
    document.getElementById('lat-graph'),
    latConfig,
    
);

var lngChart = new Chart(
    document.getElementById('lng-graph'),
    lngConfig,
);

// window.setInterval(receive_coordinates(), 1000);
receive_coordinates();

// setInterval(receive_coordinates, 1000);

window.setInterval(mycallback, 2000);

function mycallback() {

    receive_coordinates()

    var now = new Date();


    latData.datasets[0].data = latitudes;
    lngData.datasets[0].data = longitudes;



    now = now.getSeconds();
    latData.labels.push(now);
    lngData.labels.push(now);

    latChart.update();
    lngChart.update();
}

function receive_coordinates() {
    fetch('/receive_graph_coordinates')
    .then(response => response.json())
    .then(data => {
        // Add received lat and lng to respective arrays
        latitudes.push(data.lat);
        longitudes.push(data.lng);

    })

    // setTimeout(receive_coordinates, 1000);
}