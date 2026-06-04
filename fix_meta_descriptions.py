"""Fix short meta descriptions across all pages."""
import re, os

FIXES = {
    # CN Brand pages
    "./brands/FANUC.html": "FANUC发那科数控系统CRT转LCD显示器升级改造方案。覆盖A61L-0001-0074~0097全系列、D9MM-11A等型号，即插即用，零改装，2年质保。江图科技12年工业显示经验。",
    "./brands/HAAS.html": "Haas哈斯数控机床CRT显示器LCD升级解决方案。覆盖VF、ST、SL系列加工中心，原装接口即插即用，保留原安装尺寸，2年超长质保。江图科技工业显示专家。",
    "./brands/OKUMA.html": "Okuma大隈OSP 5000/5020系列CNC数控系统CRT转LCD显示器升级方案。原装接口设计，保留安装尺寸和固定孔位，无需修改系统参数。江图科技工业显示升级专家。",
    "./brands/Siemens.html": "西门子SINUMERIK数控系统显示器LCD升级替代方案。覆盖6FC3988-7FA20、SM0901-579417-TA等型号，支持840D/810D Power Line系统。江图科技12年经验。",
    "./brands/MAZAK.html": "马扎克Mazak数控系统CRT转LCD显示器升级方案。覆盖CD1472-D1M、C5470NS、DR5614等型号，支持Mazatrol系统。原装接口即插即用，质保2年。",
    "./brands/Mitsubishi.html": "三菱Mitsubishi数控系统工业显示器CRT转LCD替代方案。覆盖MDT962B、BM09DF、FCUA-CT100等型号，支持M64/E60/M500/M520系列系统。即插即用零改装。",

    # EN Brand pages
    "./en/brands/FANUC.html": "FANUC CNC display CRT to LCD upgrade solutions. Covers A61L-0001-0074~0097 series and D9MM-11A models. Plug-and-play installation, zero CNC parameter changes, 2-year warranty. Kongto Technology — 12+ years industrial display expertise.",
    "./en/brands/HAAS.html": "Haas CNC machine CRT to LCD display upgrade solutions. Covers VF, ST, SL series machining centers. Original connector plug-and-play design, retains factory mounting dimensions. 2-year warranty. Kongto Technology industrial display experts.",
    "./en/brands/OKUMA.html": "Okuma OSP 5000/5020 CNC system CRT to LCD display upgrade solutions. Original connector design preserves mounting dimensions and bolt patterns, no system parameter changes required. Kongto Technology since 2013.",
    "./en/brands/MAZAK.html": "Mazak CNC system CRT to LCD display upgrade solutions. Covers CD1472-D1M, C5470NS, DR5614 models for Mazatrol systems. Plug-and-play, original interfaces retained, 2-year warranty. Kongto Technology.",
    "./en/brands/Siemens.html": "Siemens SINUMERIK CNC display LCD upgrade solutions. Covers 6FC3988-7FA20, SM0901-579417-TA for 840D/810D Power Line systems. Original connector plug-and-play, zero parameter changes. Kongto Technology 12+ years.",
    "./en/brands/Mitsubishi.html": "Mitsubishi industrial CNC display CRT to LCD replacement solutions. Covers MDT962B, BM09DF, FCUA-CT100 for M64/E60/M500/M520 systems. True plug-and-play replacement. Kongto Technology since 2013.",
}

def main():
    count = 0
    for filepath, new_desc in FIXES.items():
        if not os.path.exists(filepath):
            print(f"  SKIP (not found): {filepath}")
            continue
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Replace the meta description
        old_content = content
        content = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{new_desc}">',
            content,
            count=1,
        )

        if content != old_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Fixed: {filepath} ({len(new_desc)} chars)")
            count += 1
        else:
            print(f"  NO CHANGE: {filepath}")

    print(f"\nTotal fixed: {count}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
