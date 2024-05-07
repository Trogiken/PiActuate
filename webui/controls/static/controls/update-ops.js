const updateSocket = new WebSocket('ws://'+ window.location.host + '/ws/api/update/');

window.addEventListener('beforeunload', function() {
    updateSocket.close();
});

updateSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.command === 'prepare_update') {
        var update_info = document.getElementById("update-info"); // update-info container
        var download_button = document.getElementById("download-button");
        var info_h1 = update_info.querySelector('h1');
        var info_h2 = update_info.querySelector('h2');
        var info_p = update_info.querySelector('p');
        var success_buttons = document.getElementById("success-buttons");
        var error_buttons = document.getElementById("error-buttons");

        download_button.style.display = 'none';
        if (data.signal === '200') {
            info_h1.innerHTML = 'Complete!';
            info_p.innerHTML = "Downloaded the latest update";
            success_buttons.style.display = "block";
            error_buttons.style.display = "none";
        } else {
            info_h1.innerHTML = 'Download Failed';
            info_h2.innerHTML = 'Signal: ' + data.signal;
            info_p.innerHTML = data.message;
            success_buttons.style.display = "none";
            error_buttons.style.display = "block";
        }
    }
};

function sendUpdateCommand(command) {
    if (command === 'prepare_update') { // Play animation
        var download_button = document.getElementById("download-button");
        download_button.disabled = true;
        download_button.innerHTML = "Downloading...";
        download_button.classList.add("disabled");
        download_button.classList.add("loading");
    }
    updateSocket.send(JSON.stringify({
        'message': command
    }));
};