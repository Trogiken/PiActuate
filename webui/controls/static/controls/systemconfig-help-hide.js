function toggleHelp(a) {
    var x = document.getElementById(a);
    if (x.style.display === "inline-block") {
        x.style = "display: none;"
    } else {
        x.style = "display: inline-block;"
  }
}