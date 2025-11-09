try:
    from PySide6.QtCore import QFile
    from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
    from PySide6.QtUiTools import QUiLoader
except ImportError:
    import pip
    import os

    print("PySide6 is not installed. Installing...")
    pip.main(["install", "PySide6"])

    if os.system(f"python {__file__}") == 0:
        exit(0)
    elif os.system(f"py {__file__}") == 0:
        exit(0)
    elif os.system(f"python3 {__file__}") == 0:
        exit(0)
    else:
        print("Failed to start application. Please run it manually.")
        exit(1)


class MemorizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.ui = loader.load("./ui/memorize.ui", self)

        self.setLayout(self.ui.layout())
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        self.setFont(self.ui.font())


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

        self.ui.btnMemorize.clicked.connect(self.on_btnMemorize_clicked)

    def on_btnMemorize_clicked(self):
        dialog = MemorizeDialog(self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication([])
    window = PortalWindow()
    window.show()
    app.exec()
