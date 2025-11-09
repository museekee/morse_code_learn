try:
    from PySide6.QtWidgets import QApplication, QMainWindow
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile
    from pathlib import Path
except ImportError:
    # import importlib
    import pip
    import os

    print("PySide6 is not installed. Installing...")
    pip.main(["install", "PySide6"])
    # QApplication = importlib.import_module("PySide6.QtWidgets").QApplication
    # QUiLoader = importlib.import_module("PySide6.QtUiTools").QUiLoader
    # QFile = importlib.import_module("PySide6.QtCore").QFile
    if os.system(f"python {__file__}") == 0:
        exit(0)
    elif os.system(f"py {__file__}") == 0:
        exit(0)
    elif os.system(f"python3 {__file__}") == 0:
        exit(0)
    else:
        print("Failed to start application. Please run it manually.")
        exit(1)


class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load("./ui/portal.ui")
        self.setCentralWidget(self.ui.centralWidget())
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle(self.ui.windowTitle())
        self.setStyleSheet(self.ui.styleSheet())
        self.setFont(self.ui.font())


if __name__ == "__main__":
    app = QApplication([])
    window = PortalWindow()
    window.show()
    app.exec()
