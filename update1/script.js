document.addEventListener('DOMContentLoaded', () => {

  // NAV MENU DROPDOWN
  const navMenu = document.getElementById('navMenu');
  const userContainer = document.getElementById('userContainer');
  const userDropdown = document.getElementById('userDropdown');

  function toggleMenu() {
    navMenu?.classList.toggle('show');
  }

  userContainer?.addEventListener('click', () => {
    const isShown = userDropdown?.classList.contains('show');
    userDropdown?.classList.toggle('show');
    userContainer.setAttribute('aria-expanded', !isShown);
  });

  document.addEventListener('click', (e) => {
    if (!userContainer?.contains(e.target)) {
      userDropdown?.classList.remove('show');
      userContainer?.setAttribute('aria-expanded', 'false');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      userDropdown?.classList.remove('show');
      userContainer?.setAttribute('aria-expanded', 'false');
      userContainer?.focus();
    }
  });


  // IMAGE SLIDER
  const slides = document.querySelectorAll('.slide');
  let currentSlide = 0;
  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
  }
  setInterval(() => {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }, 4000);


  // BACK TO TOP BUTTON
  const backToTopButton = document.getElementById("backToTop");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      backToTopButton.style.display = "block";
    } else {
      backToTopButton.style.display = "none";
    }
  });

  backToTopButton.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });


  // BRA SIZE CALCULATOR
  const braForm = document.getElementById('bra-size-form');
  if (braForm) {
    braForm.addEventListener('submit', function(event) {
      event.preventDefault();
      const underbust = parseFloat(document.getElementById('underbust').value);
      const overbust = parseFloat(document.getElementById('overbust').value);

      if (isNaN(underbust) || isNaN(overbust)) {
        alert('Please enter valid numbers for both measurements.');
        return;
      }

      const bandSize = Math.floor(underbust) + (Math.floor(underbust) % 2 === 0 ? 2 : 1);
      const cupDifference = overbust - underbust;
      let cupSize = '';

      if (cupDifference < 1) cupSize = 'A';
      else if (cupDifference < 2) cupSize = 'B';
      else if (cupDifference < 3) cupSize = 'C';
      else if (cupDifference < 4) cupSize = 'D';
      else if (cupDifference < 5) cupSize = 'DD';
      else if (cupDifference < 6) cupSize = 'E';
      else if (cupDifference < 7) cupSize = 'F';
      else if (cupDifference < 8) cupSize = 'G';
      else cupSize = 'H';

      const result = document.getElementById('result');
      result.textContent = `Your bra size is ${bandSize}${cupSize}`;
    });
  }


  // BODY TYPE FORM
  const bodyForm = document.getElementById('bodyTypeForm');
  if (bodyForm) {
    bodyForm.addEventListener('submit', function(e) {
      e.preventDefault();

      const bust = parseFloat(document.getElementById('bust').value);
      const waist = parseFloat(document.getElementById('waist').value);
      const hips = parseFloat(document.getElementById('hips').value);

      if (isNaN(bust) || isNaN(waist) || isNaN(hips)) {
        alert('Please enter valid numbers.');
        return;
      }

      const bodyType = calculateBodyType(bust, waist, hips);
      document.getElementById('result').textContent = `Your body type is: ${bodyType}`;
    });
  }

  function calculateBodyType(bust, waist, hips) {
    if (bust > hips && bust > waist) return 'Inverted Triangle';
    else if (hips > bust && hips > waist) return 'Pear';
    else if (bust === hips && waist < bust) return 'Hourglass';
    else if (bust === waist && waist === hips) return 'Rectangle';
    else if (waist > bust && waist > hips) return 'Apple';
    else return 'Undefined';
  }


  // Load header and footer
  fetch('header.html')
    .then(response => response.text())
    .then(data => document.getElementById('header').innerHTML = data);

  fetch('footer.html')
    .then(response => response.text())
    .then(data => document.getElementById('footer').innerHTML = data);

});


