window.twttr = (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0],
  t = window.twttr || {};
  if (d.getElementById(id)) return t;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);

  t._e = [];
  t.ready = function(f) {
    t._e.push(f);
  };

  return t;
}(document, "script", "twitter-wjs"));

window.onload = (function(){

  var x = document.getElementsByClassName("mytweet");
  var i;
  for (i = 0; i < x.length; i++) {

    var id = x[i].getAttribute("tweetID");

    twttr.widgets.createTweet(
      id, x[i],
      {
        conversation : 'none',    // or all
        cards        : 'hidden',  // or visible
        linkColor    : '#cc0000', // default is blue
        theme        : 'light'    // or dark
      })
      .then (function (el) {
        //el.contentDocument.querySelector(".footer").style.display = "none";
      });
    }
  });
