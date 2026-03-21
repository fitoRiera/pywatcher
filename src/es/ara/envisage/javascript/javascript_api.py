from abc import ABC, abstractmethod
from typing import List

from traits.has_traits import Interface

SCRIPTS_EXTENSION_POINT = 'es.ara.envisage.javascript.scripts'


class ScriptId:

    def __init__(self, name:str, version:str):
        self.name = name
        self.version = version


class IScript(Interface):
    id: ScriptId

    def get_content(self):
        '''
        Returns the content of the script
        :return: The content of the script
        '''
        ...


class IJavascriptService(ABC):

    @abstractmethod
    def create_task_pane(self, scripts:List[ScriptId]=[]):
        '''
        Create a web view task pane that loads all the given scripts
        :param scripts: the scripts to load
        :return: a new web view
        '''
        ...