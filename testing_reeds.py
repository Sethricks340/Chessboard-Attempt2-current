import sys
import math
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsView
)
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import QTimer

class CircleInterruptGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interrupt State Viewer")
        self.setGeometry(100, 100, 500, 500)

        # Circle parameters
        self.num_nodes = 10
        self.radius = 150
        self.node_size = 30
        self.center_x = 250
        self.center_y = 250

        # State memory
        self.last_states = [0] * self.num_nodes

        # Scene setup
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Create the circular node indicators
        self.nodes = []
        for i in range(self.num_nodes):
            angle = i * (2 * math.pi / self.num_nodes)
            x = self.center_x + self.radius * math.cos(angle) - self.node_size / 2
            y = self.center_y + self.radius * math.sin(angle) - self.node_size / 2

            circle = QGraphicsEllipseItem(x, y, self.node_size, self.node_size)
            circle.setBrush(QBrush(QColor("red")))
            self.scene.addItem(circle)
            self.nodes.append(circle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleInterruptGUI()
    window.show()
    sys.exit(app.exec())