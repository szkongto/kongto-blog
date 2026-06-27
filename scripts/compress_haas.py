import os, sys
from PIL import Image

src = sys.argv[1]
dst = sys.argv[2]
os.makedirs(dst, exist_ok=True)

# Files to compress for the article
key_files = [
    "Haas 9-pin CRT to lcd.jpg", "Haas 9-pin display CRT to lcd.jpg",
    "HAAS-V2.5-1904-01.jpg", "HAAS-V2.5-1904-02.jpg",
    "HAAS-V2.5-1904-09.jpg", "HAAS-V2.5-1904-11.jpg",
    "Haas_Monitor_00.jpg", "Haas_Monitor_01.jpg",
    "Haas_Monitor_08.jpg", "Haas_Monitor_09.jpg",
    "VF3.jpg",
]

for f in os.listdir(src):
    if f not in key_files: continue
    src_path = os.path.join(src, f)
    name, ext = os.path.splitext(f)
    name = name.lower().replace(" ", "-").replace("_副本", "").replace("_", "-")
    out_name = f"haas-{name}.jpg"
    out_path = os.path.join(dst, out_name)
    try:
        img = Image.open(src_path)
        if img.width > 800:
            r = 800 / img.width
            img = img.resize((800, int(img.height * r)), Image.LANCZOS)
        img.save(out_path, "JPEG", quality=80, optimize=True)
        print(f"  {out_name} ({os.path.getsize(out_path)//1024}KB)")
    except Exception as e:
        print(f"  SKIP {f}: {e}")
