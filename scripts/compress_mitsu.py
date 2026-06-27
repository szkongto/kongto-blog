import os, sys
from PIL import Image

src = os.path.join("D:", os.sep + "工作资料", "KONDTO", "产品图片", "SL三菱8.4（MDT962B,BM09DF,FCUA-CT100等）")
dst = "d:/code/seo_deploy/images/mitsubishi"
os.makedirs(dst, exist_ok=True)

files = []
for f in os.listdir(src):
    if f.lower().endswith(('.jpg','.jpeg','.png')):
        files.append(f)

for f in sorted(files)[:15]:  # Top 15 images
    src_path = os.path.join(src, f)
    name, ext = os.path.splitext(f)
    clean = name.lower().replace(" ", "-").replace("_", "-").replace("--", "-")
    out_name = f"mitsubishi-{clean}.jpg"
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

print("\nDone")
