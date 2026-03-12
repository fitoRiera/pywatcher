from envisage.plugin import Plugin
from envisage.service_offer import ServiceOffer
from traits.trait_types import List


SERVICE_OFFERS='envisage.service_offers'

WEB_VIEWER_SERVICE_PROTOCOL='es.ara.envisage.web_viewer.web_viewer_api.api.IWebViewerService'


class WebViewerPlugin(Plugin):

    webViewerService = None

    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        service_offer = ServiceOffer(
            protocol=WEB_VIEWER_SERVICE_PROTOCOL,
            factory=self._create_service
        )
        return [service_offer]

    @staticmethod
    def _create_service():
        from es.ara.envisage.web_viewer.web_viewer_plugin.web_viewer_service import WebViewerService
        return WebViewerService()