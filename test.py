import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QListWidget, QTableWidget, QHeaderView, QSplitter
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from back import ImageData

class ImageViewer(QWidget):
    def __init__(self, side_bar, data_dict, score):
        super().__init__()
        self.setWindowTitle("3-Image Viewer with Sidebar and Table")
        self.setGeometry(200, 200, 2500, 900)
        self.side_bar = side_bar
        self.data_dict = data_dict
        self.score = score

        # ===== 메인 분할 레이아웃 (사이드바 + 본문) =====
        splitter = QSplitter(Qt.Horizontal)
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

        # ===== 사이드바 =====
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        splitter.addWidget(self.sidebar)

        self.sidebar.addItems(self.side_bar)

        # ===== 메인 위젯 =====
        main_widget = QWidget()
        vbox = QVBoxLayout(main_widget)
        splitter.addWidget(main_widget)

        # ===== 이미지 표시 영역 =====
        self.img_layout = QHBoxLayout()
        vbox.addLayout(self.img_layout)

        self.labels = []
        for _ in range(3):
            lbl = QLabel("No Image")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("border: 1px solid gray; background-color: #222; color: #fff;")
            self.img_layout.addWidget(lbl)
            self.labels.append(lbl)

        # ===== 표 영역 =====
        self.table = QTableWidget()
        self.table.setRowCount(3)
        self.table.setColumnCount(2)
        self.table.setFixedSize(2500, 500)
        self.table.setHorizontalHeaderLabels(["ConfusionMatrix", "Count"])
        vbox.addWidget(self.table)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 열 너비 자동 채움
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)    # 행 높이 자동 채움

        # ===== 이미지 경로 직접 입력 =====
        # ↓↓↓ 여기에 직접 이미지 경로 입력 ↓↓↓
        self.image_paths = [
            r"results/origin/concrete_lv1_1.jpg",
            r"results/answer/concrete_lv1_1.jpg",
            r"results/predict/concrete_lv1_1.jpg"
        ]
        self.show_images(self.image_paths)

    def show_images(self, paths):
        for lbl, path in zip(self.labels, paths):
            pixmap = QPixmap(path)
            lbl.setPixmap(pixmap.scaled(800, 650, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            lbl.setText("")

        for lbl in self.labels[len(paths):]:
            lbl.clear()
            lbl.setText("No Image")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data = ImageData("config.json")
    viewer = ImageViewer(
        data.side_bar_list,
        data.img_info,
        data.score
    )
    viewer.show()
    sys.exit(app.exec_())