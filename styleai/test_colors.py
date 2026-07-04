import cv2
import numpy as np
from sklearn.cluster import KMeans

img = cv2.imread("test.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

pixels = img.reshape((-1, 3))

kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(pixels)

colors = kmeans.cluster_centers_.astype(int)

print("Dominant Colors:")
for color in colors:
    r, g, b = map(int, color)
    print(f"RGB({r}, {g}, {b})")
