// var map = L.map('map').setView([-35.363263, 149.1652378], 19);
// var map = L.map('map').setView([-35.363263, 150.1652378], 19);


/*
------------------------------
INITIALIZE MAP:
------------------------------
*/

var map = L.map('map').setView([init_lat, init_lng], 19);

staticUrl = document.getElementById('map').dataset.staticUrl

// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.{ext}', {
// 	minZoom: 0,
// 	maxZoom: 20,
// 	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
// 	ext: 'png'
// }).addTo(map);

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
}).addTo(map);


/*
------------------------------
INITIALIZE MAP MARKERS:
------------------------------
*/

var droneMarker;
var droneMarker2
;
var userMarker;
var takeoffMarker;

var takeoffIcon = L.icon({
    iconUrl: './static/images/takeoff_img.png',
    iconSize: [25, 25],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
})

var droneIcon = L.icon({
    // iconUrl: staticUrl + 'images/drone.png',
    iconUrl: './static/images/camera-drone.png',
    // iconUrl: '{{ url_for("static", filename="images/drone.png") }}',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
});

/*
------------------------------
INITIALIZE WAYPOINTS VARIABLES:
------------------------------
*/

var waypoints = [];
var lines = [];
var waypointsSent = false;

var latitudes = [];
var longitudes = [];


/*
------------------------------
WAIT FOR EVERYTHING TO LOAD:
------------------------------
*/
document.addEventListener('DOMContentLoaded', function() {

    /* ------------------------------
    GET THE GRAPH CANVAS FROM HTML
    ------------------------------*/


    map.whenReady(function () {

        /*
        ------------------------------
        INITIATE MARKERS ON MAP:
        ------------------------------
        */

        takeoffMarker = L.marker([init_lat, init_lng], {icon: takeoffIcon}).addTo(map);

        droneMarker = L.marker([init_lat, init_lng], { icon: droneIcon }).addTo(map);

        /*
        ------------------------------
        CALL FUNCION TO UPDATE THE LOCATION OF THE DRONE MARKER
        ------------------------------
        */

        updateDronePosition();

        /* ------------------------------
        ADDING MARKERS AND WAYPOINTS ON MAP:
        ------------------------------*/

        var drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
    
        var drawControl = new L.Control.Draw({
            edit: {
                featureGroup: drawnItems
            },
            draw: {
                marker: true,
                polygon: false,
                circle: false,
                rectangle: false,
                polyline: false
            }
        });
    
        map.addControl(drawControl);

        // ---------------------------
        // MOVE DRONE ON MAP CLICK

        map.on('draw:created', function(e) {
            var type = e.layerType,
            layer = e.layer;

            if (type == 'marker') {
                userMarker = layer.getLatLng();
                console.log("User maker placed here: ", userMarker);

                sendLocationToDrone(userMarker);
            };

            drawnItems.addLayer(layer);
        });


        // ---------------------------------
        // CREATE A SQUARE FOR DRONE TO MOVE

        map.on('click', function(e) {
            var waypoint = L.marker(e.latlng).addTo(map);
            waypoints.push(waypoint);

            if (waypoints.length === 4) {
                drawSquare();
            }
        })
    
    });
    
});

/* ------------------------------
FUNCTION TO MOVE DRONE MARKER ON MAP:
------------------------------*/

var previousLatLng = L.latLng(init_lat, init_lng);
var droneMoveIndex = 0;

function moveDroneTo() {

    if (latitudes.length === 0 || longitudes.length === 0){
        return;
    }

    var startLatLng = previousLatLng;
    // var endLatLng = L.latLng(lat, lng);
    var endLatLng = L.latLng(latitudes[droneMoveIndex], longitudes[droneMoveIndex]);

    var duration = 1000; // Animation duration in milliseconds 1000

    var startTime = Date.now();
    var animate = function() {
        var elapsedTime = Date.now() - startTime;
        var fraction = Math.min(elapsedTime / duration, 1); // Clamp fraction to 1

        if (fraction < 1) {
            var interpolatedLatLng = L.latLng(
                startLatLng.lat + fraction * (endLatLng.lat - startLatLng.lat),
                startLatLng.lng + fraction * (endLatLng.lng - startLatLng.lng)
            );

            droneMarker.setLatLng(interpolatedLatLng);
            requestAnimationFrame(animate);
            
        } else {
            droneMarker.setLatLng(endLatLng);
            previousLatLng = endLatLng;

            // Move to next set of coords if available
            droneMoveIndex++;
            if (droneMoveIndex < latitudes.length) {
                startLatLng = endLatLng;
                endLatLng = L.latLng(latitudes[droneMoveIndex], longitudes[droneMoveIndex]);
                startTime = Date.now();
                requestAnimationFrame(animate);
            }
        }
    };

    animate();
}


/* ------------------------------
RECEIVE DRONE COORDS
FROM FLASK:
------------------------------*/

function updateDronePosition() {
    
    fetch('/get_drone_coordinates')
    .then(response => response.json())
    .then(data => {
        droneMarker.setLatLng([data.lat, data.lng]);
        // moveDroneTo(data.lat, data.lng);

        latitudes.push(data.lat);
        longitudes.push(data.lng);

        // moveDroneTo(data.lat, data.lng);
    })
    .catch(error => {
        console.error('Error fething drone coordinates: ', error);
    });

    // Schedule the next update
    setTimeout(updateDronePosition, 1000); //Udate every 1 second
}


/* ------------------------------
SEND USER CLICK COORDS
TO FLASK SERVER TO MOVE DRONE:
------------------------------*/

function sendLocationToDrone(location) {
    fetch('/move_drone', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error sending location to server: ', error);
    });
}


/* ------------------------------
SEND THE LIST OF WAYPOINTS TO
FLASK SERVER:
------------------------------*/

function sendMarkerListToDrone(markerList) {
    fetch('/send_marker_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ markers: markerList }),
    })
    .then(data => {
        console.log("Server response: ", data);
    })
    .catch(error => {
        console.error('Error sending marker list to server: ', error);
    });

    console.log('Sent the following from the SENDMARKER FUNC: ', markerList);

    // Empty the list
    markerList = [];
    // console.log("Marker list emptied: ", userMarker);
}

/* ------------------------------
DRAW LINES BETWEEN USER'S WAYPOINTS
AND SEND COORDS LIST TO SERVER
------------------------------*/

function drawSquare() {
    var latlngs = waypoints.map(function(waypoint) {
        return waypoint.getLatLng();
    });

    // sendMarkerListToDrone(latlngs);
    
    latlngs.push(latlngs[0]); // Close the square

    var line = L.polyline(latlngs, {color: 'red'}).addTo(map);
    lines.push(line);

    document.getElementById('clearButton').addEventListener('click', function(event) {
        clearWaypoints();
    });

    document.getElementById('navSendButton').addEventListener('click', function(event) {
        if (waypoints.length !== 0 && !waypointsSent) {
            console.log("length ", waypoints.length)
            sendMarkerListToDrone(latlngs);
            waypointsSent = true;

        }

        else if (waypointsSent) console.log("Already sent those waypoints!");

        else console.log("No waypoints provided...");
    });

    
}


/* ------------------------------
CLEAR USER'S WAYPOINTS 
------------------------------*/

function clearWaypoints() {
    waypoints.forEach(function(waypoint) {
        map.removeLayer(waypoint);
    });
    waypoints = [];

    lines.forEach(function(line) {
        map.removeLayer(line);
    });
    lines = []

    waypointsSent = false;
}