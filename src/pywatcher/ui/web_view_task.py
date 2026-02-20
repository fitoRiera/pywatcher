from __future__ import annotations

from pathlib import Path

from pyface.qt import QtCore, QtWidgets
from pyface.tasks.api import TraitsTaskPane
from traits.api import Any, Str, observe

try:
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover - depends on optional Qt module
    QWebEngineView = None
    QWebEnginePage = None
    QWebEngineProfile = None
    QWebEngineSettings = None

_WEBENGINE_CACHE_ROOT = Path.home() / ".cache" / "pywatcher" / "qtwebengine"
_CLEAR_HTTP_CACHE_ON_START = False

def _default_page_url() -> str:
    html_path = Path(__file__).with_name("BasicExample.html")
    if html_path.exists():
        return html_path.resolve().as_uri()
    return "about:blank"


class WebViewTaskPane(TraitsTaskPane):
    """Central pane that renders a web page from a URL."""

    id = "pywatcher.web_view"
    name = "Web Viewer"
    page_url = Str(_default_page_url())

    _web_control = Any()
    _web_profile = Any()
    _web_page = Any()

    def create(self, parent):
        if QWebEngineView is not None:
            control = QWebEngineView(parent)
            self._configure_web_engine(control)
            control.load(QtCore.QUrl(self.page_url))
        else:
            control = QtWidgets.QTextBrowser(parent)
            control.setSource(QtCore.QUrl(self.page_url))

        self._web_control = control
        self.control = control

    def set_url(self, url: str) -> None:
        """Update the URL shown in the pane."""
        self.page_url = url

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
        if QWebEngineSettings is not None:
            settings = control.settings()
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self._web_profile = profile
        self._web_page = page

    @observe("page_url")
    def _on_page_url_changed(self, event):
        if self._web_control is None:
            return
        url = QtCore.QUrl(event.new)
        if QWebEngineView is not None and isinstance(self._web_control, QWebEngineView):
            self._web_control.load(url)
            return
        self._web_control.setSource(url)
