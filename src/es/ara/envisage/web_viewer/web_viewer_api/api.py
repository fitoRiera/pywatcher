from typing import Protocol

from pyface.tasks.traits_task_pane import TraitsTaskPane
from traits.has_traits import Interface


class IWebViewerService(Interface):

    def create_task_pane(self, page: str) -> TraitsTaskPane:
        '''
        Create a new WebView TaskPanel
        :param scripts: the IDs of the scripts to when the pane is created
        :return: the new WebView TaskPanel
        '''
        ...
