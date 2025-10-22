from glob import glob
import os
import json

class ImageData:
    def __init__(self, cfg_name):
        with open(cfg_name, "r") as f:
            self.config = json.load(f)

        self.paths = self.config['path']
        self.side_bar_list = list(self.find_common_files())
        self.img_info = {}
        self.score = self.run()

    def find_common_files(self):
        common_basenames = None

        for directory in self.paths.values():
            files = glob(os.path.join(directory, "*.jpg"))  
            basenames = {os.path.splitext(os.path.basename(f).lower())[0] for f in files}

            if not basenames:
                return []

            if common_basenames is None:
                common_basenames = basenames
            else:
                common_basenames &= basenames

        return sorted(common_basenames) if common_basenames else []

    def box_info(self, label_data, pred_data):
        bbox = {
            'answer': [],
            'predict': [],
            'IoU': [],
            'TP': 0,
            'FP': 0,
            'FN': 0
        }
        matched = set()

        for label in label_data["shapes"]:
            (Lx1, Ly1), (Lx2, Ly2) = label["points"]
            label_cls = label["label"]
            bbox['answer'].append((Lx1, Ly1, Lx2, Ly2, label_cls))

            best_iou = 0
            best_idx = -1

            for i, pred in enumerate(pred_data):
                Px1, Py1, Px2, Py2 = pred['box']
                iou = cal_iou(Lx1, Ly1, Lx2, Ly2, Px1, Py1, Px2, Py2)
                if iou > best_iou:
                    best_iou = iou
                    best_idx = i

            if best_idx >= 0:
                matched.add(best_idx)
                pred = pred_data[best_idx]
                Px1, Py1, Px2, Py2 = pred['box']
                pred_cls = pred['cls']
                bbox['predict'].append((Px1, Py1, Px2, Py2, pred_cls))
                bbox['IoU'].append(best_iou)

                # === TP/FP 판단 ===
                if label_cls == pred_cls:
                    if best_iou >= 0.5:
                        bbox['TP'] += 1
                    else:
                        bbox['FP'] += 1
                else:
                    bbox['FP'] += 1
            else:
                bbox['predict'].append((0, 0, 0, 0, None))
                bbox['IoU'].append(0.0)
                bbox['FN'] += 1

        # === pred가 더 많을 경우 남은 예측은 FP 처리 ===
        if len(pred_data) > len(label_data["shapes"]):
            for i, pred in enumerate(pred_data):
                if i not in matched:
                    Px1, Py1, Px2, Py2 = pred['box']
                    bbox['answer'].append((0, 0, 0, 0, None))
                    bbox['predict'].append((Px1, Py1, Px2, Py2, pred['cls']))
                    bbox['IoU'].append(0.0)
                    bbox['FP'] += 1

        return bbox
        
    def Score(self):
        TP = FP = FN = 0
        for val in self.img_info.values():
            TP += val["TP"]
            FP += val["FP"]
            FN += val["FN"]

        precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0.0

        return {
            "TP": TP, "FP": FP, "FN": FN,
            "Precision": round(precision, 4),
            "Recall": round(recall, 4),
            "F1-Score": round(f1, 4),
            "Accuracy": round(accuracy, 4)
        }

    def run(self):
        for fname in self.side_bar_list:
            pred_path = os.path.join(self.paths['predict'], f"{fname}.json")
            label_path = os.path.join(self.paths['answer'], f"{fname}.json")

            with open(pred_path, "r") as f:
                pred_json = json.load(f)
            with open(label_path, "r") as f:
                label_json = json.load(f)

            bbox = self.box_info(label_json, pred_json)
            self.img_info[fname] = bbox
        
        score = self.Score()
        return score

def cal_iou(Lx1, Ly1, Lx2, Ly2, Px1, Py1, Px2, Py2):
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
    return round(iou,4)

# data = ImageData("config.json")
# print(data.score)