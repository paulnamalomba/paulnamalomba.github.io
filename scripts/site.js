const menuButton = document.querySelector('[data-menu-button]');
const navigation = document.querySelector('[data-nav]');
const header = document.querySelector('[data-header]');

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    navigation.classList.toggle('open', !isOpen);
    document.body.classList.toggle('menu-open', !isOpen);
  });

  navigation.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      menuButton.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('open');
      document.body.classList.remove('menu-open');
    });
  });
}

const syncHeader = () => header?.classList.toggle('scrolled', window.scrollY > 12);
syncHeader();
window.addEventListener('scroll', syncHeader, { passive: true });

document.querySelectorAll('[data-year]').forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
