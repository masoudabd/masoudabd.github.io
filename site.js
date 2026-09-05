/* Focus switching.
 * index.html is pre-rendered with the default focus visible. If the URL carries
 * ?focus=<key> (e.g. ?focus=research) and that key exists, reveal that variant's
 * blocks, hide the others, and update the title / description / résumé link.
 */
(function () {
  var root = document.documentElement;
  var valid = (root.getAttribute('data-variants') || '').split(',');
  var current = root.getAttribute('data-focus');
  var focus = new URLSearchParams(window.location.search).get('focus');
  if (!focus) return;
  focus = focus.toLowerCase();
  if (valid.indexOf(focus) === -1 || focus === current) return;

  var meta = {};
  try {
    meta = JSON.parse(document.getElementById('variants-meta').textContent)[focus] || {};
  } catch (e) { /* keep defaults */ }

  root.setAttribute('data-focus', focus);
  var blocks = document.querySelectorAll('[data-variant]');
  for (var i = 0; i < blocks.length; i++) {
    blocks[i].hidden = blocks[i].getAttribute('data-variant') !== focus;
  }
  if (meta.title) document.title = meta.title;
  var desc = document.querySelector('meta[name="description"]');
  if (desc && meta.description) desc.setAttribute('content', meta.description);
  if (meta.resume) {
    var links = document.querySelectorAll('a[data-resume]');
    for (var j = 0; j < links.length; j++) links[j].setAttribute('href', meta.resume);
  }
})();
