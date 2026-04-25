// Cosmos Game Cafe - Ana JS Dosyası
// Todo: İleride filtreleme eklenecek.

/* --- 1. NAVBAR İŞLEMLERİ --- */
const nav = document.querySelector('.nav');
const toggle = document.querySelector('.nav__toggle');
const menu = document.querySelector('.nav__menu');

// Aktif sayfayı bulup menüde işaretle
const links = document.querySelectorAll('.nav__link');
const currentPage = window.location.pathname.split('/').pop() || 'index.html';

links.forEach(link => {
  const href = link.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    link.classList.add('nav__link--active');
  }
});

// Sayfa kaydırılınca menünün arkaplanını karart
window.addEventListener('scroll', () => {
  if (window.scrollY > 20) {
    nav.classList.add('nav--scrolled');
  } else {
    nav.classList.remove('nav--scrolled');
  }
}, { passive: true });

// Sayfa ilk yüklendiğinde ortalardaysak diye kontrol
if (window.scrollY > 20 && nav) {
  nav.classList.add('nav--scrolled');
}

// Mobil Hamburger Menü
if (toggle && menu) {
  toggle.addEventListener('click', () => {
    toggle.classList.toggle('nav__toggle--open');
    menu.classList.toggle('nav__menu--open');
  });

  // Linke tıklayınca menüyü kapat
  menu.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('nav__toggle--open');
      menu.classList.remove('nav__menu--open');
    });
  });
}


/* --- 2. SCROLL ANIMASYONLARI (Aşağı indikçe çıkan elemanlar) --- */
const revealEls = document.querySelectorAll('.reveal');

if (revealEls.length > 0) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('reveal--visible');
        observer.unobserve(entry.target); // Bir kere çalışsın yeter
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => observer.observe(el));
}


/* --- 3. MENÜ HOVER EFEKTİ --- */
const menuItems = document.querySelectorAll('.menu-item');
menuItems.forEach(item => {
  item.addEventListener('mouseenter', () => {
    item.style.paddingLeft = '1.75rem';
  });
  item.addEventListener('mouseleave', () => {
    item.style.paddingLeft = '';
  });
});


/* --- 4. RAKAM SAYDIRMA EFEKTİ (Hero kısmındaki istatistikler) --- */
const counters = document.querySelectorAll('[data-count]');

if (counters.length > 0) {
  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-count'), 10);
    const duration = 1500; // 1.5 saniye
    const start = performance.now();

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);

      // Yumuşak duruş için basit easing
      const eased = 1 - Math.pow(1 - progress, 2);
      const current = Math.round(eased * target);

      el.textContent = current + (el.getAttribute('data-suffix') || '');

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  // Ekrana girince saydırmaya başla
  const counterObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => counterObserver.observe(counter));
}