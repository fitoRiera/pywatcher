import json
import logging
from pathlib import Path
from typing import List, Optional

from PySide6 import QtCore
from PySide6.QtWebEngineCore import QWebEnginePage
from pyface.tasks.traits_task_pane import TraitsTaskPane

from es.ara.envisage.javascript.javascript_api import IScript, IJavascriptService, ScriptId
from es.ara.envisage.web_viewer.web_viewer_api.api import IWebViewerService
from es.ara.envisage.web_viewer.web_viewer_plugin.web_viewer_service import QWebChannel, WebChannelBackend

logger = logging.getLogger(__name__)


class CommandExecutor:
    def __init__(self, commandName:str):
        self._commandName = commandName

    def execute(self, args:dict):
        raise NotImplementedError('Abstract method not implemented.')


class Event:
    def __init__(self, type:str, source:str, details:dict):
        self.type = type
        self.source = source
        self.details = details


class EventListener:

    def onEvent(self, event:Event):
        raise NotImplementedError('Abstract method not implemented.')


class IOChannel(QtCore.QObject):

    messageReceived = QtCore.Signal(str)
    messageToJavascript = QtCore.Signal(str)
    javascriptResponse = QtCore.Signal(str)

    def __init__(self, page:QWebEnginePage):
        super().__init__(page)
        self._page = page

    def run_javascript(self, method:str, args:str, response_handler:callable=None) -> None:
        if self._page is None:
            logger.warning("No QWebEnginePage asociated for execute Javascript.")
            return

        script = f"window.metadata.{method}({args!r})"

        if response_handler:
            def _on_reply(result):
                nonlocal response_handler
                logger.debug("Response from JS: %s", result)
                if response_handler:
                    response_handler(result)

            self._page.runJavaScript(script, _on_reply)
        else:
            self._page.runJavaScript(script)


class OutputChannel(IOChannel):

    def execute_command(self, name:str, args:dict, response_handler:callable) -> None:
        cmd = {
            'name': name,
            'args': args,
        }
        self.run_javascript('handleCommandCall', json.dumps(cmd), response_handler=response_handler)

    def fire_event(self, event:Event) -> None:
        self.run_javascript('handleEvent', json.dumps(event))


class InputChannel(IOChannel):

    def __init__(self, page:QWebEnginePage):
        super().__init__(page)
        self._executors = {}
        self._listeners = {}

    def add_command_executor(self, name:str, executor:callable) -> None:
        if self._executors.get(executor.name):
            raise ValueError(f'Executor {executor.name} already registered')
        self._executors[executor.name] = executor

    def add_event_listener(self, event_name:str, listener:callable) -> None:
        event_listeners = self._listeners.get(event_name) or []
        if listener in event_listeners:
            raise ValueError(f'Listener already registered')

        event_listeners.append(listener)
        self._listeners[event_name] = event_listeners

    def _handle_command_call(self, name:str, args:dict) -> None:
        executor = self._executors.get(name)
        if executor is None:
            raise ValueError(f'Executor {name} not registered')
        executor(**args)

    def _handle_event(self, event:dict) -> None:
        type = event.get('type')
        listeners = self._listeners.get(type) or []
        if not listeners:
            logger.warning(f'Listeners not registered for type {type}')
        for listener in listeners:
            try:
                listener.onEvent(event)
            except Exception as e:
                logger.exception(f'Error on listenser {listener} processing event {event}')


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
        pane = service.create_task_pane(page)
        pane._configure_web_engine = self.extends_configure_web_engine(pane)
        return pane

    def extends_configure_web_engine(self, pane:TraitsTaskPane):
        original_method = pane._configure_web_engine

        def extended_configure_web_engine(*args, **kwargs):
            original_method(*args, **kwargs)
            self._init_web_channel(pane)

        return extended_configure_web_engine

    @staticmethod
    def _init_web_channel(pane:TraitsTaskPane):
        page = pane._web_page

        backend = WebChannelBackend(page)
        channel = QWebChannel(page)
        channel.registerObject("backend", backend)
        page.setWebChannel(channel)

        # Keep strong refs to avoid QObject/channel being garbage-collected.
        pane._web_backend = backend
        pane._web_channel = channel
