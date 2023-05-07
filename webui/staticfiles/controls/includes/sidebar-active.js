// if a link item is selected, add the class "active" to the parent li
// element. This is used to highlight the current page in the sidebar
(function() {
    var path = window.location.pathname;
    var links = document.querySelectorAll('li a');
    for (var i = 0; i < links.length; i++) {
        var link = links[i];
        if (link.pathname === path) {
            link.parentNode.classList.add('active');
        }
    }
})();