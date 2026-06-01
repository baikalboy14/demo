(function () {
    var slides = document.querySelectorAll('.slider-img');
    var prevBtn = document.getElementById('sliderPrev');
    var nextBtn = document.getElementById('sliderNext');

    if (!slides.length || !prevBtn || !nextBtn) {
        return;
    }

    var num = 0;

    function showSlide(n) {
        slides[num].classList.remove('active');
        num = (n + slides.length) % slides.length;
        slides[num].classList.add('active');
    }

    prevBtn.addEventListener('click', function () {
        showSlide(num - 1);
    });

    nextBtn.addEventListener('click', function () {
        showSlide(num + 1);
    });
})();
