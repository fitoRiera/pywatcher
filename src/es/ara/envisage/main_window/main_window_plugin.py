from envisage.extension_point import ExtensionPoint
from envisage.plugin import Plugin
from envisage.ui.tasks.api import TaskFactory

from pyface.action.api import StatusBarManager
from pyface.qt import QtWidgets
from pyface.tasks.action.api import TaskAction
from pyface.tasks.action.schema import SMenu, SMenuBar, SToolBar
from pyface.tasks.api import PaneItem, Task, TaskLayout, TraitsDockPane, TraitsTaskPane
from traits.api import Instance, List, Str, observe
from traitsui.api import Item, TextEditor, UItem, View


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


class TabbedEditorsTaskPane(TraitsTaskPane):
    """Panel con pestañas, una por cada EditorTaskPane registrado."""

    id = "pywatcher.tabbed_editors"
    name = "Editors"
    editors = List(Instance(TraitsTaskPane))

    def __init__(self, **traits):
        super().__init__(**traits)
        self._editor_panes: list[TraitsTaskPane] = []

    def create(self, parent):
        self.control = QtWidgets.QTabWidget(parent)
        self._editor_panes = self.editors
        self._rebuild_tabs()

    def destroy(self):
        self._clear_editor_panes()
        super().destroy()

    @observe("editors.items")
    def _editors_updated(self, event):
        if self.control is not None:
            self._rebuild_tabs()

    def _rebuild_tabs(self):
        current_task_panes = list(self._editor_panes)
        new_task_panes = [e for e in self.editors if e not in current_task_panes]
        old_task_panes = [e for e in current_task_panes if e not in self.editors]

        for task_pane in old_task_panes:
            self._editor_panes.remove(task_pane)
            task_pane.destroy()

        for task_pane in new_task_panes:
            self._editor_panes.append(task_pane)

        self.control.clear()

        for pane in self._editor_panes:
            label = getattr(pane, "label", None) or pane.id
            if pane.control is None:
                pane.task = self.task
                pane.create(self.control)
            if pane.control is not None:
                self.control.addTab(pane.control, label)

        if self.control.count() == 0:
            self.control.addTab(
                QtWidgets.QLabel("No hay editores registrados en extension point 'editors'."),
                "Sin editores",
            )

    def _clear_editor_panes(self):
        for pane in self._editor_panes:
            pane.destroy()
        self._editor_panes = []


class MainWindowTask(Task):
    id = "pywatcher.ui.main_window.task"
    name = "PyWatcher - Envisage"
    editors = List(Instance(TraitsTaskPane))

    def create_central_pane(self):
        pane = TabbedEditorsTaskPane()
        pane.editors = self.editors
        return pane

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

    editors = ExtensionPoint(
        List(Instance(TraitsTaskPane)),
        id="pywatcher.ui.main_window.editors",
    )

    def _tasks_default(self):
        return [
            TaskFactory(
                id="pywatcher.ui.main_window.task",
                name="Main window task",
                factory=self._create_main_window,
            )
        ]

    def _create_main_window(self, **traits) -> Task:
        task = MainWindowTask(**traits)
        task.editors = self.editors
        return task
