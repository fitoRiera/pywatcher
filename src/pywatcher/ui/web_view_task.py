from __future__ import annotations

from pyface.qt import QtWidgets
from pyface.tasks.api import TraitsTaskPane
from traits.api import Any, Str, observe

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover - depends on optional Qt module
    QWebEngineView = None


class WebViewTaskPane(TraitsTaskPane):
    """Central pane that renders a web page from HTML text."""

    id = "pywatcher.web_view"
    name = "Web Viewer"
    html_text = Str(
        """\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>PyWatcher</title>
    <style>
      body { font-family: sans-serif; padding: 20px; }
      .counter { font-size: 2rem; font-weight: bold; color: #1f6feb; }
    </style>
  </head>
  <body>
    <h1>PyWatcher</h1>
    <p>Live counter (updates every second):</p>
    <div id="counter" class="counter">0</div>
    <script>
      let count = 0;
      const counterElement = document.getElementById("counter");
      setInterval(() => {
        count += 1;
        counterElement.textContent = String(count);
      }, 1000);
    </script>
  </body>
</html>
"""
    )

    _web_control = Any()

    def create(self, parent):
        if QWebEngineView is not None:
            control = QWebEngineView(parent)
            control.setHtml(self.html_text)
        else:
            control = QtWidgets.QTextBrowser(parent)
            control.setHtml(self.html_text)

        self._web_control = control
        self.control = control

    def set_html(self, html: str) -> None:
        """Update the HTML shown in the pane."""
        self.html_text = html

    @observe("html_text")
    def _on_html_text_changed(self, event):
        if self._web_control is None:
            return
        self._web_control.setHtml(event.new)
