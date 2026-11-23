document.getElementById("takeoffButton").addEventListener("click", function(event) {
    event.preventDefault(); // Prevent default form submission
    console.log("takeoff button presses..........")

    // Serialize form data
    var formData = new FormData(document.getElementById("takeoffForm"));

    // Send form data to server using AJAX
    fetch("/process_takeoff", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log("Takeoff command sent successfully");
        } else {
            console.error("Error sending takeoff command");
        }
    })
    .then(data => {
        console.log(data.message); // Log server response
        console.log("Altitude: ", data.altitude); // Log altitude received from server
    })
    .catch(error => {
        console.error("Error: ", error);
    });
});


// ------------------------- ALTITUDE FIELD -------------------------


$('#increaseAlt').click(function() {
    changeAltitude('increase');
});

$('#decreaseAlt').click(function() {
    changeAltitude('decrease');
});

$('#increaseRot').click(function() {
    changeAltitude('increaseRot');
});

$('#decreaseRot').click(function() {
    changeAltitude('decreaseRot');
});

$('#forward').click(function() {
    changeAltitude('forward');
});

$('#backward').click(function() {
    changeAltitude('backward');
});

$('#right').click(function() {
    changeAltitude('right');
});

$('#left').click(function() {
    changeAltitude('left');
});


function changeAltitude(action) {
    // var alt_amount = new FormData(document.getElementById('altForm'));
    var alt_amount = $('#alt_amount').val();
    

    $.ajax({
        url: '/process_altData',
        type: 'POST',
        data: { action: action, alt_amount: alt_amount },
        success: function(response) {
            console.log(response, "alt send from funcion");
        },
        error: function(xhr, status, error) {
            console.error('Error', error);
        }
    });
}


// ------------------------- ARM DISARM FIELD -------------------------


$('#armButton').click(function() {
    console.log("Arm Button Clicked");
    armDisarm("arm");
});

$('#disarmButton').click(function() {
    console.log("Disarm Button Clicked");
    armDisarm("disarm");
});

function armDisarm(action) {
    $.ajax({
        url: '/process_arm_disarm',
        type: 'POST',
        data: { action: action },
        success: function(response) {
            console.log(response, action + " command sent")
        },
        error: function(xhr, status, error) {
            console.error("Error", error);
        }
    });
}