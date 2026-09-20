'use strict';

const { catalog, locales } = window.QAS_CONTENT;
const pageRoutes = window.QAS_PAGE;
let language = 'es';
let category = 'all';
let languageInitialized = false;
const dialog = document.getElementById('article');
const titleKey = article => `article.${article.id}.title`;
const summaryKey = article => `article.${article.id}.summary`;

function translation(key) {
  const value = locales[language].messages[key];
  const translated = typeof value === 'string' && value.trim() !== '';
  return { text: translated ? value : locales.es.messages[key], lang: translated ? language : 'es' };
}

function fill(element, key) {
  const value = translation(key);
  element.textContent = value.text;
  element.lang = value.lang;
  return element;
}

function translatedElement(tag, key, className) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  return fill(element, key);
}

function renderCards() {
  const cards = document.querySelector('.cards');
  window.QASMotion?.releaseCards();
  cards.replaceChildren();
  const categoryKeys = { astronomy: 'ui.astronomyTag', solar: 'ui.solarTag', andino: 'ui.andinoTag', learning: 'ui.learningTag' };
  catalog.articles.filter(article => article.showCard).forEach(article => {
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.category = article.category;
    card.hidden = category !== 'all' && article.category !== category;
    const visual = document.createElement('div');
    visual.className = `card-image topic-art topic-${article.id}`;
    const symbol = document.createElement('span');
    symbol.className = 'topic-symbol';
    symbol.textContent = article.symbol;
    symbol.setAttribute('aria-hidden', 'true');
    visual.append(symbol, translatedElement('span', categoryKeys[article.category], 'tag'));
    const scene = document.createElement('div');
    scene.className = 'scene';
    scene.setAttribute('aria-hidden', 'true');
    ['scene-orbit', 'scene-orbit outer', 'scene-body', 'scene-mountain'].forEach(className => {
      const layer = document.createElement('span');
      layer.className = className;
      scene.append(layer);
    });
    visual.append(scene);
    const body = document.createElement('div');
    body.className = 'card-body';
    const title = translatedElement('h3', titleKey(article));
    title.id = `card-${article.id}`;
    const summary = translatedElement('p', summaryKey(article));
    const button = translatedElement('a', 'ui.readArticle', 'small-link');
    button.href = pageRoutes.articleLinks[language][article.id];
    button.dataset.article = article.id;
    button.setAttribute('aria-describedby', title.id);
    const arrow = document.createElement('span');
    arrow.textContent = '↗';
    arrow.setAttribute('aria-hidden', 'true');
    button.append(arrow);
    body.append(title, summary, button);
    card.append(visual, body);
    cards.append(card);
  });
  window.QASMotion?.observeCards();
}

function renderArticle(id) {
  const article = catalog.articles.find(item => item.id === id);
  if (!article) return;
  dialog.dataset.article = id;
  fill(document.getElementById('article-title'), titleKey(article));
  const body = document.getElementById('article-body');
  body.replaceChildren();
  const fullPage = translatedElement('a', 'ui.articlePage', 'small-link');
  fullPage.href = pageRoutes.articleLinks[language][id];
  body.append(fullPage);
  article.paragraphs.forEach(key => body.append(translatedElement('p', key)));
  if (id === 'glossary') {
    const glossary = document.createElement('dl');
    glossary.className = 'glossary';
    catalog.glossary.forEach(term => {
      glossary.append(translatedElement('dt', `glossary.${term}.term`), translatedElement('dd', `glossary.${term}.definition`));
    });
    body.append(glossary);
  }
  if (article.activity) {
    const activity = document.createElement('section');
    activity.className = 'article-activity';
    activity.append(translatedElement('h3', 'ui.activity'), translatedElement('p', article.activity));
    body.append(activity);
  }
  if (article.sources.length) {
    body.append(translatedElement('h3', 'ui.sourceHeading'));
    const list = document.createElement('ul');
    list.className = 'source';
    article.sources.forEach(id => {
      const source = catalog.sources[id];
      const item = document.createElement('li');
      const link = document.createElement('a');
      fill(link, source.labelKey);
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      item.append(link);
      list.append(item);
    });
    body.append(list);
  }
  const parts = article.paragraphs.map(key => translation(key).text);
  if (id === 'glossary') catalog.glossary.forEach(term => parts.push(translation(`glossary.${term}.term`).text + ': ' + translation(`glossary.${term}.definition`).text));
  if (article.activity) parts.push(translation('ui.activity').text, translation(article.activity).text);
  article.sources.forEach(key => parts.push(translation(catalog.sources[key].labelKey).text + ': ' + catalog.sources[key].url));
  const messages = Object.fromEntries(Object.keys(locales.es.messages).filter(key => key.startsWith('ui.')).map(key => [key, translation(key).text]));
  const url = new URL(fullPage.getAttribute('href'), location.href);
  if (url.protocol === 'https:' || url.protocol === 'http:') body.append(window.QASShare.create(translation(titleKey(article)).text, parts.join('\n\n'), url.href, messages, locales[language].meta.needsReview ? translation('ui.translationDraft').text : ''));
}

