/* =========================================================
   Miguel Villalba — Portfolio
   Vanilla JS (no jQuery / no framework)
   ========================================================= */
(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Preloader ---------- */
  window.addEventListener("load", () => {
    const pre = document.getElementById("preloader");
    if (pre) { pre.classList.add("done"); setTimeout(() => pre.remove(), 600); }
  });

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
      document.body.style.overflow = "";
    };
    navToggle.addEventListener("click", () => {
      const willOpen = !navMenu.classList.contains("open");
      navMenu.classList.toggle("open", willOpen);
      navToggle.classList.toggle("is-open", willOpen);
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

  /* ---------- Typed role rotator ---------- */
  const typedEl = document.querySelector("[data-typed]");
  if (typedEl) {
    const items = (typedEl.getAttribute("data-typed") || "").split("|").map(s => s.trim()).filter(Boolean);
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
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-filter");
      projectCards.forEach(card => {
        const match = filter === "*" || card.getAttribute("data-category") === filter;
        card.classList.toggle("is-hidden", !match);
      });
    });
  });

  /* ---------- Testimonials carousel ---------- */
  const track = document.querySelector(".testi-track");
  const prevBtn = document.querySelector("[data-testi-prev]");
  const nextBtn = document.querySelector("[data-testi-next]");
  if (track && prevBtn && nextBtn) {
    const scrollByCard = (dir) => {
      const card = track.querySelector(".testi-card");
      const gap = 22.4; // matches CSS gap
      const width = card ? card.getBoundingClientRect().width + gap : 320;
      track.scrollBy({ left: dir * width, behavior: reducedMotion ? "auto" : "smooth" });
    };
    prevBtn.addEventListener("click", () => scrollByCard(-1));
    nextBtn.addEventListener("click", () => scrollByCard(1));
  }

  /* ---------- Footer year ---------- */
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

})();
