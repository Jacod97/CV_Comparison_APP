import os
import json
import cv2
from glob import glob
# base_dir = "push_img/origin"

# jpg_paths = glob(os.path.join(base_dir, "*.jpg"))
# json_paths = glob(os.path.join(base_dir, "*.json"))

# for i in range(len(jpg_paths)):
#     json_path = json_paths[i]
#     print("here!!!!!!!!!!!!!",json_path)
#     img_path = jpg_paths[i]
#     jpg_name = os.path.basename(img_path)
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     img = cv2.imread(img_path)

#     for shape in data["shapes"]:
#         label = shape["label"]
#         (x1, y1), (x2, y2) = shape["points"]

#         cv2.rectangle(
#             img,
#             (int(x1), int(y1)),
#             (int(x2), int(y2)),
#             (0, 255, 0),
#             2
#         )

#         cv2.putText(
#             img,
#             label,
#             (int(x1), max(20, int(y1) - 10)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.7,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA
#         )
#         save_path = os.path.join("results/answer", jpg_name)
#     cv2.imwrite(jpg_name, img)

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 데이터
plot_dict = {
    'TP': 17, 'FP': 2, 'FN': 3, 'TN': 0,
    'Precision': 0.8947, 'Recall': 0.85,
    'F1-Score': 0.8718, 'Accuracy': 0.7727
}

# Confusion Matrix
matrix = np.array([
    [plot_dict['TP'], plot_dict['FP']],
    [plot_dict['FN'], plot_dict['TN']]
])

# 성능 지표 DataFrame
metrics_df = pd.DataFrame({
    'Metric': ['Precision', 'Recall', 'F1-Score', 'Accuracy'],
    'Value': [plot_dict['Precision'], plot_dict['Recall'],
              plot_dict['F1-Score'], plot_dict['Accuracy']]
})

# 서브플롯 구성
fig, axes = plt.subplots(2, 1, figsize=(5, 8), gridspec_kw={'height_ratios': [2, 1]})

# 1️⃣ Confusion Matrix
sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Predicted Positive', 'Predicted Negative'],
            yticklabels=['Actual Positive', 'Actual Negative'],
            cbar=False, ax=axes[0],
            vmin=0.1, vmax=0.1)
axes[0].set_title("Confusion Matrix", fontsize=14)

# 2️⃣ Performance Metrics (단색 표 스타일)
sns.heatmap(metrics_df.set_index('Metric'),
            annot=True, fmt=".4f",
            cmap='Greens', cbar=False,
            linewidths=0.5, ax=axes[1],
            vmin=0, vmax=0,  # 색상 통일
            annot_kws={'ha': 'center', 'fontsize': 11})

axes[1].set_title("Performance Metrics", fontsize=12)
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].tick_params(left=False, bottom=False)

plt.tight_layout()
plt.show()



