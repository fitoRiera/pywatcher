
from envisage.core_plugin import CorePlugin
from envisage.plugin import Plugin
from envisage.ui.tasks.api import TaskFactory, TasksApplication, TasksPlugin

from pyface.action.api import StatusBarManager
from pyface.tasks.action.api import TaskAction
from pyface.tasks.action.schema import SMenu, SMenuBar, SToolBar
from pyface.tasks.api import PaneItem, Task, TaskLayout, TraitsDockPane, TraitsTaskPane
from traits.api import List, Str
from traitsui.api import Item, TextEditor, UItem, View
from pywatcher.ui.web_view_task import WebViewTaskPane


class EditorPrincipalPane(TraitsTaskPane):
    """Panel central que actúa como editor principal."""

    id = "pywatcher.editor_principal"
    name = "Editor principal"
    contenido = Str("Escribe aquí...\n\nEste es el panel central.")

    view = View(
        UItem(
            "contenido",
            style="custom",
            editor=TextEditor(multi_line=True),
            springy=True,
        ),
        resizable=True,
    )

    def create(self, parent):
        super().create(parent)
        # Color distintivo para el panel central.
        self.control.setStyleSheet("background-color: #FFF5CC;")


class PanelLateralPane(TraitsDockPane):
    """Panel lateral acoplable."""

    id = "pywatcher.panel_lateral"
    name = "Panel lateral"
    info = Str("Panel lateral\n\nContenido de ejemplo.")

    view = View(
        Item(
            "info",
            style="readonly",
            editor=TextEditor(multi_line=True),
            show_label=False,
            springy=True,
        ),
        resizable=True,
    )

    def create(self, parent):
        super().create(parent)
        # Color distintivo para el panel lateral.
        self.control.setStyleSheet("background-color: #DFF7E2;")


class MainWindowTask(Task):
    id = "pywatcher.ui.main_window.task"
    name = "PyWatcher - Envisage"

    def create_central_pane(self):
        return WebViewTaskPane()

    def create_dock_panes(self):
        return [PanelLateralPane()]

    def _default_layout_default(self):
        return TaskLayout(right=PaneItem("pywatcher.panel_lateral"))

    def _status_bar_default(self):
        return StatusBarManager(message="Estado: aplicación iniciada")

    def _menu_bar_default(self):
        return SMenuBar(
            SMenu(
                TaskAction(
                    name="Actualizar estado",
                    method="actualizar_estado",
                ),
                id="menu_app",
                name="&Aplicación",
            )
        )

    def _tool_bars_default(self):
        return [
            SToolBar(
                TaskAction(
                    name="Actualizar",
                    method="actualizar_estado",
                ),
                id="toolbar_principal",
                name="Principal",
            )
        ]

    def activated(self):
        super().activated()
        if self.window is not None and self.window.control is not None:
            # Colores para distinguir menú, toolbar y barra de estado.
            self.window.control.setStyleSheet(
                """
                QMenuBar { background-color: #D8E9FF; }
                QToolBar { background-color: #D8F6EC; spacing: 6px; }
                QStatusBar { background-color: #FFD8D8; }
                """
            )

    def actualizar_estado(self):
        if self.status_bar is not None:
            self.status_bar.message = "Estado: acción ejecutada"


class MainWindowPlugin(Plugin):
    id = "pywatcher.ui.main_window"
    name = "Plugin that define the default main window"
    tasks = List(contributes_to="envisage.ui.tasks.tasks")

    def _tasks_default(self):
        return [
            TaskFactory(
                id="pywatcher.ui.main_window.task",
                name="Main window task",
                factory=MainWindowTask,
            )
        ]
