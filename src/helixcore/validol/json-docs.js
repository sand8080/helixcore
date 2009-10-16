function showHideAll(ids) {
    var elems = ids.map(function(id) { return document.getElementById(id); });
    var status = elems.every(function(el) { return el.style.display == 'block'; }) ? 'none' : 'block';
    elems.forEach(function(el) { el.style.display = status; });
}
function showHide(id) {
    var el = document.getElementById(id);
    el.style.display = (el.style.display == 'block' ? 'none' : 'block');
}