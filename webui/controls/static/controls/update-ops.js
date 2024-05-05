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

        var popup_title = document.getElementById('popup-title')
        var popup_message = document.getElementById("popup-message");
        var popup_message_h2 = popup_message.querySelector('h2');
        var popup_message_p = popup_message.querySelector('p');
        popup.style.display = "block";
        if (data.signal === '200') {
            popup_title.innerHTML = 'Download Complete';
            success_buttons.style.display = "block";
            error_buttons.style.display = "none";
        } else {
            popup_title.innerHTML = 'Download Failed';
            popup_message_h2.innerHTML = 'Signal: ' + data.signal;
            popup_message_p.innerHTML = 'Message: ' + data.message;
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
        download_button.classList.add("loading");
    }
    updateSocket.send(JSON.stringify({
        'message': command
    }));
};