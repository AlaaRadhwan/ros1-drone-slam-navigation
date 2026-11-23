function sendWaypoints() {
    fetch('/send_waypoints', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.text())
    .then(data => {
        console.log('Response from server: '+ data)
    })
    .catch(error => {
        console.error('Error: ', error);
    });
}