from pathlib import Path

from envisage.plugin import Plugin
from traits.trait_types import List

from es.ara.envisage.web_viewer.web_viewer_api.api import IWebViewerService


class WwdPlugin(Plugin):
    id = "pywatcher.wwd"
    name = "Plugin that contributes the WWD basic example editor"

    editors = List(contributes_to="pywatcher.ui.main_window.editors")

    def _editors_default(self):
        service = self.application.get_service(IWebViewerService)
        if service is None:
            raise RuntimeError(
                f"Service IWebViewerService is not registered."
            )
        return [service.create_task_pane(self._basic_example_page())]

    @staticmethod
    def _basic_example_page() -> str:
        return Path(__file__).with_name("BasicExample.html").resolve().as_uri()
