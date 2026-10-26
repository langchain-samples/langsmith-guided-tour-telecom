"""Generate a simple synthetic bill image for the multi-modal demo."""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "sample_bill.png"

img = Image.new("RGB", (640, 400), "white")
d = ImageDraw.Draw(img)
lines = [
    "NORTHWIND MOBILE — Monthly Statement",
    "Account: ACCT-1001   Name: Alex Rivera",
    "",
    "Plan: Unlimited Premium .............. $90.00",
    "Device payment (Pixel 9 Pro) ......... $27.00",
    "Taxes & fees ......................... $11.47",
    "One-time: intl roaming day pass ...... $10.00",
    "--------------------------------------------",
    "Total due ............................ $138.47",
    "(Last month: $92.47)",
]
y = 24
for line in lines:
    d.text((28, y), line, fill="black")
    y += 32
img.save(OUT)
print("wrote", OUT)
