function toggleHelp(a) {
    var x = document.getElementById(a);
    if (x.style.display === "block") {
        x.style.display = "none";
    } else {
        x.style.display = "block";
  }
  // hack to make sure the background reaches the bottom of the page when too many help-texts are shown
  document.getElementsByTagName("body")[0].style = "height: 100%;"
}