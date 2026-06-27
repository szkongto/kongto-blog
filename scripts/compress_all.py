import os, sys
from PIL import Image

base_src = sys.argv[1]
base_dst = sys.argv[2]

jobs = [
    ("SIM西门子", "siemens"),
    ("MAZAK马扎克-日立", "mazak"),
    ("Okuma 5000-5020", "okuma"),
]

for folder, brand in jobs:
    src = os.path.join(base_src, folder)
    dst = os.path.join(base_dst, brand)
    os.makedirs(dst, exist_ok=True)
    if not os.path.isdir(src):
        print(f"SKIP {brand}: {src}")
        continue
    count = 0
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith(('.jpg','.jpeg','.png')): continue
        if count >= 8: break
        src_path = os.path.join(src, f)
        name, ext = os.path.splitext(f)
        import re
        clean = re.sub(r'[^a-zA-Z0-9.-]', '-', name.lower())[:40].strip('-')
        out_name = f"{brand}-{clean}.jpg"
        out_path = os.path.join(dst, out_name)
        if os.path.exists(out_path): continue
        try:
            img = Image.open(src_path)
            if img.width > 800:
                r = 800 / img.width
                img = img.resize((800, int(img.height * r)), Image.LANCZOS)
            img.save(out_path, "JPEG", quality=80, optimize=True)
            print(f"  {brand}/{out_name} ({os.path.getsize(out_path)//1024}KB)")
            count += 1
        except: pass
    print(f"  {brand}: {count} images")
print("Done")
