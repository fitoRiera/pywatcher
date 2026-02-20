from __future__ import annotations

from pathlib import Path

from pyface.qt import QtWidgets
from pyface.tasks.api import TraitsTaskPane
from traits.api import Any, Str, observe

try:
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover - depends on optional Qt module
    QWebEngineView = None
    QWebEnginePage = None
    QWebEngineProfile = None

_WEBENGINE_CACHE_ROOT = Path.home() / ".cache" / "pywatcher" / "qtwebengine"
_CLEAR_HTTP_CACHE_ON_START = False

_DEFAULT_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h3>BasicExample.html no encontrado.</h3>
</body>
</html>
"""


def _load_default_html() -> str:
    html_path = Path(__file__).with_name("BasicExample.html")
    try:
        return html_path.read_text(encoding="utf-8")
    except OSError:
        return _DEFAULT_HTML


class WebViewTaskPane(TraitsTaskPane):
    """Central pane that renders a web page from HTML text."""

    id = "pywatcher.web_view"
    name = "Web Viewer"
    html_text = Str(_load_default_html())

    _web_control = Any()
    _web_profile = Any()
    _web_page = Any()

    def create(self, parent):
        if QWebEngineView is not None:
            control = QWebEngineView(parent)
            self._configure_web_engine(control)
            control.setHtml(self.html_text)
        else:
            control = QtWidgets.QTextBrowser(parent)
            control.setHtml(self.html_text)

        self._web_control = control
        self.control = control

    def set_html(self, html: str) -> None:
        """Update the HTML shown in the pane."""
        self.html_text = html

    def _configure_web_engine(self, control) -> None:
        if QWebEngineProfile is None or QWebEnginePage is None:
            return

        _WEBENGINE_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile("pywatcher.web_view", control)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setCachePath(str(_WEBENGINE_CACHE_ROOT / "http-cache"))
        profile.setPersistentStoragePath(str(_WEBENGINE_CACHE_ROOT / "storage"))
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        if _CLEAR_HTTP_CACHE_ON_START:
            profile.clearHttpCache()

        page = QWebEnginePage(profile, control)
        control.setPage(page)
        self._web_profile = profile
        self._web_page = page

    @observe("html_text")
    def _on_html_text_changed(self, event):
        if self._web_control is None:
            return
        self._web_control.setHtml(event.new)
