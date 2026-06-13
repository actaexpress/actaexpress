const COOKIE_CONSENT_KEY = "actaexpress_cookie_consent";

function showCookieBanner() {
  if (localStorage.getItem(COOKIE_CONSENT_KEY)) return;

  const banner = document.createElement("div");
  banner.className = "cookie-banner";
  banner.setAttribute("role", "dialog");
  banner.setAttribute("aria-label", "Consentement cookies");
  banner.innerHTML = `
    <div class="cookie-banner-inner">
      <p>
        Nous utilisons des cookies pour mesurer l'audience et améliorer le site.
        <a href="/legal/cookies.html">En savoir plus</a>
      </p>
      <div class="cookie-banner-actions">
        <button type="button" class="btn btn-sm" data-cookie="reject">Refuser</button>
        <button type="button" class="btn btn-primary btn-sm" data-cookie="accept">Accepter</button>
      </div>
    </div>
  `;

  const base = document.querySelector('link[href*="css/style.css"]')?.href.includes("../") ? "../" : "";
  const cookiesLink = banner.querySelector("a");
  if (cookiesLink) cookiesLink.href = `${base}legal/cookies.html`;

  banner.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cookie]");
    if (!btn) return;
    localStorage.setItem(COOKIE_CONSENT_KEY, btn.dataset.cookie);
    banner.remove();
  });

  document.body.appendChild(banner);
}

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const mobileNav = document.querySelector(".nav-mobile");

  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      mobileNav.classList.toggle("open");
    });
  }

  showCookieBanner();
});
