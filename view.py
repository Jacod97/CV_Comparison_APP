import os
import json
import cv2

base_dir = "../data/test/lv_test"
json_name = "concrete_lv1_1.json"
jpg_name  = "concrete_lv1_1.jpg"

json_path = os.path.join(base_dir, json_name)
img_path  = os.path.join(base_dir, jpg_name)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

img = cv2.imread(img_path)

for shape in data["shapes"]:
    label = shape["label"]
    (x1, y1), (x2, y2) = shape["points"]

    cv2.rectangle(
        img,
        (int(x1), int(y1)),
        (int(x2), int(y2)),
        (0, 255, 0),
        2
    )

    cv2.putText(
        img,
        label,
        (int(x1), max(20, int(y1) - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

# cv2.imshow("Label Visualization", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
cv2.imwrite(jpg_name, img)