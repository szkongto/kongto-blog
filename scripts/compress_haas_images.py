import os, sys
from PIL import Image

# Use raw string for Windows path with Chinese
src = os.path.join("D:", os.sep + "工作资料", "KONDTO", "产品图片", "Haas_哈斯")
dst = "d:/code/seo_deploy/images/haas"
os.makedirs(dst, exist_ok=True)

key_files = [
    "Haas 9-pin display CRT to lcd.jpg",
    "HAAS-V2.5-1904-01.jpg", "HAAS-V2.5-1904-02.jpg",
    "HAAS-V2.5-1904-09.jpg", "HAAS-V2.5-1904-11.jpg",
    "Haas_Monitor_00.jpg", "Haas_Monitor_01.jpg", 
    "Haas_Monitor_08.jpg", "Haas_Monitor_09.jpg",
]

files = [f for f in os.listdir(src) if f in key_files]
for f in files:
    src_path = os.path.join(src, f)
    name, ext = os.path.splitext(f)
    name = name.lower().replace(" ", "-").replace("_副本", "")
    out_name = f"haas-{name}.jpg"
    out_path = os.path.join(dst, out_name)
    
    try:
        img = Image.open(src_path)
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
        img.save(out_path, "JPEG", quality=80, optimize=True)
        print(f"  {f} -> {out_name} ({os.path.getsize(out_path)//1024}KB)")
    except Exception as e:
        print(f"  SKIP {f}: {e}")

# Copy VF3 image too (installation example)
vf3 = os.path.join(src, "VF3.jpg")
if os.path.exists(vf3):
    img = Image.open(vf3)
    if img.width > 800:
        ratio = 800 / img.width
        img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
    img.save(os.path.join(dst, "haas-vf3-installation.jpg"), "JPEG", quality=80, optimize=True)
    print(f"  VF3.jpg -> haas-vf3-installation.jpg")

print("\nDone")
