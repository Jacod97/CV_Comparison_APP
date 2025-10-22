import json
import os
from glob import glob

def box_info(label_data, pred_data):
    bbox = {'answer': [], 'predict': [], 'IoU': []}
    matched = set()

    for label in label_data["shapes"]:
        (Lx1, Ly1), (Lx2, Ly2) = label["points"]
        bbox['answer'].append((Lx1, Ly1, Lx2, Ly2, label['label']))

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
            bbox['predict'].append((Px1, Py1, Px2, Py2, pred['cls']))
            bbox['IoU'].append(best_iou)
        else:
            bbox['predict'].append((0, 0, 0, 0, None))
            bbox['IoU'].append(0.0)
    
    # pred가 더 많을 경우 남은 예측만 추가
    if len(pred_data) > len(label_data["shapes"]):
        for i, pred in enumerate(pred_data):
            if i not in matched:
                Px1, Py1, Px2, Py2 = pred['box']
                bbox['answer'].append((0, 0, 0, 0, None))
                bbox['predict'].append((Px1, Py1, Px2, Py2, pred['cls']))
                bbox['IoU'].append(0.0)

    return bbox

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

def Confusion_matrix(img_info):
    length = len(img_info['answer'])
    matrix = {
        "TP" : 0,
        "FP" : 0,
        "FN" : 0
    }

    for i in range(length):
        _,_,_,_,label = img_info['answer'][i]
        _,_,_,_,pred = img_info['predict'][i]
        
        if pred is None:
            matrix["FN"] += 1
            continue

        if label == pred:
            if img_info['IoU'][i] >= 0.5:
                matrix["TP"] += 1
            else:
                matrix['FP'] += 1
        else:
            matrix['FP'] += 1
    
    return matrix

def Score(img_infos):
    TP = 0
    FP = 0
    FN = 0
    for img_info in img_infos:
        matrix = Confusion_matrix(img_info)
        TP += matrix["TP"]
        FP += matrix["FP"]
        FN += matrix["FN"]

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else 0.0

    return {
        "TP" : TP, "FP" : FP, "FN" : FN,
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1-Score": round(f1, 4),
        "Accuracy": round(accuracy, 4)
    }

result_dir = "../data/test/test_excute/result"
# pred_dir = "../data/test/0923_test/hbeam/inference/all"
# label_dir = "../data/test/0923_test/hbeam/json_img"
pred_dir = "results/predict"
label_dir = "results/answer"
pred_paths = glob(os.path.join(pred_dir, "*.json"))
label_paths = glob(os.path.join(label_dir, "*.json"))

img_infos = []
for i in range(len(pred_paths)):
    with open(pred_paths[i], "r") as f:
        pred_json = json.load(f)
    with open(label_paths[i], "r") as f:
        label_json = json.load(f)
        
    bbox = box_info(label_json, pred_json)
    print(bbox)
    img_infos.append(bbox)
    
score = Score(img_infos)
print(score)
# {'TP': 60, 'FP': 16, 'FN': 10, 'Precision': 0.7895, 'Recall': 0.8571, 'F1-Score': 0.8219, 'Accuracy': 0.6977}
# {'TP': 80, 'FP': 37, 'FN': 8, 'Precision': 0.6838, 'Recall': 0.9091, 'F1-Score': 0.7805, 'Accuracy': 0.64}
# 3100 {'TP': 84, 'FP': 28, 'FN': 10, 'Precision': 0.75, 'Recall': 0.8936, 'F1-Score': 0.8155, 'Accuracy': 0.6885}h
# 3100 {'TP': 56, 'FP': 16, 'FN': 13, 'Precision': 0.7778, 'Recall': 0.8116, 'F1-Score': 0.7943, 'Accuracy': 0.6588}c