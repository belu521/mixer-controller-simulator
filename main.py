# main.py
# Yamaha DM Series Controller Simulator v2.0 - 入口

import sys
from PyQt6.QtWidgets import QApplication
from mixer_simulator.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Yamaha DM Series Controller Simulator")
    app.setApplicationVersion("2.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
