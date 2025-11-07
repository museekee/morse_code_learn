try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile
except ImportError:
    import importlib

    import pip

    print("PySide6 is not installed. Installing...")
    pip.main(["install", "PySide6"])
    PySide6 = importlib.import_module("PySide6")

app = QApplication([])
loader = QUiLoader()
window = loader.load("./ui/portal.ui")

if __name__ == "__main__":
    window.show()
    app.exec()
