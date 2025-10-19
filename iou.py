import json

def cal_iou(label, pred):
    box_dict = {}
    (x1, y1), (x2, y2) = label["points"]
    box_dict['answer'] = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
    }

    x,y,w,h = pred['bbox'].values()
    box_dict['predict'] = {
        "x1": x,
        "y1": y,
        "x2": x + w,
        "y2": y + h
    }

    a = box_dict['answer']
    p = box_dict['predict']

    # 교집합 영역 계산
    inter_x1 = max(a['x1'], p['x1'])
    inter_y1 = max(a['y1'], p['y1'])
    inter_x2 = min(a['x2'], p['x2'])
    inter_y2 = min(a['y2'], p['y2'])

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h 

    area_a = (a['x2'] - a['x1']) * (a['y2'] - a['y1'])
    area_p = (p['x2'] - p['x1']) * (p['y2'] - p['y1'])
    union_area = area_a + area_p - inter_area
    iou = inter_area / union_area if union_area > 0 else 0
    box_dict['IoU'] = iou

    return box_dict

def compare_label(label, pred):
    if label['label'] == pred['label']:
        return False
    else:
        return True

def box_info(label_data, pred_data):
    length = len(label_data["shapes"])
    bbox = []
    for i in range(length):
        label = label_data["shapes"][i]
        pred = pred_data[i]

        flag = compare_label(label, pred)
        print(flag)

        box_dict = cal_iou(label, pred)
        box_dict['label'] = label['label']
        if flag:
            box_dict['IoU'] = 0.0
        bbox.append(box_dict)

        print(box_dict['IoU'])

    return bbox

label_path = "./results/answer/c1.json"
pred_path = "./results/predict/c1.json"

with open(label_path, "r", encoding="utf-8") as f:
    label_data = json.load(f)
with open(pred_path, "r", encoding="utf-8") as f:
    pred_data = json.load(f)

bbox = box_info(label_data, pred_data)
# print(bbox)