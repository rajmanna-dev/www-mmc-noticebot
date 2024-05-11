document.addEventListener('DOMContentLoaded', function () {
  var navLinks = document.querySelectorAll('nav .nav--link');

  navLinks.forEach(function (each) {
    each.addEventListener('click', smoothScroll);
  });

  function smoothScroll(e) {
    e.preventDefault();
    var targetId = this.getAttribute('href');
    var targetPosition = document.querySelector(targetId).offsetTop;
    var startPosition = window.pageYOffset;
    var distance = targetPosition - startPosition;
    var startTime = null;

    function animation(currentTime) {
      if (startTime === null) startTime = currentTime;
      var timeElapsed = currentTime - startTime;
      var run = ease(timeElapsed, startPosition, distance, 1000);
      window.scrollTo(0, run);
      if (timeElapsed < 1000) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
      t /= d / 2;
      if (t < 1) return (c / 2) * t * t + b;
      t--;
      return (-c / 2) * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
  }
});
