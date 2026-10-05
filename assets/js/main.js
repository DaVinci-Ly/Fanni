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

  /* قائمة الجوال: تُغلق عند النقر خارجها أو على رابط أو بزر Esc */
  var menu = doc.querySelector(".menu");
  if (menu) {
    menu.addEventListener("toggle", function () {
      doc.documentElement.classList.toggle("menu-open", menu.open);
    });
    doc.addEventListener("click", function (e) {
      if (menu.open && (!menu.contains(e.target) || e.target.closest("a"))) menu.open = false;
    });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) {
        menu.open = false;
        menu.querySelector("summary").focus();
      }
    });
    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) {
      if (mq.matches) menu.open = false;
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
