window.onload = function() {
    var x = document.getElementsByClassName("help-text");
    for (var i = 0; i < x.length; i++) {
        x[i].style = "display: none;";
    }
}

function toggleHelp(a) {
    var x = document.getElementById(a);
    if (x.style.display === "block") {
        x.style = "display: none;"
    } else {
        x.style = "display: block;"
  }
}