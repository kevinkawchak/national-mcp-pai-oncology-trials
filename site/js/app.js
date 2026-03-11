/**
 * app.js - Main application logic, navigation, scroll behavior
 * National MCP-PAI Oncology Trials - GitHub Pages v1.2.0
 */

(function () {
  "use strict";

  /* ---------- Smooth scroll for nav links ---------- */
  document.addEventListener("click", function (e) {
    var link = e.target.closest('a[href^="#"]');
    if (!link) return;
    var target = document.querySelector(link.getAttribute("href"));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      history.replaceState(null, "", link.getAttribute("href"));
    }
  });

  /* ---------- Active nav highlighting ---------- */
  var navLinks = document.querySelectorAll(".nav-links a");
  var sections = [];

  navLinks.forEach(function (link) {
    var href = link.getAttribute("href");
    if (href && href.startsWith("#")) {
      var sec = document.getElementById(href.slice(1));
      if (sec) sections.push({ el: sec, link: link });
    }
  });

  function updateActiveNav() {
    var scrollY = window.scrollY + 120;
    var current = null;
    sections.forEach(function (s) {
      if (s.el.offsetTop <= scrollY) current = s;
    });
    navLinks.forEach(function (l) { l.classList.remove("active"); });
    if (current) current.link.classList.add("active");
  }

  /* ---------- Back to top button ---------- */
  var backBtn = document.querySelector(".back-to-top");
  function updateBackToTop() {
    if (!backBtn) return;
    if (window.scrollY > 400) {
      backBtn.classList.add("visible");
    } else {
      backBtn.classList.remove("visible");
    }
  }

  if (backBtn) {
    backBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------- Scroll handler ---------- */
  var ticking = false;
  window.addEventListener("scroll", function () {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        updateActiveNav();
        updateBackToTop();
        ticking = false;
      });
      ticking = true;
    }
  });

  /* ---------- Tab functionality ---------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".tab-btn");
    if (!btn) return;
    var group = btn.closest(".tab-group");
    if (!group) return;
    var target = btn.getAttribute("data-tab");

    group.querySelectorAll(".tab-btn").forEach(function (b) {
      b.classList.remove("active");
    });
    group.querySelectorAll(".tab-content").forEach(function (c) {
      c.classList.remove("active");
    });

    btn.classList.add("active");
    var content = group.querySelector('[data-tab-content="' + target + '"]');
    if (content) content.classList.add("active");
  });

  /* ---------- Conformance level expand/collapse ---------- */
  document.addEventListener("click", function (e) {
    var item = e.target.closest(".conformance-level");
    if (!item) return;
    item.classList.toggle("expanded");
  });

  /* ---------- Init ---------- */
  updateActiveNav();
  updateBackToTop();
})();
