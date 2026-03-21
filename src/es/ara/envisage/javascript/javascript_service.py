from pathlib import Path
from typing import List, Optional

from es.ara.envisage.javascript.javascript_api import IScript, IJavascriptService, ScriptId
from es.ara.envisage.web_viewer.web_viewer_api.api import IWebViewerService


class JavascriptService(IJavascriptService):

    def __init__(self, scripts:List[IScript], application: Optional[object] = None):
        super().__init__()
        self._scripts_map = self._create_scripts_map(scripts)
        self._application = application

    @staticmethod
    def _create_scripts_map(scripts:List[IScript]):
        scripts_map = {}
        for script in scripts:
            scripts_map[f'{script.id.name}.{script.id.version}'] = script
        return scripts_map

    def create_task_pane(self, scripts: List[ScriptId]=None):
        scripts = [] if scripts is None else scripts

        if self._application is None:
            raise RuntimeError("Envisage application is not set; cannot obtain IWebViewerService.")

        service = self._application.get_service(IWebViewerService)
        if service is None:
            raise RuntimeError("Service IWebViewerService is not registered.")

        page = Path(__file__).with_name("JavascriptBasePage.html").resolve().as_uri()
        return service.create_task_pane(page)
