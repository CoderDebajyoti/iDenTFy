"""
Script to generate synthetic Indian government identity documents:
1. sample_valid_passport.jpg (Republic of India - Aarav Sharma)
2. sample_expired_passport.jpg (Republic of India - Rajesh Verma, Expired)
3. sample_blacklisted_license.jpg (Indian Driving Licence - Vikram Singh, Blacklisted)
4. sample_face_portrait.jpg (Biometric face probe)
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_samples")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_realistic_face(draw, x, y, w, h):
    # Head contour
    draw.ellipse([(x, y), (x + w, y + h)], fill=(235, 205, 180), outline=(140, 100, 70), width=2)
    # Hair
    draw.chord([(x - 4, y - 6), (x + w + 4, y + int(h * 0.45))], start=180, end=360, fill=(40, 30, 25))
    # Eyes
    eye_y = y + int(h * 0.42)
    draw.ellipse([(x + int(w * 0.22), eye_y), (x + int(w * 0.38), eye_y + 12)], fill=(255, 255, 255), outline=(60, 40, 30), width=1)
    draw.ellipse([(x + int(w * 0.27), eye_y + 2), (x + int(w * 0.33), eye_y + 10)], fill=(40, 25, 15))
    draw.ellipse([(x + int(w * 0.62), eye_y), (x + int(w * 0.78), eye_y + 12)], fill=(255, 255, 255), outline=(60, 40, 30), width=1)
    draw.ellipse([(x + int(w * 0.67), eye_y + 2), (x + int(w * 0.73), eye_y + 10)], fill=(40, 25, 15))
    # Eyebrows
    draw.line([(x + int(w * 0.20), eye_y - 6), (x + int(w * 0.40), eye_y - 8)], fill=(40, 30, 25), width=3)
    draw.line([(x + int(w * 0.60), eye_y - 8), (x + int(w * 0.80), eye_y - 6)], fill=(40, 30, 25), width=3)
    # Nose
    draw.line([(x + int(w * 0.50), eye_y + 10), (x + int(w * 0.48), y + int(h * 0.65)), (x + int(w * 0.55), y + int(h * 0.65))], fill=(160, 120, 90), width=2)
    # Mouth
    draw.line([(x + int(w * 0.35), y + int(h * 0.78)), (x + int(w * 0.65), y + int(h * 0.78))], fill=(170, 70, 70), width=3)

def generate_valid_passport():
    img = Image.new("RGB", (900, 620), color=(248, 250, 252))
    d = ImageDraw.Draw(img)

    # Top Header - Indian Passport Navy Blue
    d.rectangle([(0, 0), (900, 85)], fill=(15, 23, 42))
    d.text((30, 18), "REPUBLIC OF INDIA  |  भारत गणराज्य", fill=(255, 215, 0))
    d.text((30, 48), "PASSPORT  /  पासपोर्ट  (Type P - IND)", fill=(226, 232, 240))

    # Security microprint background watermark lines
    for line_y in range(95, 480, 25):
        d.line([(0, line_y), (900, line_y)], fill=(241, 245, 249), width=1)

    # Details
    fields = [
        ("COUNTRY CODE", "IND"),
        ("PASSPORT NO.", "Z6549210"),
        ("SURNAME", "SHARMA"),
        ("GIVEN NAMES", "AARAV"),
        ("NATIONALITY", "INDIAN / IND"),
        ("SEX", "M"),
        ("DATE OF BIRTH", "15 AUG 1995"),
        ("PLACE OF BIRTH", "NEW DELHI, INDIA"),
        ("DATE OF ISSUE", "15 AUG 2020"),
        ("DATE OF EXPIRY", "14 AUG 2030"),
    ]

    y_pos = 105
    for lbl, val in fields:
        d.text((40, y_pos), lbl, fill=(100, 116, 139))
        d.text((230, y_pos), val, fill=(15, 23, 42))
        y_pos += 35

    # Biometric Portrait Box
    d.rectangle([(620, 105), (860, 420)], fill=(240, 243, 246), outline=(37, 99, 235), width=2)
    d.rectangle([(620, 105), (860, 125)], fill=(37, 99, 235))
    d.text((640, 108), "BIOMETRIC PHOTO - IND", fill=(255, 255, 255))
    # Draw face inside
    draw_realistic_face(d, 665, 150, 150, 200)

    # MRZ Machine Readable Zone
    d.rectangle([(20, 480), (880, 595)], fill=(15, 23, 42), outline=(56, 189, 248), width=1)
    d.text((35, 500), "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<", fill=(56, 189, 248))
    d.text((35, 545), "Z6549210<2IND9508152M3008144<<<<<<<<<<<<<<08", fill=(56, 189, 248))

    path = os.path.join(OUTPUT_DIR, "sample_valid_passport.jpg")
    img.save(path, format="JPEG", quality=95)
    print(f"Generated: {path}")

def generate_expired_passport():
    img = Image.new("RGB", (900, 620), color=(253, 248, 246))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([(0, 0), (900, 85)], fill=(30, 41, 59))
    d.text((30, 18), "REPUBLIC OF INDIA  |  भारत गणराज्य", fill=(212, 175, 55))
    d.text((30, 48), "PASSPORT  /  पासपोर्ट  (Type P - IND)", fill=(203, 213, 225))

    # Details
    fields = [
        ("COUNTRY CODE", "IND"),
        ("PASSPORT NO.", "Z1102945"),
        ("SURNAME", "VERMA"),
        ("GIVEN NAMES", "RAJESH"),
        ("NATIONALITY", "INDIAN / IND"),
        ("SEX", "M"),
        ("DATE OF BIRTH", "12 MAY 1980"),
        ("PLACE OF BIRTH", "LUCKNOW, INDIA"),
        ("DATE OF ISSUE", "10 JAN 2012"),
        ("DATE OF EXPIRY", "09 JAN 2022 (EXPIRED)"),
    ]

    y_pos = 105
    for lbl, val in fields:
        d.text((40, y_pos), lbl, fill=(100, 116, 139))
        color = (220, 38, 38) if "EXPIRED" in val else (15, 23, 42)
        d.text((230, y_pos), val, fill=color)
        y_pos += 35

    # Portrait Box
    d.rectangle([(620, 105), (860, 420)], fill=(240, 243, 246), outline=(100, 116, 139), width=2)
    draw_realistic_face(d, 665, 150, 150, 200)

    # MRZ Machine Readable Zone
    d.rectangle([(20, 480), (880, 595)], fill=(15, 23, 42))
    d.text((35, 500), "P<INDVERMA<<RAJESH<<<<<<<<<<<<<<<<<<<<<<<<<<", fill=(148, 163, 184))
    d.text((35, 545), "Z11029455IND8005124M2201091<<<<<<<<<<<<<<06", fill=(148, 163, 184))

    path = os.path.join(OUTPUT_DIR, "sample_expired_passport.jpg")
    img.save(path, format="JPEG", quality=95)
    print(f"Generated: {path}")

def generate_blacklisted_license():
    img = Image.new("RGB", (900, 560), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Header - Transport Dept
    d.rectangle([(0, 0), (900, 80)], fill=(30, 58, 138))
    d.text((30, 16), "UNION OF INDIA  |  DRIVING LICENCE", fill=(255, 255, 255))
    d.text((30, 46), "MINISTRY OF ROAD TRANSPORT & HIGHWAYS (SARATHI)", fill=(191, 219, 254))

    fields = [
        ("DL NO.", "DL04202300789"),
        ("NAME", "VIKRAM SINGH"),
        ("S/O", "HARBHAJAN SINGH"),
        ("DOB", "30 AUG 1985"),
        ("BLOOD GRP", "B+"),
        ("ISSUED ON", "12 JAN 2021"),
        ("VALID TILL", "11 JAN 2031"),
        ("CLASS", "LMV / MOTOR CYCLE"),
        ("AUTHORITY", "RTO DELHI CENTRAL (DL-04)"),
    ]

    y_pos = 110
    for lbl, val in fields:
        d.text((50, y_pos), lbl, fill=(71, 85, 105))
        d.text((220, y_pos), val, fill=(15, 23, 42))
        y_pos += 42

    # Portrait Box
    d.rectangle([(620, 110), (850, 400)], fill=(241, 245, 249), outline=(30, 58, 138), width=2)
    draw_realistic_face(d, 650, 140, 160, 210)

    # QR / Barcode representation
    d.rectangle([(50, 480), (550, 530)], fill=(226, 232, 240), outline=(148, 163, 184))
    d.text((70, 495), "||||| | |||| ||| ||||||| ||||| |||| |||||| ||||| DL04202300789", fill=(15, 23, 42))

    path = os.path.join(OUTPUT_DIR, "sample_blacklisted_license.jpg")
    img.save(path, format="JPEG", quality=95)
    print(f"Generated: {path}")

def generate_face_portrait():
    img = Image.new("RGB", (400, 450), color=(240, 244, 248))
    d = ImageDraw.Draw(img)
    # Clean probe portrait for Aarav Sharma
    draw_realistic_face(d, 100, 80, 200, 270)

    path = os.path.join(OUTPUT_DIR, "sample_face_portrait.jpg")
    img.save(path, format="JPEG", quality=95)
    print(f"Generated: {path}")

if __name__ == "__main__":
    generate_valid_passport()
    generate_expired_passport()
    generate_blacklisted_license()
    generate_face_portrait()
    print("All demo samples generated successfully.")
