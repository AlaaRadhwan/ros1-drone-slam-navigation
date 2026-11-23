function handleButtonClick(buttonId) {
    fetch("/landing_process", {
        method: "POST",
        body: JSON.stringify({ action: buttonId}), // Send button ID as JSON data
        headers: {
            'Content-Type': 'application/json' // Set the content type to JSON
        }
    })
    .then(response => {
        if (response.ok) {
            console.log("landing command sent successfully");
        } else {
            throw new Error('Failed to send command');
        }
    })
    .then(data => {
        console.log(data.message); // Log server response
    })
    .catch(error => {
        console.error("Error: ", error);
    });
}

document.querySelectorAll('.control-buttons[data-button-id="land"], .control-buttons[data-button-id="rtl"]').forEach(button => {
    button.addEventListener('click', function() {
        handleButtonClick(this.dataset.buttonId); // Pass the button ID to the handle function
    });
});