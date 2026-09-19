'use strict';

// Small, dependency-free transitions. Content is visible even if this file fails.
window.QASMotion = (() => {
  const root = document.documentElement;
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const button = document.getElementById('motion-toggle');
  const hero = document.querySelector('.hero');
  const header = document.querySelector('header');
  const progress = document.querySelector('.scroll-progress');
  const seen = new WeakSet();
  const running = new WeakMap();
  const transient = new Set();
  let locale = 'es';
  let manualPause = false;
  let frame = 0;
  try { manualPause = localStorage.getItem('qas-motion') === 'paused'; } catch { /* Local files may have no storage. */ }

  function enabled() { return !manualPause && !preference.matches && !document.hidden; }

  function animate(element, frames, options = {}) {
    if (!element || !enabled() || !element.animate) return;
    running.get(element)?.cancel();
    const animation = element.animate(frames, {
      duration: 650,
      easing: 'cubic-bezier(.22,1,.36,1)',
      ...options,
    });
    running.set(element, animation);
    transient.add(animation);
    const clean = () => {
      transient.delete(animation);
      if (running.get(element) === animation) running.delete(element);
    };
    animation.finished.then(clean, clean);
  }

  function cancelTransient() {
    transient.forEach(animation => animation.cancel());
    transient.clear();
  }

  function enter(element, delay = 0) {
    animate(element, [{ opacity: .15, transform: 'translateY(22px)' }, { opacity: 1, transform: 'translateY(0)' }], { delay, fill: 'backwards' });
  }

  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
    entries.forEach(entry => {
      entry.target.classList.toggle('is-in-view', entry.isIntersecting);
      if (!entry.isIntersecting || seen.has(entry.target)) return;
      seen.add(entry.target);
      if (entry.target !== hero) enter(entry.target, Number(entry.target.dataset.motionDelay || 0));
    });
  }, { threshold: .08 }) : null;

  function watch(element) {
    if (observer) observer.observe(element);
    else element.classList.add('is-in-view');
  }

  function observeCards() {
    document.querySelectorAll('.card').forEach((card, index) => {
      card.dataset.motionDelay = String((index % 3) * 55);
      watch(card);
    });
  }

  function releaseCards() {
    document.querySelectorAll('.card').forEach(card => {
      observer?.unobserve(card);
      running.get(card)?.cancel();
    });
  }

  function captureCards() {
    return new Map(Array.from(document.querySelectorAll('.card:not([hidden])'), card => [card, card.getBoundingClientRect()]));
  }

  function filterCards(previous) {
    document.querySelectorAll('.card:not([hidden])').forEach((card, index) => {
      seen.add(card);
      const before = previous?.get(card);
      const after = card.getBoundingClientRect();
      // Skip work outside the viewport; the observer handles its first appearance.
      if (after.bottom < 0 || after.top > innerHeight) { seen.delete(card); return; }
      const transform = before ? `translate(${before.left - after.left}px, ${before.top - after.top}px)` : 'translateY(18px) scale(.98)';
      animate(card, [{ opacity: before ? 1 : .15, transform }, { opacity: 1, transform: 'translate(0, 0) scale(1)' }], { duration: 480, delay: Math.min(index * 35, 140), fill: 'backwards' });
    });
  }

  function updateControl() {
    const paused = manualPause || preference.matches;
    root.classList.toggle('motion-paused', paused);
    button.hidden = preference.matches;
    button.setAttribute('aria-pressed', String(paused));
    const key = paused ? 'ui.resumeMotion' : 'ui.pauseMotion';
    const dictionary = window.QAS_CONTENT.locales[locale].messages;
    const translated = dictionary[key] || window.QAS_CONTENT.locales.es.messages[key];
    button.querySelector('.motion-label').textContent = translated;
    button.setAttribute('aria-label', translated);
    button.lang = dictionary[key] ? locale : 'es';
    if (paused) {
      cancelTransient();
      // A CSS duration change does not cancel transitions already in flight.
      document.getAnimations?.().forEach(animation => {
        if ('transitionProperty' in animation) animation.cancel();
      });
    }
  }

  function languageChanged(value, initial = false) {
    locale = value;
    updateControl();
    if (!initial) {
      [document.querySelector('.hero-inner'), document.querySelector('.word-strip'), document.querySelector('.section-heading')].forEach(element => {
        const rect = element.getBoundingClientRect();
        if (rect.bottom > 0 && rect.top < innerHeight) animate(element, [{ opacity: .45, transform: 'translateY(5px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 360 });
      });
    }
  }

  function updateScroll() {
    frame = 0;
    const distance = Math.max(root.scrollHeight - innerHeight, 1);
    progress.style.transform = `scaleX(${Math.max(0, Math.min(scrollY / distance, 1))})`;
    header.classList.toggle('is-scrolled', scrollY > 20);
  }
  function scheduleScroll() { if (!frame) frame = requestAnimationFrame(updateScroll); }

  button.addEventListener('click', () => {
    manualPause = !manualPause;
    try { localStorage.setItem('qas-motion', manualPause ? 'paused' : 'enabled'); } catch { /* Preference applies for the session. */ }
    updateControl();
  });
  preference.addEventListener('change', updateControl);
  document.addEventListener('visibilitychange', () => {
    root.classList.toggle('page-inactive', document.hidden);
    if (document.hidden) cancelTransient();
  });
  document.addEventListener('click', event => {
    const target = event.target.closest('.button, .filter, .small-link');
    if (target) animate(target, [{ scale: '1' }, { scale: '.96', offset: .3 }, { scale: '1' }], { duration: 260 });
  });
  addEventListener('scroll', scheduleScroll, { passive: true });
  addEventListener('resize', scheduleScroll, { passive: true });
  if ('ResizeObserver' in window) new ResizeObserver(scheduleScroll).observe(document.body);

  [hero, ...document.querySelectorAll('.word, .section-heading, .culture, .guide > div, .guide li, .contact-section')].forEach(watch);
  updateControl();
  updateScroll();
  requestAnimationFrame(() => {
    document.querySelectorAll('.hero-inner > *').forEach((element, index) => enter(element, index * 75));
  });

  return {
    observeCards,
    releaseCards,
    captureCards,
    filterCards,
    languageChanged,
    openDialog(element) {
      animate(element, [{ opacity: 0, transform: 'translateY(18px) scale(.97)' }, { opacity: 1, transform: 'translateY(0) scale(1)' }], { duration: 380 });
    },
  };
})();
