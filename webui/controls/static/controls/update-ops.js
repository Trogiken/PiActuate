const updateSocket = new WebSocket('ws://'+ window.location.host + '/ws/api/update/');

window.addEventListener('beforeunload', function() {
    updateSocket.close();
});

updateSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.command === 'prepare_update') {
        var update_info = document.getElementById("update-info"); // update-info container
        var popup = document.getElementById("update-popup"); // update-popup container
        var success_buttons = document.getElementById("success-buttons");
        var error_buttons = document.getElementById("error-buttons");

        var popup_title = document.getElementById('popup-title')
        var popup_message = document.getElementById("popup-message");
        var popup_message_h2 = popup_message.querySelector('h2');
        var popup_message_p = popup_message.querySelector('p');
        update_info.style.display = "none"; // hide the update-info container so the popup takes its place
        popup.style.display = "block";
        if (data.signal === '200') {
            popup_title.innerHTML = 'Download Complete';
            success_buttons.style.display = "block";
            error_buttons.style.display = "none";
        } else {
            popup_title.innerHTML = 'Download Failed';
            popup_message_h2.innerHTML = 'Signal: ' + data.signal;
            popup_message_p.innerHTML = data.message;
            success_buttons.style.display = "none";
            error_buttons.style.display = "block";
            popup_message.style.display = "block";
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