import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, 
    QWidget, QLabel, QHBoxLayout, QListWidget,
    QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QRect

# print(find_common_images(IMG_PATH))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # IOU 정보 담기
        self.files = find_common_files(IMG_PATH)
        self.data_dict = {}
        self.viewer_bboxes = {}
        for file in self.files:
            label_path = os.path.join(IMG_PATH['answer'], f"{file}.json")
            pred_path = os.path.join(IMG_PATH['predict'], f"{file}.json")
            with open(label_path, "r", encoding="utf-8") as f:
                label_data = json.load(f)
            with open(pred_path, "r", encoding="utf-8") as f:
                pred_data = json.load(f)
            bbox = box_info(label_data, pred_data)
            self.data_dict[file] = bbox
            self.viewer_bboxes[file] = to_viewer_bboxes(bbox)
        # ui호출
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
        self.img_container.setLayout(QVBoxLayout())
        self.main_layout.addWidget(self.img_container)
        self.set_img_widget()

    # 메뉴바 필요하면 주석풀고 만들기
    # def _create_menubar(self,menu_name) -> None:
    #     menubar = self.menuBar()
    #     menubar.setNativeMenuBar(False)
    #     menubar.addMenu(menu_name)
    
    def set_sidebar_widget(self):                       
        sidebar = QListWidget()
        sidebar.addItems(find_common_files(IMG_PATH))
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

        # 수평 레이아웃 생성
        hbox = QHBoxLayout()
        layout.addLayout(hbox)

        # 이미지 3개 표시
        fname = selected_name or self.files[0]
        for key, path in IMG_PATH.items():
            img, caption = self.show_img(path, fname, key)

            vbox = QVBoxLayout()
            vbox.addWidget(img)
            vbox.addWidget(caption)

            container = QWidget()
            container.setLayout(vbox)
            hbox.addWidget(container)

    def show_img(self, path, img_name, caption_text):
        img_path = os.path.join(path, f"{img_name}.jpg")
        bboxes = self.viewer_bboxes.get(img_name, [])

        if caption_text.lower() == "predict":
            img = DetectionViewer(img_path, bboxes=bboxes)
            img.doubleClicked.connect(self._on_bbox_clicked)  
        else:
            img = QLabel()
            pixmap = QPixmap(img_path)
            scaled = pixmap.scaled(500, 650, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(scaled)
            img.setAlignment(Qt.AlignCenter)

        caption = QLabel(f"{caption_text} 이미지")
        caption.setAlignment(Qt.AlignCenter)

        return img, caption

    def _on_bbox_clicked(self, box):
        # print(f"[DEBUG] _on_bbox_clicked triggered → {box['label']} / IoU={box['IoU']:.3f}")
        msg = (
            f"라벨: {box['label']}\n"
            f"IoU: {box['IoU']:.3f}\n"
        )
        QMessageBox.information(self, "Detection Info", msg)

    
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QMessageBox

class DetectionViewer(QLabel):
    doubleClicked = pyqtSignal(dict)  # 클릭된 bbox 정보를 보낼 시그널

    def __init__(self, img_path, bboxes=None, parent=None):
        super().__init__(parent)
        self.img_path = img_path
        self.bboxes = bboxes or []
        self.hover_index = None
        self.pixmap_orig = QPixmap(img_path)
        self.setPixmap(self.pixmap_orig.scaled(500, 650, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.setScaledContents(True)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEnabled(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.bboxes:
            return
        painter = QPainter(self)
        scale_x = self.width() / self.pixmap_orig.width()
        scale_y = self.height() / self.pixmap_orig.height()
        for i, box in enumerate(self.bboxes):
            p = box['predict']
            x1, y1 = int(p['x1'] * scale_x), int(p['y1'] * scale_y)
            x2, y2 = int(p['x2'] * scale_x), int(p['y2'] * scale_y)
            width = x2 - x1
            height = y2 - y1
            if i == self.hover_index:
                painter.setPen(QPen(QColor(255, 140, 0), 3))
                painter.fillRect(QRect(x1, y1, width, height), QBrush(QColor(255, 140, 0, 60)))
            else:
                painter.setPen(QPen(QColor(0, 200, 255), 2))
            painter.drawRect(x1, y1, width, height)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handled = self._emit_box_from_pos(event.pos(), source="click")
            if handled:
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            handled = self._emit_box_from_pos(event.pos(), source="double-click")
            if handled:
                return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        updated = False
        if self._ensure_bboxes():
            real_x, real_y, _, _ = self._map_to_image_coordinates(event.pos())
            index, _ = self._find_box_index(real_x, real_y)
            if index != self.hover_index:
                self.hover_index = index
                updated = True
        if updated:
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.hover_index is not None:
            self.hover_index = None
            self.update()
        super().leaveEvent(event)

    def _emit_box_from_pos(self, pos, source):
        action = source.upper()
        print(f"\n[DEBUG] ===== {action} DETECTED =====")
        if not self._ensure_bboxes():
            print(f"[DEBUG] self.bboxes is empty on {source}")
            return False

        click_x, click_y = pos.x(), pos.y()
        print(f"[DEBUG] Clicked position (widget): ({click_x:.2f}, {click_y:.2f})")

        real_x, real_y, _, _ = self._map_to_image_coordinates(pos)
        print(f"[DEBUG] Converted position (image): ({real_x:.2f}, {real_y:.2f})")

        index, box = self._find_box_index(real_x, real_y, verbose=True)
        if box is None:
            print("[DEBUG] No bbox matched click position.")
            return False

        print(f"[DEBUG] HIT! → Box {index} / Label={box['label']}, IoU={box['IoU']:.3f}")
        self.hover_index = index
        self.update()
        self.doubleClicked.emit(box)
        return True

    def _ensure_bboxes(self):
        return bool(self.bboxes) or self._load_bboxes_from_source()

    def _map_to_image_coordinates(self, pos):
        widget_w = max(self.width(), 1)
        widget_h = max(self.height(), 1)
        scale_x = self.pixmap_orig.width() / widget_w
        scale_y = self.pixmap_orig.height() / widget_h
        real_x = pos.x() * scale_x
        real_y = pos.y() * scale_y
        return real_x, real_y, scale_x, scale_y

    def _find_box_index(self, real_x, real_y, verbose=False):
        for i, box in enumerate(self.bboxes):
            p = box['predict']
            if verbose:
                print(f"[DEBUG] Box {i}: ({p['x1']:.1f},{p['y1']:.1f})~({p['x2']:.1f},{p['y2']:.1f})")
            if p['x1'] <= real_x <= p['x2'] and p['y1'] <= real_y <= p['y2']:
                return i, box
        return None, None

    def _load_bboxes_from_source(self):
        base_name = os.path.splitext(os.path.basename(self.img_path))[0]
        label_path = os.path.join(IMG_PATH.get('answer', ''), f"{base_name}.json")
        pred_path = os.path.join(IMG_PATH.get('predict', ''), f"{base_name}.json")

        try:
            with open(label_path, encoding="utf-8") as lf:
                label_data = json.load(lf)
            with open(pred_path, encoding="utf-8") as pf:
                pred_data = json.load(pf)
        except FileNotFoundError:
            print(f"[DEBUG] Annotation files not found for {base_name}")
            return False
        except json.JSONDecodeError as exc:
            print(f"[DEBUG] Failed to parse annotation: {exc}")
            return False

        try:
            raw_boxes = box_info(label_data, pred_data)
            self.bboxes = to_viewer_bboxes(raw_boxes)
        except Exception as exc:  # 폴백 로딩 실패 시 디버깅용 메시지 출력
            print(f"[DEBUG] box_info failed on {base_name}: {exc}")
            self.bboxes = []
            return False

        if not self.bboxes:
            return False

        self.hover_index = None
        self.update()  # 새 박스가 로드되면 다시 그리기
        return True

# 여기부터는 메서드 작성
import json
with open("config.json", "r", encoding="utf-8") as f:
    file = json.load(f)
IMG_PATH = file['path']

from glob import glob
import os

def find_common_files(paths):
    common_basenames = None

    for directory in paths.values():
        files = glob(os.path.join(directory, "*.jpg"))  
        basenames = {os.path.splitext(os.path.basename(f).lower())[0] for f in files}

        if not basenames:
            return []

        if common_basenames is None:
            common_basenames = basenames
        else:
            common_basenames &= basenames

    return sorted(common_basenames) if common_basenames else []

def cal_iou(label, pred):
    (Lx1, Ly1), (Lx2, Ly2) = label["points"]
    x,y,w,h = pred['bbox'].values()
    Px1 = x
    Py1 = y
    Px2 = x+w
    Py2 = y+h

    # 교집합 영역 계산
    inter_x1 = max(Lx1, Px1)
    inter_y1 = max(Ly1, Py1)
    inter_x2 = min(Lx2, Px2)
    inter_y2 = min(Ly2, Py2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h 

    area_a = (Lx2 - Lx1) * (Ly2 - Ly1)
    area_p = (Px2 - Px1) * (Py2 - Py1)
    union_area = area_a + area_p - inter_area
    iou = inter_area / union_area if union_area > 0 else 0

    return iou

def box_info(label_data, pred_data):
    length = len(label_data["shapes"])
    bbox = {}
    bbox['answer'] = []
    bbox['predict'] = []
    bbox['IoU'] = []
    for i in range(length):
        label = label_data["shapes"][i]
        pred = pred_data[i]

        (Lx1, Ly1), (Lx2, Ly2) = label["points"]
        bbox['answer'].append((Lx1, Ly1, Lx2, Ly2, label['label']))
        x,y,w,h = pred['bbox'].values()
        Px1 = x
        Py1 = y
        Px2 = x+w
        Py2 = y+h
        bbox['predict'].append((Px1, Py1, Px2, Py2, pred['label']))
        if label['label'] == pred['label']:
            iou = cal_iou(label, pred)
        else:
            iou = 0.0
        bbox['IoU'].append(iou)

    return bbox

def to_viewer_bboxes(bbox_info):
    if not bbox_info:
        return []

    predicts = bbox_info.get('predict') or []
    ious = bbox_info.get('IoU') or []
    boxes = []
    for idx, pred in enumerate(predicts):
        if len(pred) < 5:
            continue
        x1, y1, x2, y2, label = pred
        iou = ious[idx] if idx < len(ious) else 0.0
        boxes.append({
            'label': label,
            'IoU': iou,
            'predict': {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
        })

    return boxes

data_dict = {}
for file in find_common_files(IMG_PATH):
    label_path = os.path.join(IMG_PATH['answer'], f"{file}.json")
    pred_path = os.path.join(IMG_PATH['predict'], f"{file}.json")
    with open(label_path, "r", encoding="utf-8") as f:
        label_data = json.load(f)
    with open(pred_path, "r", encoding="utf-8") as f:
        pred_data = json.load(f)
    bbox = box_info(label_data, pred_data)
    data_dict[file] = bbox

def Confusion_matrix(data_dict, fname):
    img = data_dict[fname]
    length = min(len(img['answer']), len(img['predict']))
    matrix = {
        "TP" : 0,
        "FP" : 0,
        "FN" : 0
    }

    if len(img['answer']) > len(img['predict']):
        matrix['FN'] += len(img['answer']) - len(img['predict'])

    elif len(img['answer']) < len(img['predict']):
        matrix['FP'] += len(img['answer']) - len(img['predict'])

    for i in range(length):
        _,_,_,_,label = img['answer'][i]
        _,_,_,_,pred = img['predict'][i]

        if label == pred:
            if img['IoU'][i] >= 0.5:
                matrix["TP"] += 1
            else:
                matrix['FP'] += 1
        else:
            matrix['FP'] += 1
    
    return matrix

def Score(data_dict):
    TP = 0
    FP = 0
    FN = 0
    for key in data_dict.keys():
        matrix = Confusion_matrix(data_dict,key)
        TP += matrix["TP"]
        FP += matrix["FP"]
        FN += matrix["FN"]

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0.0

    return {
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1-Score": round(f1, 4),
        "Accuracy": round(accuracy, 4)
    }
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
