document.addEventListener("DOMContentLoaded", () => {
  // NAV MENU TOGGLE
  const navMenu = document.getElementById("navMenu");
  const menuToggle = document.getElementById("menuToggle");
  const userContainer = document.getElementById("userContainer");
  const userDropdown = document.getElementById("userDropdown");

  // Toggle navigation menu
  function toggleNavMenu() {
    navMenu.classList.toggle("show");
    const isExpanded = navMenu.classList.contains("show");
    menuToggle.setAttribute("aria-expanded", isExpanded);

    // Close user dropdown when nav menu opens
    if (isExpanded) {
      userDropdown.classList.remove("show");
      userContainer.setAttribute("aria-expanded", "false");
    }
  }

  // Toggle user dropdown
  function toggleUserDropdown() {
    userDropdown.classList.toggle("show");
    const isExpanded = userDropdown.classList.contains("show");
    userContainer.setAttribute("aria-expanded", isExpanded);

    // Close nav menu when user dropdown opens
    if (isExpanded) {
      navMenu.classList.remove("show");
      menuToggle.setAttribute("aria-expanded", "false");
    }
  }

  // Event listeners
  if (menuToggle) {
    menuToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleNavMenu();
    });
  }

  if (userContainer) {
    userContainer.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleUserDropdown();
    });
  }

  // Close menus when clicking outside
  document.addEventListener("click", (e) => {
    if (userContainer && !userContainer.contains(e.target)) {
      userDropdown.classList.remove("show");
      userContainer.setAttribute("aria-expanded", "false");
    }
    if (
      menuToggle &&
      navMenu &&
      !menuToggle.contains(e.target) &&
      !navMenu.contains(e.target)
    ) {
      navMenu.classList.remove("show");
      menuToggle.setAttribute("aria-expanded", "false");
    }
  });

  // Close menus with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (userDropdown?.classList.contains("show")) {
        userDropdown.classList.remove("show");
        userContainer.setAttribute("aria-expanded", "false");
      }
      if (navMenu) {
        navMenu.classList.remove("show");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    }
  });

  // IMAGE SLIDER
  const slides = document.querySelectorAll(".slide");
  if (slides.length > 0) {
    let currentSlide = 0;

    function showSlide(index) {
      slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === index);
      });
    }

    // Initialize first slide
    showSlide(0);

    // Auto-rotate slides
    let slideInterval = setInterval(() => {
      currentSlide = (currentSlide + 1) % slides.length;
      showSlide(currentSlide);
    }, 4000);

    // Pause on hover
    const slider = document.querySelector(".slider");
    if (slider) {
      slider.addEventListener("mouseenter", () => clearInterval(slideInterval));
      slider.addEventListener("mouseleave", () => {
        slideInterval = setInterval(() => {
          currentSlide = (currentSlide + 1) % slides.length;
          showSlide(currentSlide);
        }, 4000);
      });
    }
  }

  // BACK TO TOP BUTTON
  const backToTopButton = document.getElementById("backToTop");
  if (backToTopButton) {
    window.addEventListener("scroll", () => {
      backToTopButton.style.display = window.scrollY > 300 ? "block" : "none";
    });

    backToTopButton.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // BRA SIZE CALCULATOR (Removed nested DOMContentLoaded)
 const form = document.getElementById("bra-size-form");
if (form) {
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const underbust = parseFloat(document.getElementById("underbust").value);
    const overbust = parseFloat(document.getElementById("overbust").value);

    if (isNaN(underbust) || isNaN(overbust)) {
      alert("Please enter valid numbers for both measurements.");
      return;
    }

    // Limit values to a realistic range (e.g., 24–60 inches)
    if (
      underbust < 24 || underbust > 60 ||
      overbust < 24 || overbust > 60
    ) {
      alert("Please enter values between 24 and 60 inches.");
      return;
    }

    const bandSize =
      Math.floor(underbust) + (Math.floor(underbust) % 2 === 0 ? 2 : 1);
    const cupDifference = overbust - underbust;
    let cupSize = "";

    if (cupDifference < 1) cupSize = "A";
    else if (cupDifference < 2) cupSize = "B";
    else if (cupDifference < 3) cupSize = "C";
    else if (cupDifference < 4) cupSize = "D";
    else if (cupDifference < 5) cupSize = "DD";
    else if (cupDifference < 6) cupSize = "E";
    else if (cupDifference < 7) cupSize = "F";
    else if (cupDifference < 8) cupSize = "G";
    else cupSize = "H";

    const result = document.getElementById("result");
    result.textContent = `Your bra size is ${bandSize}${cupSize}`;
  });
}


  // BODY TYPE CALCULATOR
  const bodyForm = document.getElementById("bodyTypeForm");
  if (bodyForm) {
    bodyForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const bust = parseFloat(document.getElementById("bust").value);
      const waist = parseFloat(document.getElementById("waist").value);
      const hips = parseFloat(document.getElementById("hips").value);

      if (isNaN(bust) || isNaN(waist) || isNaN(hips)) {
        alert("Please enter valid numbers.");
        return;
      }

      const bodyType = calculateBodyType(bust, waist, hips);
      const result = document.getElementById("result");
      if (result) {
        result.textContent = `Your body type is: ${bodyType}`;
      }
    });
  }

  function calculateBodyType(bust, waist, hips) {
    if (bust > hips && bust > waist) return "Inverted Triangle";
    if (hips > bust && hips > waist) return "Pear";
    if (Math.abs(bust - hips) <= 1 && waist < bust) return "Hourglass";
    if (Math.abs(bust - waist) <= 1 && Math.abs(waist - hips) <= 1)
      return "Rectangle";
    if (waist > bust && waist > hips) return "Apple";
    return "Undefined";
  }
}); // Only one closing brace for the main DOMContentLoaded
