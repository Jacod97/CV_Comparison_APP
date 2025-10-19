import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QListWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# print(find_common_images(IMG_PATH))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Image Comparison Viewer")
        self.resize(1600, 800)

        # 전체 레이아웃 구성
        central_widget = QWidget(self)                         
        self.setCentralWidget(central_widget)                   
        self.main_layout = QHBoxLayout(central_widget)               

        self.sidebar = self.set_sidebar_widget()                
        self.main_layout.addWidget(self.sidebar)                     

        # 이미지 시각화
        self.img_container = QWidget()                      
        self.main_layout.addWidget(self.img_container)
        self.set_img_widget()

    # 메뉴바 필요하면 주석풀고 만들기
    # def _create_menubar(self,menu_name) -> None:
    #     menubar = self.menuBar()
    #     menubar.setNativeMenuBar(False)
    #     menubar.addMenu(menu_name)
    
    def set_sidebar_widget(self):                       
        sidebar = QListWidget()
        sidebar.addItems(find_common_images(IMG_PATH))
        sidebar.itemClicked.connect(self._on_sidebar_clicked)  
        return sidebar

    def _on_sidebar_clicked(self, item):                    
        filename = item.text()
        # print(f"[INFO] 선택된 이미지: {filename}")
        self.set_img_widget(selected_name=filename) 

    def set_img_widget(self, selected_name=None):
        # 기존 레이아웃 가져오기
        layout = self.img_container.layout()

        # 기존 위젯 정리
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # 공통 이미지 목록과 대상 파일명 선택
        common_images = find_common_images(IMG_PATH)
        img_fname = selected_name if selected_name else common_images[0]

        # 수평 레이아웃 생성
        hbox = QHBoxLayout()
        layout.addLayout(hbox)

        # 이미지 3개 표시
        for key, path in IMG_PATH.items():
            img, caption = self.show_img(path, img_fname, key)

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
