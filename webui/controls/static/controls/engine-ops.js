const statusSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/dashboard/status/'
  );
document.addEventListener('DOMContentLoaded', function() {
    window.setInterval(getStatus, 1000);
  });
function getStatus() {
    statusSocket.send(JSON.stringify({
        'message': 'get_status'
    }));
}
statusSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.querySelector('#status_text').innerHTML = data.message;
};


const movementSocket = new WebSocket(
  'ws://'
  + window.location.host
  + '/ws/door/movement/'
);
// function that accepts a variable that sends 'open' or 'close' to the server. Also show loading animation while waiting for response.
function sendDoorCommand(command) {
  showLoading();
  movementSocket.send(JSON.stringify({
      'message': command
  }));
}
// on message from server, if response is 200, hide loading animation, if response is 400, show error message.
movementSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  if (data.signal === '200') {
      document.querySelector('#loading-text').innerHTML = 'Success: ' + data.message;
      setTimeout(hideLoading, 2000);
      hideLoading();
  } else {
      document.querySelector('#loading-text').innerHTML = 'Error: ' + data.message;
      setTimeout(hideLoading, 2000);
      hideLoading();
  }
}


const loadingOverlay = document.getElementById('#loading-container');
const loadingText = document.getElementById('loading-text');
function showLoading() {
  loadingOverlay.style.display = 'block';
  loadingText.style.display = 'block';
}
function hideLoading() {
  loadingOverlay.style.display = 'none';
  loadingText.style.display = 'none';
}