// // Initialize empty arrays to store latitude and longitude data
// var latitudes = [];
// var longitudes = [];

// var timeList = [];

// // Initialize the graph
// var layout = {
//     title: 'Real-time Drone Location',
//     xaxis: { title: 'Time' },
//     yaxis: { title: 'Coordinate' }
// };
// var config = { responsive: true };
// var graph = document.getElementById('graph');

// // Function to update the graph with new latitude and longitude data
// function updateGraph() {
//     Plotly.newPlot(graph, [{
//         // x: latitudes,
//         x: timeList,
//         y: longitudes,
//         mode: 'lines+markers',
//         type: 'scatter',
//         name: 'Drone Path'
//     }], layout, config);
// }

// // Update data every second
// // setInterval(simulateDataUpdate, 1000);


// function updateDronePosition() {
//     fetch('/get_drone_coordinates')
//     .then(response => response.json())
//     .then(data => {
//         // droneMarker.setLatLng([data.lat, data.lng]);
//         // moveDroneTo(data.lat, data.lng);
//         // Simulate random latitude and longitude values
//         var latitude = data.lat;
//         var longitude = data.lng;
        
//         // Add new data points to arrays
//         latitudes.push(latitude);
//         longitudes.push(longitude);

//         timeList.push(Date.now())
        
//         // Update the graph
//         updateGraph();

//     })
//     .catch(error => {
//         console.error('Error fething drone coordinates: ', error);
//     });

    

//     // Schedule the next update
//     // setTimeout(updateDronePosition, 10000); //Udate every 1 second
// }

// setInterval(updateDronePosition, 1000);
