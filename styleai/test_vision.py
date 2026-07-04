import cv2
import base64
from ollama import chat

img = cv2.imread("test.png")

h, w = img.shape[:2]

if max(h, w) > 800:
    scale = 800 / max(h, w)
    img = cv2.resize(img, (int(w * scale), int(h * scale)))

cv2.imwrite("small_test.png", img)

with open("small_test.png", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = chat(
    model="qwen2.5vl",
    messages=[
        {
            "role": "user",
            "content": "Describe this outfit and recommend accessories.",
            "images": [image_b64]
        }
    ]
)

print(response["message"]["content"])
