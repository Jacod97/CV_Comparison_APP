import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# print(find_common_images(IMG_PATH))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("Image Comparison Viewer")
        self.resize(1600, 800)

        # self._create_menubar("test")
        self._setup_central_widget()

    # 메뉴바 필요하면 주석풀고 만들기
    # def _create_menubar(self,menu_name) -> None:
    #     menubar = self.menuBar()
    #     menubar.setNativeMenuBar(False)
    #     menubar.addMenu(menu_name)

    def _setup_central_widget(self) -> None:
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        common_images = find_common_images(IMG_PATH)
        first_image = common_images[0]

        hbox = QHBoxLayout()
        
        layout.addLayout(hbox)

        for key, path in IMG_PATH.items():
            img, caption = self.show_img(path, first_image, key)

            vbox = QVBoxLayout()
            vbox.addWidget(img)
            vbox.addWidget(caption)

            container = QWidget()
            container.setLayout(vbox)     
            hbox.addWidget(container) 
 
    def show_img(self, path, img_name, caption_text):
        img_path = os.path.join(path, img_name)
        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        caption = QLabel(f"{caption_text} 이미지")
        caption.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(img_path)
        scaled = pixmap.scaled(500, 650, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        img.setPixmap(scaled)
        # caption.setStyleSheet("color: gray; font-size: 14px; margin-top: 4px;")
        return img, caption


# 여기부터는 메서드 작성
import json
with open("config.json", "r", encoding="utf-8") as f:
    file = json.load(f)
IMG_PATH = file['path']

from glob import glob
import os

def find_common_images(paths):
    common_names= None

    for directory in paths.values():
        jpg_files = glob(os.path.join(directory, "*.jpg"))
        jpg_names = {os.path.basename(f).lower() for f in jpg_files}

        # print(f"[jpg_names] {jpg_names} {type(jpg_names)}")

        if not jpg_names:
            return f"{directory}에 jpg파일이 없음"

        if common_names is None:
            common_names = jpg_names
        else:
            common_names &= jpg_names 

    return sorted(common_names) if common_names else []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
