document.addEventListener("DOMContentLoaded", function() {
  if (typeof mermaid === "undefined") return;

  // HTML 엔티티 복원 (fence_div_format이 이스케이프한 것)
  document.querySelectorAll(".mermaid").forEach(function(el) {
    el.setAttribute("data-original", el.innerHTML);
    el.innerHTML = el.innerHTML
      .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&").replace(/&quot;/g, '"');
  });

  var isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({ startOnLoad: false, theme: isDark ? "dark" : "default" });
  mermaid.run({ nodes: document.querySelectorAll(".mermaid") });
});

// 테마 전환 시 재렌더링
new MutationObserver(function() {
  if (typeof mermaid === "undefined") return;
  document.querySelectorAll(".mermaid svg").forEach(function(svg) { svg.remove(); });
  document.querySelectorAll(".mermaid").forEach(function(el) {
    el.removeAttribute("data-processed");
    if (el.getAttribute("data-original"))
      el.innerHTML = el.getAttribute("data-original")
        .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
        .replace(/&amp;/g, "&").replace(/&quot;/g, '"');
  });
  var isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({ startOnLoad: false, theme: isDark ? "dark" : "default" });
  mermaid.run({ nodes: document.querySelectorAll(".mermaid") });
}).observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
