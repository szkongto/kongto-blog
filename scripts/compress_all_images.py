import os, sys
from PIL import Image

jobs = [
    ("西门子", "siemens"),
    ("马扎克-日立", "mazak"),
    ("5000-5020", "okuma"),
]

base_src = os.path.join("D:", os.sep + "工作资料", "KONDTO", "产品图片")
base_dst = "d:/code/seo_deploy/images"

for folder, brand in jobs:
    src = os.path.join(base_src, f"SIM西门子" if brand == "siemens" else
                       f"MAZAK马扎克-日立" if brand == "mazak" else
                       f"Okuma 5000-5020")
    dst = os.path.join(base_dst, brand)
    os.makedirs(dst, exist_ok=True)

    if not os.path.isdir(src):
        print(f"SKIP {brand}: src not found")
        continue

    count = 0
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith(('.jpg','.jpeg','.png')): continue
        if count >= 6: break
        src_path = os.path.join(src, f)
        name, ext = os.path.splitext(f)
        clean = name.lower().replace(" ", "-").replace("_", "-").replace("--", "-")
        clean = ''.join(c for c in clean if c.isascii() or c == '-')
        out_name = f"{brand}-{clean[:40]}.jpg"
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
        except Exception as e:
            print(f"  SKIP {brand}/{f}: {e}")
    print(f"  {brand}: {count} images done")
print("\nAll done")
