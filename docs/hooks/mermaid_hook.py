"""MkDocs hooks: mermaid.js CDN + version/date 치환."""

import json
import os
import subprocess

MERMAID_SCRIPT = """<script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
  if (typeof mermaid === "undefined") return;
  document.querySelectorAll(".mermaid").forEach(function(el) {
    el.textContent = el.textContent;
  });
  var isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({ startOnLoad: true, theme: isDark ? "dark" : "default" });
});
</script>
"""

_version_cache = {}


def _load_version(config):
    if _version_cache:
        return _version_cache

    hook_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.dirname(hook_dir)
    version_file = os.path.join(docs_dir, "version.json")

    version = "3.6"
    date = ""

    if os.path.exists(version_file):
        with open(version_file, encoding="utf-8") as f:
            data = json.load(f)
        version = data.get("version", version)
        date = data.get("date", "")

    _version_cache["version"] = version
    _version_cache["date"] = date
    return _version_cache


def on_page_markdown(markdown, page, config, **kwargs):
    if "{{version}}" in markdown or "{{date}}" in markdown:
        v = _load_version(config)
        markdown = markdown.replace("{{version}}", v["version"])
        markdown = markdown.replace("{{date}}", v["date"])
    return markdown


def on_post_page(output, page, config):
    if "mermaid" in output:
        return output.replace("</body>", MERMAID_SCRIPT + "</body>")
    return output
