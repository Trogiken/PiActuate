const doorSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/engine/door/'
  );

document.addEventListener('DOMContentLoaded', function() {
    window.setInterval(getStatus, 1000);
  });
function getStatus() {
  doorSocket.send(JSON.stringify({
        'message': 'get_status'
    }));
}
doorSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.signal === '200') {
      document.querySelector('#status_text').innerHTML = data.message;
    } else {
      document.querySelector('#status_text').innerHTML = 'unknown';
    }
};

// function that accepts a variable that sends 'open' or 'close' to the server. Also show loading animation while waiting for response.
function sendDoorCommand(command) {
  showLoading();
  doorSocket.send(JSON.stringify({
      'message': command
  }));
}
// on message from server, if response is 200, hide loading animation, if response is 400, show error message.
doorSocket.onmessage = function(e) {
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


const loadingContainer = document.getElementById('loading-container');
const loadingText = document.getElementById('loading-text');
function showLoading() {
  loadingContainer.style.display = 'block';
  loadingText.style.display = 'block';
}
function hideLoading() {
  loadingContainer.style.display = 'none';
  loadingText.style.display = 'none';
}