function setLanguage(value) {
  if (!Object.hasOwn(locales, value)) value = 'es';
  language = value;
  // Untranslated passages carry lang="es" individually, including partial locales.
  document.documentElement.lang = value;
  document.querySelectorAll('[data-i18n]').forEach(element => fill(element, element.dataset.i18n));
  document.querySelectorAll('[data-i18n-aria]').forEach(element => {
    const translated = translation(element.dataset.i18nAria);
    element.setAttribute('aria-label', translated.text);
    element.lang = translated.lang;
  });
  document.title = 'QAS · Quechua Aimara Space — ' + translation('ui.pageTitle').text.replace(/^QAS · /, '');
  document.querySelector('meta[name="description"]').content = translation('ui.pageDescription').text;
  document.getElementById('language').value = value;
  const notice = document.getElementById('language-notice');
  const complete = Object.values(locales[value].messages).every(text => typeof text === 'string' && text.trim());
  const needsReview = locales[value].meta.needsReview === true;
  notice.hidden = complete && !needsReview;
  fill(notice, complete && needsReview ? 'ui.translationDraft' : 'ui.pendingTranslation');
  document.querySelectorAll('a[data-article]').forEach(link => { link.href = pageRoutes.articleLinks[value][link.dataset.article]; });
  renderCards();
  if (dialog.open) renderArticle(dialog.dataset.article);
  window.QASMotion?.languageChanged(value, !languageInitialized);
  languageInitialized = true;
  try { localStorage.setItem('qas-language', value); } catch { /* Storage may be unavailable for local files. */ }
}

function filter(value) {
  const previous = window.QASMotion?.captureCards();
  category = value;
  document.querySelectorAll('.filter').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === value)));
  document.querySelectorAll('.card').forEach(card => { card.hidden = value !== 'all' && card.dataset.category !== value; });
  window.QASMotion?.filterCards(previous);
}

document.getElementById('language').addEventListener('change', event => {
  const target = pageRoutes.homeLinks[event.target.value];
  if (target) location.assign(target);
});
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => filter(button.dataset.filter)));
document.getElementById('show-all').addEventListener('click', () => filter('all'));
document.addEventListener('click', event => {
  const button = event.target.closest('a[data-article], button[data-article]');
  if (!button || event.defaultPrevented || event.button > 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  renderArticle(button.dataset.article);
  dialog.showModal();
  dialog.scrollTop = 0;
  window.QASMotion?.openDialog(dialog);
});
dialog.querySelector('.close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
});

document.getElementById('download').addEventListener('click', () => {
  const keys = ['ui.observeTitle', 'ui.observeDescription', 'ui.step1', 'ui.step2', 'ui.step3', 'ui.logTitle', 'ui.logDate', 'ui.logTime', 'ui.logPlace', 'ui.logWeather', 'ui.logSeen', 'ui.logWords', 'ui.sunSafety'];
  const parts = keys.map(translation);
  const allSpanish = parts.every(part => part.lang === 'es');
  const fallbackUsed = parts.some(part => part.lang !== language);
  const reviewNote = locales[language].meta.needsReview ? [translation('ui.translationDraft').text] : [];
  const text = ['QAS · Quechua Aimara Space', ...reviewNote, ...(fallbackUsed ? [translation('ui.pendingTranslation').text] : []), ...parts.map(part => part.text)].join('\r\n\r\n');
  const url = URL.createObjectURL(new Blob(['\ufeff' + text], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `QAS-guia-${allSpanish ? 'es' : language}.txt`;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) document.querySelectorAll('nav a').forEach(link => link.classList.toggle('active', link.hash === '#' + entry.target.id));
  }), { rootMargin: '-10% 0px -55% 0px', threshold: 0 });
  document.querySelectorAll('main section[id]').forEach(section => observer.observe(section));
}
// The URL determines the language; stored preferences must not change crawlable pages.
setLanguage(pageRoutes.language);
