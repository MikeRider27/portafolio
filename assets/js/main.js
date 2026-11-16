/* =========================================================
   Miguel Villalba — Portfolio
   Vanilla JS (no jQuery / no framework)
   ========================================================= */
(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Preloader ---------- */
  // Don't wait for images/fonts ("load"): DOM-ready is enough to show content.
  const hidePreloader = () => {
    const pre = document.getElementById("preloader");
    if (pre) { pre.classList.add("done"); setTimeout(() => pre.remove(), 600); }
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", hidePreloader);
  else hidePreloader();

  /* ---------- Back to top (declared early: onScroll below calls this) ---------- */
  const toTop = document.querySelector(".to-top");
  function toggleBackToTop() {
    if (!toTop) return;
    toTop.classList.toggle("show", window.scrollY > 500);
  }
  if (toTop) {
    toTop.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" });
    });
  }

  /* ---------- Header scroll state ---------- */
  const header = document.querySelector(".site-header");
  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 12);
    toggleBackToTop();
  };
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile nav ---------- */
  const navToggle = document.querySelector(".nav-toggle");
  const navMenu = document.querySelector(".nav-menu");
  if (navToggle && navMenu) {
    const closeMenu = () => {
      navMenu.classList.remove("open");
      navToggle.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    };
    navToggle.addEventListener("click", () => {
      const willOpen = !navMenu.classList.contains("open");
      navMenu.classList.toggle("open", willOpen);
      navToggle.classList.toggle("is-open", willOpen);
      navToggle.setAttribute("aria-expanded", String(willOpen));
      document.body.style.overflow = willOpen ? "hidden" : "";
    });
    navMenu.querySelectorAll("a").forEach(a => a.addEventListener("click", closeMenu));
    document.addEventListener("keydown", e => { if (e.key === "Escape") closeMenu(); });
  }

  /* ---------- Scrollspy ---------- */
  const sections = document.querySelectorAll("main section[id]");
  const navLinks = document.querySelectorAll(".nav-menu a[href^='#']");
  if (sections.length && navLinks.length && "IntersectionObserver" in window) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const id = entry.target.getAttribute("id");
        navLinks.forEach(link => {
          link.classList.toggle("active", link.getAttribute("href") === `#${id}`);
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    sections.forEach(s => spy.observe(s));
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !reducedMotion) {
    const reveal = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => reveal.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add("in-view"));
  }

  /* ---------- Language (ES / EN) ----------
     Spanish lives in the HTML. English lives next to it:
       data-en="…"              → replaces innerHTML
       data-en-<attr>="…"       → replaces that attribute (aria-label, alt, content, data-typed…)
     The Spanish originals are cached on first switch, so no ES dictionary is needed. */
  const LANG_KEY = "portfolio-lang";
  const SUPPORTED = ["es", "en"];

  const storage = {
    get() { try { return localStorage.getItem(LANG_KEY); } catch (_) { return null; } },
    set(v) { try { localStorage.setItem(LANG_KEY, v); } catch (_) { /* private mode */ } }
  };

  const initialLang = () => {
    const fromUrl = new URLSearchParams(location.search).get("lang");
    if (SUPPORTED.includes(fromUrl)) return fromUrl;
    const saved = storage.get();
    if (SUPPORTED.includes(saved)) return saved;
    return (navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en";
  };

  const applyLang = (lang) => {
    document.querySelectorAll("[data-en]").forEach(el => {
      if (el.__es === undefined) el.__es = el.innerHTML;
      el.innerHTML = lang === "en" ? el.getAttribute("data-en") : el.__es;
    });

    document.querySelectorAll("*").forEach(el => {
      for (const { name, value } of Array.from(el.attributes)) {
        if (!name.startsWith("data-en-")) continue;
        const target = name.slice("data-en-".length);
        el.__esAttrs = el.__esAttrs || {};
        if (!(target in el.__esAttrs)) el.__esAttrs[target] = el.getAttribute(target);
        const next = lang === "en" ? value : el.__esAttrs[target];
        if (next === null) el.removeAttribute(target); else el.setAttribute(target, next);
      }
    });

    document.documentElement.lang = lang;
    document.querySelectorAll("[data-lang-opt]").forEach(o =>
      o.classList.toggle("is-active", o.getAttribute("data-lang-opt") === lang));
    document.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
  };

  let currentLang = initialLang();
  if (currentLang !== "es") applyLang(currentLang);
  else document.querySelectorAll("[data-lang-opt='es']").forEach(o => o.classList.add("is-active"));

  const langToggle = document.getElementById("langToggle");
  if (langToggle) {
    langToggle.addEventListener("click", () => {
      currentLang = currentLang === "es" ? "en" : "es";
      applyLang(currentLang);
      storage.set(currentLang);
    });
  }

  /* ---------- Typed role rotator ---------- */
  const typedEl = document.querySelector("[data-typed]");
  if (typedEl) {
    const readItems = () => (typedEl.getAttribute("data-typed") || "").split("|").map(s => s.trim()).filter(Boolean);
    let items = readItems();
    if (items.length) {
      let itemIndex = 0, charIndex = 0, deleting = false;
      const textNode = document.createElement("span");
      typedEl.textContent = "";
      typedEl.appendChild(textNode);
      const cursor = document.createElement("span");
      cursor.className = "cursor";
      typedEl.appendChild(cursor);

      const tick = () => {
        const current = items[itemIndex];
        if (!deleting) {
          charIndex++;
          textNode.textContent = current.slice(0, charIndex);
          if (charIndex === current.length) {
            deleting = true;
            setTimeout(tick, 1600);
            return;
          }
        } else {
          charIndex--;
          textNode.textContent = current.slice(0, charIndex);
          if (charIndex === 0) {
            deleting = false;
            itemIndex = (itemIndex + 1) % items.length;
          }
        }
        setTimeout(tick, deleting ? 35 : 65);
      };
      document.addEventListener("langchange", () => {
        items = readItems();
        itemIndex = 0; charIndex = 0; deleting = false;
        textNode.textContent = reducedMotion ? items[0] : "";
      });

      if (reducedMotion) {
        textNode.textContent = items[0];
      } else {
        tick();
      }
    }
  }

  /* ---------- Counters ---------- */
  const counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const animateCount = (el) => {
      const target = parseFloat(el.getAttribute("data-count"));
      const suffix = el.getAttribute("data-suffix") || "";
      if (reducedMotion) { el.textContent = target + suffix; return; }
      const duration = 1400;
      const start = performance.now();
      const step = (now) => {
        const p = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    const cObs = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { animateCount(entry.target); obs.unobserve(entry.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(c => cObs.observe(c));
  }

  /* ---------- Portfolio filter ---------- */
  const filterBtns = document.querySelectorAll(".filter-bar button");
  const projectCards = document.querySelectorAll(".project-card");
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("active");
      btn.setAttribute("aria-pressed", "true");
      const filter = btn.getAttribute("data-filter");
      projectCards.forEach(card => {
        const cats = (card.getAttribute("data-category") || "").split(/\s+/);
        const match = filter === "*" || cats.includes(filter);
        card.classList.toggle("is-hidden", !match);
      });
    });
  });

  /* ---------- Footer year ---------- */
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

})();
