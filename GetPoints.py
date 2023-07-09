import cv2
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton, QGraphicsView, QGraphicsScene, QLabel
from PyQt5.QtGui import QPixmap, QImage, QPainter, QCursor
from PyQt5.QtCore import Qt


class MyQGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(MyQGraphicsScene, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            print(f'Normalized Position: ({pos.x()/self.width():.2f}, {pos.y()/self.height():.2f})')


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.HighQualityAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setInteractive(True)
        self.setCursor(QCursor(Qt.CrossCursor))

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())


class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = MyQGraphicsScene()
        self.view = ImageViewer()
        self.view.setScene(self.scene)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Processor')
        self.setGeometry(100, 100, 800, 600)

        # Setup UI Widgets
        self.btn_open = QPushButton('Open Image', self)
        self.btn_open.clicked.connect(self.openImage)

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_open)
        vbox.addWidget(self.view)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        widget.setLayout(vbox)

    def openImage(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open Image', '.', 'Image Files(*.jpg *.png)')

        if fname:
            img = cv2.imread(fname)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, c = img.shape
            qimg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.scene.clear()
            self.scene.setSceneRect(0, 0, w, h)
            self.scene.addPixmap(pixmap)


def main():
    app = QApplication(sys.argv)
    win = ImageWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()