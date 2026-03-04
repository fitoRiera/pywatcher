from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

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

_WEBENGINE_CACHE_ROOT = Path.home() / ".cache" / "es.ara.envisage.web_viwer" / "qtwebengine"
_CLEAR_HTTP_CACHE_ON_START = False


logger = logging.getLogger(__name__)


class WebViewerService:

    def create_task_pane(self, page: str) -> TraitsTaskPane:
        task_pane = WebViewerTaskPane()
        task_pane.page = page
        return task_pane


class WebViewerTaskPane(TraitsTaskPane):
    """Central pane that renders a web page from a URL."""

    id = "pywatcher.web_view"
    name = "Web Viewer"
    page = Str('<html><body>Page not specified</body></html>')

    _web_control = Any()
    _web_profile = Any()
    _web_page = Any()

    def create(self, parent):
        if QWebEngineView is not None:
            control = QWebEngineView(parent)
            self._configure_web_engine(control)
        else:
            control = QtWidgets.QTextBrowser(parent)

        self._web_control = control
        self.control = control
        self._load_page(self.page)

    def set_page(self, page: str) -> None:
        """Update the URL shown in the pane."""
        self.page = page

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

    @observe("page")
    def _on_page_changed(self, event):
        self._load_url(event.new)

    def _load_page(self, new_page):
        if not new_page:
            raise ValueError("Page not specified")
        if self._is_url(new_page):
            self._load_url(new_page)
        else:
            self._load_html(new_page)

    @staticmethod
    def _is_url(page: str) -> bool:
        if not page:
            return False

        parsed = urlparse(page.strip())
        if parsed.scheme in {"http", "https"}:
            return bool(parsed.netloc)
        if parsed.scheme == "file":
            return bool(parsed.path)
        return False

    def _load_url(self, url):
        if self._web_control is None:
            logger.warning("WebViewerService._web_control is not initialized")
            return
        if QWebEngineView is not None and isinstance(self._web_control, QWebEngineView):
            self._web_control.load(url)
            return
        self._web_control.setSource(url)

    def _load_html(self, event):
        #TODO
        raise NotImplementedError()
