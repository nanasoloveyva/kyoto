let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");

  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}

  // Убираем видимость у всех слайдов и активный класс
  for (i = 0; i < slides.length; i++) {
    slides[i].style.opacity = "0";
    slides[i].style.display = "none";
    slides[i].classList.remove("active");
  }

  // Отображаем текущий слайд и плавно его проявляем
  slides[slideIndex - 1].style.display = "block";
  setTimeout(() => { 
    slides[slideIndex - 1].style.opacity = "1"; 
  }, 50); // Небольшая задержка для более плавного эффекта
  slides[slideIndex - 1].classList.add("active");

  // Сбрасываем активный класс для точек и добавляем его к текущей точке
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  dots[slideIndex - 1].className += " active";
}


document.addEventListener("DOMContentLoaded", function() {
  // Код для открытия и закрытия выпадающего меню
  function toggleDropdown(event) {
      event.preventDefault();
      event.stopPropagation(); // Останавливаем распространение клика, чтобы внешний обработчик не сработал
      const dropdownMenu = event.target.nextElementSibling;
      dropdownMenu.classList.toggle('active');
  }

  // Закрытие меню при клике вне его
  document.addEventListener('click', function(event) {
      const isClickInside = event.target.closest('.dropdown');
      if (!isClickInside) {
          document.querySelectorAll('.dropdown-menu').forEach(menu => {
              menu.classList.remove('active');
          });
      }
  });

  // Добавляем обработчик для кнопки "ЛИЧНЫЙ КАБИНЕТ"
  const personalMenuItem = document.querySelector('.dropdown a');
  personalMenuItem.addEventListener('click', toggleDropdown);
});

