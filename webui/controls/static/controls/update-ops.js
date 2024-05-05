const updateSocket = new WebSocket('ws://'+ window.location.host + '/ws/api/update/');

window.addEventListener('beforeunload', function() {
    updateSocket.close();
});

updateSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.command === 'prepare_update') {
        var popup = document.getElementById("update-popup");
        var success_buttons = document.getElementById("success-buttons");
        var error_buttons = document.getElementById("error-buttons");
        popup.style.display = "block";
        if (data.signal !== '200') {
            document.querySelector('#popup-title').innerHTML = 'Download Failed';
            success_buttons.style.display = "none";
            error_buttons.style.display = "block";
        }
    }
};

function sendUpdateCommand(command) {
    if (command === 'prepare_update') { // Play animation
        var download_button = document.getElementsByClassName("download-button")
        download_button.disabled = true;
        download_button.innerHTML = "Downloading...";
        download_button.classList.add("loading");
    }
    updateSocket.send(JSON.stringify({
        'message': command
    }));
}