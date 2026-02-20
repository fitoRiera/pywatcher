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

from pywatcher.ui.main_window import MainWindowPlugin


def main():
    app = TasksApplication(
        id="pywatcher.envisage_app",
        plugins=[
            CorePlugin(),
            TasksPlugin(),
            MainWindowPlugin(),
        ],
    )
    app.run()


if __name__ == "__main__":
    main()
