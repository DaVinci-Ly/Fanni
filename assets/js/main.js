/* ==========================================================================
   المتخصص الفني — سكربت الواجهة
   الموقع يعمل كاملًا بدونه؛ وظيفته تحسين التجربة فقط.
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ظلّ الترويسة بعد بدء التمرير */
  var header = doc.querySelector("[data-header]");
  if (header) {
    var ticking = false;
    var onScroll = function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
        ticking = false;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* قائمة الجوال: زر يفتح لوحة الروابط ويغلقها */
  var toggle = doc.querySelector(".nav-toggle");
  var nav = doc.getElementById("site-nav");
  if (header && toggle && nav) {
    var isOpen = function () { return toggle.getAttribute("aria-expanded") === "true"; };
    var setOpen = function (open, restoreFocus) {
      header.classList.toggle("is-open", open);
      doc.documentElement.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", toggle.getAttribute(open ? "data-label-close" : "data-label-open"));
      if (open) {
        var first = nav.querySelector("a");
        if (first) first.focus({ preventScroll: true });
      } else if (restoreFocus) {
        toggle.focus();
      }
    };
    toggle.addEventListener("click", function () { setOpen(!isOpen()); });
    nav.addEventListener("click", function (e) {
      if (isOpen() && e.target.closest("a")) setOpen(false);
    });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) setOpen(false, true);
    });
    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) {
      if (mq.matches && isOpen()) setOpen(false);
    });
  }

  /* تأخير متدرّج للعناصر داخل المجموعات */
  each(doc.querySelectorAll(".cats, .steps, .records"), function (group) {
    each(group.children, function (child, i) { child.style.setProperty("--i", i % 4); });
  });

  /* الظهور عند التمرير */
  var revealables = doc.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    each(revealables, function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    each(revealables, function (el) { io.observe(el); });
  }

  /* سنة حقوق النشر */
  each(doc.querySelectorAll("[data-year]"), function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
