"""Aplicación de ejemplo con Envisage + Pyface Tasks.

Requisitos aproximados:
    pip install envisage pyface traits traitsui pyqt5

Ejecución:
    python -m src.envisage_app
    o
    python src/envisage_app.py
"""
from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_application import TasksApplication
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from es.ara.envisage.main_window.main_window_plugin import MainWindowPlugin
from es.ara.envisage.web_viewer.web_viewer_plugin.web_viewer_plugin import WebViewerPlugin
from es.ara.envisage.wwd.wwd_plugin import WwdPlugin


def main():
    app = TasksApplication(
        id="pywatcher.envisage_app",
        plugins=[
            CorePlugin(),
            TasksPlugin(),
            MainWindowPlugin(),
            WebViewerPlugin(),
            WwdPlugin(),
        ],
    )
    app.run()


if __name__ == "__main__":
    main()
