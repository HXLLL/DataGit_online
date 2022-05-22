import cv2
import sys
import os
from tqdm import tqdm

angles = [cv2.cv2.ROTATE_90_CLOCKWISE, cv2.cv2.ROTATE_180, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE]

for f in tqdm(os.listdir(sys.argv[1]), desc="Transforming"):
    f_dir = os.path.normpath(os.path.join(sys.argv[1], f))
    if not os.path.isfile(f_dir):
        continue
    img = cv2.imread(f_dir)
    if img is None:
        continue

    name, ext = os.path.splitext(f_dir)

    i = 1
    for a in angles:
        new = cv2.rotate(img, a)
        i += 1
        cv2.imwrite("%s_%d%s" % (name, i, ext), new)
