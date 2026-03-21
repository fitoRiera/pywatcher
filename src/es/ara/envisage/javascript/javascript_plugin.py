import logging

from envisage.extension_point import ExtensionPoint
from envisage.plugin import Plugin
from envisage.service_offer import ServiceOffer
from traits.trait_types import List, Instance

from es.ara.envisage.javascript.javascript_api import IScript, SCRIPTS_EXTENSION_POINT, IJavascriptService

logger = logging.getLogger(__name__)


class JavascriptPlugin(Plugin):
    name = 'Javascript plugin'
    version = '1.0'

    service = Instance(IJavascriptService)

    def start(self):
        logger.info('Javascript plugin started')

    def stop(self):
        logger.info('Javascript plugin stopped')


    # Publish own extension points

    scripts = ExtensionPoint(
        List(Instance(IScript)),
        id = SCRIPTS_EXTENSION_POINT,
        desc = """
        This extension point allows others plugins to register new 
        Javascript scripts that could be used inside web pages
        """
    )

    # Contribute to other plugins' extension points

    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        service_offer = ServiceOffer(
            protocol='es.ara.envisage.javascript.javascript_plugin.JavascriptService',
            factory=self._get_service
        )
        return [service_offer]

    def _get_service(self):
        if self.service is None:
            from es.ara.envisage.javascript.javascript_service import JavascriptService
            self.service =  JavascriptService(self.scripts, application=self.application)
        return self.service


    # TODO: pendiente de cambiar la forma de instanciar los editors. Los editores deben crearse invocando un servicio y no como contribuciones a un extension point
    editors = List(contributes_to="pywatcher.ui.main_window.editors")

    def _editors_default(self):
        service = self._get_service()
        if service is None:
            raise RuntimeError(
                f"Service IJavascriptService is not registered."
            )
        return [service.create_task_pane()]
