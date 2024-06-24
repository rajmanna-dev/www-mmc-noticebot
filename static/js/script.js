$(document).ready(function () {
  var navLinks = $('nav .nav--link');
  navLinks.on('click', function (e) {
    e.preventDefault();
    var targetId = $(this).attr('href');
    var targetPosition = $(targetId).offset().top;
    var startPosition = $(window).scrollTop();
    var distance = targetPosition - startPosition;
    var startTime = null;
    function animation(currentTime) {
      if (startTime === null) startTime = currentTime;
      var timeElapsed = currentTime - startTime;
      var run = ease(timeElapsed, startPosition, distance, 1000);
      $(window).scrollTop(run);
      if (timeElapsed < 1000) requestAnimationFrame(animation);
    }
    function ease(t, b, c, d) {
      t /= d / 2;
      if (t < 1) return (c / 2) * t * t + b;
      t--;
      return (-c / 2) * (t * (t - 2) - 1) + b;
    }
    requestAnimationFrame(animation);
  });
});
