
from envisage.plugin import Plugin
from envisage.service_offer import ServiceOffer
from envisage.ui.tasks.task_factory import TaskFactory
from traits.trait_types import List
import os

from es.ara.envisage.web_viewer.web_viewer_api.api import WEB_VIEWER_SERVICE_PROTOCOL

SERVICE_OFFERS='envisage.service_offers'


class WebViewerPlugin(Plugin):

    webViewerService = None

    service_offers = List(contributes_to=SERVICE_OFFERS)

    editors = List(contributes_to="pywatcher.ui.main_window.editors")

    def _service_offers_default(self):
        service_offer = ServiceOffer(
            protocol=WEB_VIEWER_SERVICE_PROTOCOL,
            factory=self._get_service
        )
        return [service_offer]

    def _get_service(self):
        if not self.webViewerService:
            from es.ara.envisage.web_viewer.web_viewer_plugin.web_viewer_service import WebViewerService
            self.webViewerService = WebViewerService()
        return self.webViewerService

    def _editors_default(self):
        return [
            self._get_service().create_task_pane('http://google.com')
        ]

    def _create_editor(self):
        return