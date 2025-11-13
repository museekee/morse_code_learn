try:
    from PySide6.QtCore import QFile
    from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtGui import QPixmap, QPainter
    from PySide6.QtCore import Qt
    from PySide6.QtSvg import QSvgRenderer
    import darkdetect
except ImportError:
    import pip
    import os

    print("Requirements are not installed. Installing...")
    pip.main(["install", "PySide6", "darkdetect"])

    if os.system(f"python \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"py \"{__file__}\"") == 0:
        exit(0)
    elif os.system(f"python3 \"{__file__}\"") == 0:
        exit(0)
    else:
        print("Failed to start application. Please run it manually.")
        exit(1)

def getPixmap(image_name: str) -> QPixmap:
    theme = "dark" if darkdetect.isDark() else "light"
    image_path = f"./assets/img/{theme}/{image_name}"
    return QPixmap(image_path)

def getPixmapedSvg(image_name: str, width: int, height: int) -> QPixmap:
    theme = "dark" if darkdetect.isDark() else "light"
    image_path = f"./assets/img/{theme}/{image_name}"
    renderer = QSvgRenderer(image_path)

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return pixmap

class MemorizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.ui = loader.load("./assets/memorize.ui", self)

        self.setLayout(self.ui.layout())
        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.size())
        self.setFont(self.ui.font())

        self.ui.NumberImage.setPixmap(getPixmapedSvg("숫자기호.svg", self.width()*3, self.height()*3).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        self.ui.EngImage.setPixmap(getPixmapedSvg("알파벳.svg", self.width()*3, self.height()*3).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        self.ui.HangulImage.setPixmap(getPixmapedSvg("한글.svg", self.width()*3, self.height()*3).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        
        self.ui.buttonBox.accepted.connect(self.on_ok_clicked)

    def on_ok_clicked(self):
        self.accept()

class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.ui = loader.load("./assets/portal.ui")
        self.setCentralWidget(self.ui.centralWidget())
        self.setGeometry(self.ui.geometry())
        self.setWindowTitle(self.ui.windowTitle())
        self.setStyleSheet(self.ui.styleSheet())
        self.setFont(self.ui.font())

        self.ui.btnMemorize.clicked.connect(self.on_btnMemorize_clicked)

    def on_btnMemorize_clicked(self):
        dialog = MemorizeDialog(self)
        dialog.show()


if __name__ == "__main__":
    app = QApplication([])
    window = PortalWindow()
    window.show()
    app.exec()
