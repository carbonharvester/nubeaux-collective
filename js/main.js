/* ============================================
   NUBEAUX COLLECTIVE — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all modules
  initHeader();
  initMobileMenu();
  initScrollReveal();
  initSmoothScroll();
  initLightbox();
});

/* ----- Header Scroll Effect ----- */
function initHeader() {
  const header = document.querySelector('.header');
  if (!header) return;

  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
  }, { passive: true });
}

/* ----- Mobile Menu ----- */
function initMobileMenu() {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.mobile-menu');
  const links = document.querySelectorAll('.mobile-menu a');

  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    menu.classList.toggle('active');
    toggle.classList.toggle('active');
    document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
  });

  links.forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.remove('active');
      toggle.classList.remove('active');
      document.body.style.overflow = '';
    });
  });
}

/* ----- Scroll Reveal Animation ----- */
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');

  if (!reveals.length) return;

  const revealOnScroll = () => {
    reveals.forEach(element => {
      const windowHeight = window.innerHeight;
      const elementTop = element.getBoundingClientRect().top;
      const revealPoint = 100;

      if (elementTop < windowHeight - revealPoint) {
        element.classList.add('active');
      }
    });
  };

  window.addEventListener('scroll', revealOnScroll, { passive: true });
  revealOnScroll(); // Check on load
}

/* ----- Smooth Scroll for Anchor Links ----- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    });
  });
}

/* ----- Work Filter (for Work page) ----- */
function initWorkFilters() {
  const filters = document.querySelectorAll('.work-filter');
  const items = document.querySelectorAll('.work-item');

  if (!filters.length || !items.length) return;

  filters.forEach(filter => {
    filter.addEventListener('click', () => {
      // Update active state
      filters.forEach(f => f.classList.remove('active'));
      filter.classList.add('active');

      const category = filter.dataset.filter;

      items.forEach(item => {
        const itemCategories = item.dataset.category || '';
        if (category === 'all' || itemCategories.includes(category)) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });
}

/* ----- Form Validation (for Contact page) ----- */
function initContactForm() {
  const form = document.querySelector('.contact-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    // Basic validation
    const name = form.querySelector('[name="name"]');
    const email = form.querySelector('[name="email"]');
    const message = form.querySelector('[name="message"]');

    let valid = true;

    [name, email, message].forEach(field => {
      if (!field.value.trim()) {
        field.style.borderColor = '#c00';
        valid = false;
      } else {
        field.style.borderColor = '';
      }
    });

    if (valid) {
      // Here you would normally send the form data
      console.log('Form submitted');
      form.reset();
      alert('Thank you for your message. We will be in touch shortly.');
    }
  });
}

// Initialize page-specific features
if (document.querySelector('.work-filter')) {
  initWorkFilters();
}

if (document.querySelector('.contact-form')) {
  initContactForm();
}

/* ----- Lightbox Gallery ----- */
function initLightbox() {
  // Select gallery images from portfolio and recent work sections
  const galleryImages = document.querySelectorAll('.destination-card img, .gallery-item img');

  if (!galleryImages.length) return;

  // Create lightbox elements
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = `
    <div class="lightbox-overlay"></div>
    <div class="lightbox-container">
      <button class="lightbox-close" aria-label="Close">&times;</button>
      <button class="lightbox-prev" aria-label="Previous">&#10094;</button>
      <button class="lightbox-next" aria-label="Next">&#10095;</button>
      <div class="lightbox-content">
        <img src="" alt="Gallery image">
      </div>
      <div class="lightbox-counter"></div>
    </div>
  `;
  document.body.appendChild(lightbox);

  const overlay = lightbox.querySelector('.lightbox-overlay');
  const closeBtn = lightbox.querySelector('.lightbox-close');
  const prevBtn = lightbox.querySelector('.lightbox-prev');
  const nextBtn = lightbox.querySelector('.lightbox-next');
  const lightboxImg = lightbox.querySelector('.lightbox-content img');
  const counter = lightbox.querySelector('.lightbox-counter');

  let currentImages = [];
  let currentIndex = 0;

  // Make images clickable
  galleryImages.forEach((img, index) => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', (e) => {
      e.preventDefault();

      // Get all images in the same gallery section
      const parent = img.closest('.destinations-scroll, .gallery-grid');
      if (parent) {
        currentImages = Array.from(parent.querySelectorAll('img'));
        currentIndex = currentImages.indexOf(img);
      } else {
        currentImages = [img];
        currentIndex = 0;
      }

      openLightbox();
    });
  });

  function openLightbox() {
    updateLightboxImage();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  }

  function updateLightboxImage() {
    const img = currentImages[currentIndex];
    lightboxImg.src = img.src;
    lightboxImg.alt = img.alt || 'Gallery image';
    counter.textContent = `${currentIndex + 1} / ${currentImages.length}`;

    // Hide nav buttons if only one image
    prevBtn.style.display = currentImages.length > 1 ? '' : 'none';
    nextBtn.style.display = currentImages.length > 1 ? '' : 'none';
  }

  function nextImage() {
    currentIndex = (currentIndex + 1) % currentImages.length;
    updateLightboxImage();
  }

  function prevImage() {
    currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
    updateLightboxImage();
  }

  // Event listeners
  closeBtn.addEventListener('click', closeLightbox);
  overlay.addEventListener('click', closeLightbox);
  nextBtn.addEventListener('click', nextImage);
  prevBtn.addEventListener('click', prevImage);

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;

    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'ArrowLeft') prevImage();
  });
}
