from __future__ import annotations

import logging
import time
from pathlib import Path
from urllib.parse import urlparse

from pyface.qt import QtCore, QtWidgets
from pyface.tasks.api import TraitsTaskPane
from traits.api import Any, Str, observe

_WEBENGINE_IMPORT_ERROR = None
_WEBCHANNEL_IMPORT_ERROR = None

QWebEngineView = None
QWebEnginePage = None
QWebEngineProfile = None
QWebEngineSettings = None
QWebChannel = None

for _binding_name in ("PySide6", "PyQt6", "PyQt5"):
    try:
        if _binding_name == "PySide6":
            from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtWebChannel import QWebChannel
        elif _binding_name == "PyQt6":
            from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtWebChannel import QWebChannel
        else:
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
            from PyQt5.QtWebEngineWidgets import QWebEngineSettings
            from PyQt5.QtWebChannel import QWebChannel
        _WEBENGINE_IMPORT_ERROR = None
        _WEBCHANNEL_IMPORT_ERROR = None
        break
    except Exception as exc:  # pragma: no cover - depends on optional Qt module
        if QWebEngineView is None:
            _WEBENGINE_IMPORT_ERROR = exc
        if QWebChannel is None:
            _WEBCHANNEL_IMPORT_ERROR = exc

_WEBENGINE_CACHE_ROOT = Path.home() / ".cache" / "es.ara.envisage.web_viwer" / "qtwebengine"
_CLEAR_HTTP_CACHE_ON_START = False


logger = logging.getLogger(__name__)


class WebChannelBackend(QtCore.QObject):
    """QObject exposed to JavaScript through QWebChannel as `backend`."""

    messageReceived = QtCore.Signal(str)
    messageToJavascript = QtCore.Signal(str)
    javascriptResponse = QtCore.Signal(str)

    def __init__(self, page):
        super().__init__(page)
        self._page = page

    @QtCore.Slot(str, result=str)
    def send_to_python(self, message: str) -> str:
        logger.info("Mensaje recibido desde JS: %s", message)
        self.messageReceived.emit(message)
        self.send_to_javascript()
        return f"ACK: {message}"

    @QtCore.Slot(result=str)
    def send_to_javascript(self) -> str:
        message = "Hola desde Python"
        #self.messageToJavascript.emit(message)
        self.call_javascript("hola desde Python", response_handler=logging.error)
        return message

    @QtCore.Slot(str)
    def call_javascript(self, message: str, response_handler:callable=None) -> None:
        if self._page is None:
            logger.warning("No hay QWebEnginePage asociado para ejecutar JavaScript.")
            return

        script = f"window.handleFromPython({message!r})"

        def _on_reply(result):
            nonlocal response_handler
            logger.info("Respuesta desde JS: %s", result)
            if response_handler:
                response_handler(result)

        self._page.runJavaScript(script, _on_reply)


class LoggingWebEnginePage(QWebEnginePage):
    """QWebEnginePage that forwards JS console messages to Python logs."""

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        logger.warning("JS console [%s] %s:%s - %s", level, source_id, line_number, message)


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
    _web_channel = Any()
    _web_backend = Any()

    def create(self, parent):
        if QWebEngineView is not None:
            control = QWebEngineView(parent)
            self._configure_web_engine(control)
        else:
            logger.warning(
                "QWebEngineView no disponible; usando QTextBrowser sin JavaScript. Error import: %s",
                _WEBENGINE_IMPORT_ERROR,
            )
            control = QtWidgets.QTextBrowser(parent)
            control.setHtml(
                "<html><body>"
                "<h3>QtWebEngine no disponible</h3>"
                "<p>Este visor ha usado QTextBrowser y no ejecuta JavaScript ni QWebChannel.</p>"
                "<p>Revisa la instalacion de PySide6 QtWebEngine.</p>"
                "</body></html>"
            )

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

        page = LoggingWebEnginePage(profile, control)
        control.setPage(page)
        self._configure_web_channel(page)
        if QWebEngineSettings is not None:
            settings = control.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self._web_profile = profile
        self._web_page = page

    def _configure_web_channel(self, page) -> None:
        if QWebChannel is None:
            logger.warning(
                "PySide6.QtWebChannel no disponible: backend JS/Python deshabilitado. Error import: %s",
                _WEBCHANNEL_IMPORT_ERROR,
            )
            return

        backend = WebChannelBackend(page)
        channel = QWebChannel(page)
        channel.registerObject("backend", backend)
        page.setWebChannel(channel)

        # Keep strong refs to avoid QObject/channel being garbage-collected.
        self._web_backend = backend
        self._web_channel = channel

    @observe("page")
    def _on_page_changed(self, event):
        self._load_page(event.new)

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
        qurl = QtCore.QUrl(url) if isinstance(url, str) else url
        if QWebEngineView is not None and isinstance(self._web_control, QWebEngineView):
            self._web_control.load(qurl)
            return
        self._web_control.setSource(qurl)

    def _load_html(self, event):
        #TODO
        raise NotImplementedError()
