import cv2
import sys
import os
from tqdm import tqdm

scale = 0.6

for f in tqdm(os.listdir(sys.argv[1]), desc="Transforming"):
    f_dir = os.path.normpath(os.path.join(sys.argv[1], f))
    if not os.path.isfile(f_dir):
        continue
    img = cv2.imread(f_dir)
    if img is None:
        continue

    w = int(img.shape[1] * scale)
    h = int(img.shape[0] * scale)

    new = cv2.resize(img, (w, h))

    cv2.imwrite(f_dir, new)
