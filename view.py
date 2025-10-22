import os
import json
import cv2
from glob import glob
base_dir = "push_img/origin"

jpg_paths = glob(os.path.join(base_dir, "*.jpg"))
json_paths = glob(os.path.join(base_dir, "*.json"))

for i in range(len(jpg_paths)):
    json_path = json_paths[i]
    print("here!!!!!!!!!!!!!",json_path)
    img_path = jpg_paths[i]
    jpg_name = os.path.basename(img_path)
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
        save_path = os.path.join("results/answer", jpg_name)
    cv2.imwrite(jpg_name, img)

# cv2.imshow("Label Visualization", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()