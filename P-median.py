import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QFileDialog

def p_median(weights, points, optimized_points, min_distance=0.20, scale=0.01):
    weights = [w * scale for w in weights]  # Scale the weights

    grid = [(i/100, j/100) for i in range(101) for j in range(101)]
    num_grid = len(grid)
    num_points = len(points)

    distance_matrix = np.zeros((num_points, num_grid))
    for i in range(num_points):
        for j in range(num_grid):
            distance = ((points[i][0] - grid[j][0])**2 + (points[i][1] - grid[j][1])**2) ** 0.5
            distance_matrix[i][j] = weights[i] * distance

    # Add penalty to grid points near the already optimized points
    for optimized_point in optimized_points:
        for j in range(num_grid):
            distance_to_optimized_point = ((grid[j][0] - optimized_point[0])**2 + (grid[j][1] - optimized_point[1])**2) ** 0.5
            if distance_to_optimized_point < min_distance:
                distance_matrix[:, j] += 1e6  # Add large penalty

    total_distance = np.sum(distance_matrix, axis=0)
    optimized_point_index = total_distance.argsort()[0]
    optimized_point = grid[optimized_point_index]

    return optimized_point

class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.image = None
        self.pixmap = None
        self.original_pixmap = None
        self.points = []
        self.weights = []
        self.optimized_points = []
        self.optimized_by_algo_points = []  
        self.setGeometry(300, 300, 800, 800)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('P-median Algorithm')
        self.loadImageBtn = QPushButton('Load Image', self)
        self.loadImageBtn.clicked.connect(self.loadImage)

        self.addPointBtn = QPushButton('Add Coordinate', self)
        self.addPointBtn.clicked.connect(self.addCoords)

        self.addOptimizedPointBtn = QPushButton('Add Blue Point', self)
        self.addOptimizedPointBtn.clicked.connect(self.addOptimizedPoint)

        self.optimizeBtn = QPushButton('Optimize', self)
        self.optimizeBtn.clicked.connect(self.optimize)

        self.resetBtn = QPushButton('Reset', self)
        self.resetBtn.clicked.connect(self.reset)

        self.label = QLabel(self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.loadImageBtn)
        vbox.addWidget(self.addPointBtn)
        vbox.addWidget(self.addOptimizedPointBtn)
        vbox.addWidget(self.optimizeBtn)
        vbox.addWidget(self.resetBtn)
        vbox.addWidget(self.label)

        self.setLayout(vbox)

    def loadImage(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        if fname[0] == '':
            return

        self.image = Image.open(fname[0])
        self.pixmap = QPixmap(fname[0])
        self.original_pixmap = self.pixmap.copy()  # Keep a copy of the original image
        self.label.setPixmap(self.pixmap)

    def addCoords(self):
        x, ok = QInputDialog.getInt(self, 'X Coordinate', 'Enter X(0-100):')
        if not ok or x < 0 or x > 100:
            QMessageBox.warning(self, "Warning", "Please enter a valid X coordinate (0-100).")
            return

        y, ok = QInputDialog.getInt(self, 'Y Coordinate', 'Enter Y(0-100):')
        if not ok or y < 0 or y > 100:
            QMessageBox.warning(self, "Warning", "Please enter a valid Y coordinate (0-100).")
            return

        w, ok = QInputDialog.getInt(self, 'Weight', 'Enter weight(0-10):')
        if not ok or w < 0 or w > 10:
            QMessageBox.warning(self, "Warning", "Please enter a valid weight (0-10).")
            return

        self.points.append((x/100, y/100))
        self.weights.append(w)

        self.drawPoints()

    def drawPoints(self):
        if self.pixmap is None:
            return

        painter = QPainter(self.pixmap)
        pen = QPen()
        pen.setWidth(10)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        width, height = self.image.size
        for point in self.points:
            painter.drawPoint(int(point[0] * width), int(point[1] * height))

        painter.end()

        self.label.setPixmap(self.pixmap)

    def addOptimizedPoint(self):
        x, ok = QInputDialog.getInt(self, 'X Coordinate', 'Enter X(0-100):')
        if not ok or x < 0 or x > 100:
            QMessageBox.warning(self, "Warning", "Please enter a valid X coordinate (0-100).")
            return

        y, ok = QInputDialog.getInt(self, 'Y Coordinate', 'Enter Y(0-100):')
        if not ok or y < 0 or y > 100:
            QMessageBox.warning(self, "Warning", "Please enter a valid Y coordinate (0-100).")
            return

        self.optimized_points.append((x/100, y/100))

        self.drawOptimizedPoints()

    def drawOptimizedPoints(self):
        if self.pixmap is None:
            return

        painter = QPainter(self.pixmap)
        pen = QPen()
        pen.setWidth(10)

        # Draw the manually added optimized points in blue
        pen.setColor(Qt.blue)
        painter.setPen(pen)
        width, height = self.image.size
        for point in self.optimized_points:
            painter.drawPoint(int(point[0] * width), int(point[1] * height))

        # Draw the optimized points by algorithm in green
        pen.setColor(Qt.green)
        painter.setPen(pen)
        for point in self.optimized_by_algo_points:
            painter.drawPoint(int(point[0] * width), int(point[1] * height))

        painter.end()

        self.label.setPixmap(self.pixmap)

    def optimize(self):
        if len(self.points) == 0:
            QMessageBox.warning(self, "Warning", "No points added yet.")
            return

        # Moving the previously optimized points to manually optimized ones
        self.optimized_points.extend(self.optimized_by_algo_points)
        self.optimized_by_algo_points.clear()

        optimized_point = p_median(self.weights, self.points, self.optimized_points)
        self.optimized_by_algo_points.append(optimized_point)  

        self.drawOptimizedPoints()

    def reset(self):
        self.points = []
        self.weights = []
        self.optimized_points = []
        self.optimized_by_algo_points = []
        self.pixmap = self.original_pixmap.copy()
        self.label.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())