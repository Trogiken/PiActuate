const statusSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/dashboard/status/'
  );
  
document.onload = function() {
    window.setInterval(getStatus, 1000);
};

function getStatus() {
    statusSocket.send(JSON.stringify({
        'message': 'get_status'
    }));
}

statusSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#status_text').innerHTML = data.message;
};