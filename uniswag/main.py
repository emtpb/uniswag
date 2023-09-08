"""Main module."""

import sys
from os import path

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from uniswag.device_properties.gen_properties import GenProperties
from uniswag.device_properties.osc_properties import OscProperties
from uniswag.front_to_back_connector import FrontToBackConnector


def main():

    # Material, Universal, Fusion
    sys.argv += ['--style', 'Fusion']

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    front_to_back_connector = FrontToBackConnector()
    osc_properties = OscProperties(front_to_back_connector)
    gen_properties = GenProperties(front_to_back_connector)

    engine.rootContext().setContextProperty('FrontToBackConnector', front_to_back_connector)
    engine.rootContext().setContextProperty('OscProperties', osc_properties)
    engine.rootContext().setContextProperty('GenProperties', gen_properties)

    main_qml = path.join(path.dirname(__file__), 'qml', 'Main.qml')
    engine.load(main_qml)

    front_to_back_connector.start_device_list_updates()

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
