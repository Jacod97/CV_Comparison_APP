import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3-Image Viewer")
        self.setGeometry(200, 200, 1800, 700)

        # ===== 메인 레이아웃 =====
        layout = QVBoxLayout()
        self.setLayout(layout)

        # ===== 이미지 표시 영역 =====
        self.img_layout = QHBoxLayout()
        layout.addLayout(self.img_layout)

        # ===== QLabel 3개 생성 =====
        self.labels = []
        for _ in range(3):
            lbl = QLabel("No Image")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("border: 1px solid gray; background-color: #222; color: #fff;")
            self.labels.append(lbl)
            self.img_layout.addWidget(lbl)

        # ===== 이미지 경로 직접 입력 =====
        # ↓↓↓ 여기 부분에 직접 이미지 경로 입력 ↓↓↓
        self.image_paths = [
            "results/origin/concrete_lv1_1.jpg",
            "results/origin/concrete_lv1_2.jpg",
            "results/origin/concrete_lv1_3.jpg"
        ]
        self.show_images(self.image_paths)

    def show_images(self, paths):
        for lbl, path in zip(self.labels, paths):
            pixmap = QPixmap(path)
            lbl.setPixmap(pixmap.scaled(500, 650, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            lbl.setText("")  # 텍스트 제거

        # 남은 빈 슬롯 초기화
        for lbl in self.labels[len(paths):]:
            lbl.clear()
            lbl.setText("No Image")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()

    viewer.show()
    sys.exit(app.exec_())
