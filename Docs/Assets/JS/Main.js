document.addEventListener('DOMContentLoaded', () => {

  // ── Scroll Progress Bar ──
  const progressBar = document.getElementById('scroll-progress');
  if (progressBar) {
    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      progressBar.style.width = docHeight > 0 ? (scrollTop / docHeight) * 100 + '%' : '0%';
    }, { passive: true });
  }

  // ── Nav scroll shadow ──
  const nav = document.querySelector('nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 16);
    }, { passive: true });
  }

  // ── Mobile Menu ──
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        navLinks.classList.remove('open');
      });
    });
  }

  // ── Language Toggle ──
  const langLinks = document.querySelectorAll('.lang-toggle a');
  langLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const lang = link.getAttribute('data-lang');
      langLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      document.body.classList.toggle('lang-tr', lang === 'tr');
      try { localStorage.setItem('agent-synapse-lang', lang); } catch (_) {}
    });
  });
  try {
    const savedLang = localStorage.getItem('agent-synapse-lang');
    if (savedLang === 'tr') {
      document.querySelector('.lang-toggle a[data-lang="tr"]')?.click();
    }
  } catch (_) {}

  // ── Theme Toggle ──
  const themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    const applyTheme = (pref) => {
      document.documentElement.classList.remove('light', 'dark');
      if (pref === 'light') document.documentElement.classList.add('light');
      else if (pref === 'dark') document.documentElement.classList.add('dark');
      themeBtn.textContent = pref === 'light' ? '\u{2600}\u{FE0F}' : pref === 'dark' ? '\u{1F319}' : '\u{1F30D}';
    };
    try {
      const saved = localStorage.getItem('agent-synapse-theme');
      if (saved) applyTheme(saved);
    } catch (_) {}
    themeBtn.addEventListener('click', () => {
      const html = document.documentElement;
      const isDark = !html.classList.contains('light');
      const next = isDark ? 'light' : 'dark';
      applyTheme(next);
      try { localStorage.setItem('agent-synapse-theme', next); } catch (_) {}
    });
  }

  // ── Animated Counters ──
  const counters = document.querySelectorAll('.stat-value');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const raw = el.textContent.replace(/[,+]/g, '');
      const target = parseInt(raw, 10);
      if (isNaN(target)) return;
      const duration = 1000;
      const startTime = performance.now();
      function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target).toLocaleString() + '+';
        if (progress < 1) requestAnimationFrame(update);
      }
      requestAnimationFrame(update);
      counterObserver.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(el => counterObserver.observe(el));

  // ── Scroll Fade-In ──
  const fadeEls = document.querySelectorAll('.fade-in');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  fadeEls.forEach(el => fadeObserver.observe(el));

  // ── FAQ Accordion ──
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.parentElement;
      const isOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });

  // ── Copy to Clipboard ──
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const pre = btn.parentElement.querySelector('pre');
      if (!pre) return;
      const text = pre.textContent.replace(/\u{276E}\s*/gu, '').trim();
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 2000);
      }).catch(() => {});
    });
  });

  // ── Back to Top ──
  const backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      backToTop.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── Active nav link on scroll ──
  const sections = document.querySelectorAll('section[id]');
  const navAnchor = document.querySelectorAll('.nav-links a[href^="#"]');
  if (sections.length && navAnchor.length) {
    window.addEventListener('scroll', () => {
      let current = '';
      sections.forEach(s => {
        if (window.scrollY >= s.offsetTop - 120) current = s.id;
      });
      navAnchor.forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === '#' + current);
      });
    }, { passive: true });
  }

});
