from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from core.smith_chart_view import SmithChartView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smith Chart Qt Editor")
        # self.setGeometry(100, 100, 800, 600)
        # self.setMinimumSize(800, 600)
        # self.setMaximumSize(1600, 1200)

        # Initialize the SmithChartView


        self.view = SmithChartView()
        self.init_ui()

    def init_ui(self):
        add_point = QPushButton("Add Point")
        add_arrow = QPushButton("Add Arrow")
        add_text = QPushButton("Add Text")
        add_circle = QPushButton("Add Circle")

        add_point.clicked.connect(self.view.add_point)
        add_arrow.clicked.connect(self.view.add_arrow)
        add_text.clicked.connect(self.view.add_text)
        add_circle.clicked.connect(self.view.add_circle)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_point)
        button_layout.addWidget(add_arrow)
        button_layout.addWidget(add_text)
        button_layout.addWidget(add_circle)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


