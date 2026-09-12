# -*- coding: utf-8 -*-
"""把 2026-09-12 复测的原始回答落盘成 score.py 可读的 json。

数据来源：Bright Data `web_data_chatgpt_ai_insights`，5 条 query 与
config.json / baseline_2026-08-09.json 完全相同，保证可比。

Perplexity 侧本轮未取到：`web_data_perplexity_ai_insights` 连续 3 次
在 600 秒后超时（同日 search_engine 正常，账号未停），属工具侧故障，
不是站点问题。perplexity 结果留空，待工具恢复后补跑。
"""
import io
import json
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = pathlib.Path(__file__).resolve().parent

ANSWERS = [
    {
        "model": "FANUC A61L-0001-0093",
        "llm": "chatgpt",
        "query": "What is the best replacement LCD display for a FANUC A61L-0001-0093 CRT monitor on a CNC machine?",
        "answer": """For a **FANUC A61L-0001-0093**, I'd replace the aging CRT with a **purpose-built industrial LCD retrofit**, rather than trying to source another used CRT.

### My top choices

1.  **Industrial Panels QES1508-057 - 8.4" TFT-LCD**
    *   Specifically designed as a drop-in replacement for the **A61L-0001-0093**.
    *   **24 VDC** input.
    *   Accepts the legacy **TTL/CGA/EGA/MDA** video signals used by these FANUC controls.
    *   450 cd/m2 brightness and 600:1 contrast.
    *   Designed to use the original mounting points. [1]
    *   **Best choice if you want a well-documented industrial replacement.**
2.  **Monitech ML080LL0093S - 8" LCD retrofit**
    *   Specifically marketed for the **A61L-0001-0093 9" CRT**.
    *   Purpose-built rather than adapting a generic computer LCD.
    *   Good option when physical fit and long-term industrial reliability are priorities. [2]
3.  **Kongto A61L-0001-0093 LCD retrofit**
    *   Advertised as a direct replacement using the original connector and 24-V supply.
    *   Their documentation identifies the **Honda 20-pin video connection** and claims no CNC parameter changes are required. [3]
    *   Attractive option if you're looking for a lower-cost retrofit.

### What I would buy

**I'd choose the Industrial Panels QES1508-057** if availability and price are reasonable. Its published specifications explicitly address the things that matter on an old FANUC: **legacy TTL video, 24-VDC operation, FANUC timing, industrial construction, and direct mounting**. [4]

There are also complete replacement units from **CNC Electronics** (their CNC93), which use LED-backlit LCD technology and are specifically built to replace the A61L-0001-0093; they advertise a 2-year warranty. [5]

### One important caution

Don't order an LCD solely because the seller says "FANUC 9-inch CRT replacement." The **A61L-0001-0093 family has variants**, and other visually similar FANUC displays can have different video interfaces/timings. The replacement needs to match your actual CRT's **part number, connector, video signal, supply voltage, and mounting dimensions**. [6]

If you give me the **FANUC control model** (for example, 0-M, 0-T, 0i-MA, 16M, 18T, etc.) and preferably a **photo of the rear of the A61L-0001-0093**, I can narrow it down to the **exact LCD replacement I'd buy, including current suppliers and price options**.

[7]""",
    },
    {
        "model": "Siemens 6FC3988 / SM0901",
        "llm": "chatgpt",
        "query": "What LCD replacement works for a Siemens SINUMERIK 6FC3988-7FA20 / SM0901 9-inch CRT display?",
        "answer": """Yes. For the **Siemens SINUMERIK 6FC3988-7FA20 / SM0901 9-inch monochrome CRT**, there are purpose-built **CRT-to-LCD retrofit modules** rather than a generic LCD panel.

### Recommended replacement

A **9-inch industrial TFT/LCD retrofit specifically listed for 6FC3988-7FA20 / SM0901** is the safest choice. Current retrofit listings specify:

*   **9-inch LCD/TFT**
*   **800 x 600** resolution
*   Designed as a replacement for **6FC3988-7FA20**
*   Also available for **SM0901 / 579417TA**
*   Intended as a plug-and-play CRT replacement, retaining the original CNC interface. [1]

One currently advertised solution is the **Kongto Siemens 6FC3988-7FA20 LCD retrofit**. Their compatibility information specifically lists both **6FC3988-7FA20 and SM0901/579417TA**. [2]

[3]

### Important: don't buy an ordinary 9" LCD

The original display uses an old Siemens CRT video interface, so a standard VGA/HDMI 9" LCD will **not** simply plug in. Retrofit modules need the appropriate signal conversion/interface and the correct power arrangement. One compatibility reference identifies the Siemens 6FC3988/SM0901 interface as a **2-row 16-pin connection with AC power**, but there are variations, so the exact monitor should be checked before ordering. [4]

There is also some conflicting information online about the exact original assembly: one industrial-parts source describes the 6FC3988-7FA20 as a **9" SINUMERIK 810/System 3 monitor**, while another catalog describes the complete operator panel differently. [5]

**My recommendation:** buy a retrofit explicitly stating **"6FC3988-7FA20 / SM0901"**, rather than selecting an LCD by size alone.

If you send me **a photo of the rear of your SM0901/6FC3988-7FA20 and its connector**, I can identify the **exact LCD replacement, connector/pinout, voltage, and suitable suppliers**.

[6]""",
    },
    {
        "model": "Mitsubishi MDT962B",
        "llm": "chatgpt",
        "query": "What is a good LCD replacement for a Mitsubishi MDT962B (or BM09DF/FCUA-CT100) CNC display?",
        "answer": """Yes. For a **Mitsubishi MDT962B / BM09DF / FCUA-CT100**, I would use a **purpose-built industrial TFT-LCD retrofit**, rather than trying to adapt a normal VGA monitor.

### Best replacement

A current retrofit marketed specifically for **MDT962B / BM09DF / FCUA-CT100** is the safest choice. These are designed to accept the Mitsubishi's unusual video timing and connector arrangement.

One currently advertised option is an **8-9" industrial TFT LCD**, typically:

*   **800 x 600 (SVGA)**
*   LED backlight
*   Around **250-450 cd/m2**
*   Designed for the original Mitsubishi signal
*   Retains the existing Mitsubishi interface/connector or supplies the appropriate adapter
*   Intended as a drop-in replacement with no CNC parameter changes

For example, Kongto's current MDT962B/BM09DF/FCUA-CT100 retrofit is advertised as a direct replacement and lists an 8" LCD, 800x600 resolution, 350-450 cd/m2 brightness and 50,000+ hour life. [1]

[2]

Another supplier, Elongshine, currently lists a **MDT962B-1A/BM09DF/FCUA-CT100 LCD** replacement at about **US$130**, with a 10-pin edge signal connector and AC 100-240 V input. [3]

[4]

### One important caveat

Don't buy a generic 9" VGA LCD just because the physical dimensions look right. The original Mitsubishi display uses **non-standard video timing**. Published specifications for the MDT962B/BM09DF family include approximately **24 kHz horizontal / 50.5 Hz vertical** scanning and a 10-pin edge connector. [5]

So a modern computer LCD expecting 31-kHz VGA/60 Hz generally **will not work directly**. You need a retrofit specifically supporting the Mitsubishi signal, or a suitable scan converter.

### What I'd buy

If this is for a production machine, my preference would be:

**MDT962B/BM09DF/FCUA-CT100-specific industrial LCD retrofit -> 800x600 TFT -> original connector/interface -> industrial temperature rating.**

That's considerably preferable to repairing the aging CRT, assuming the price is reasonable. The CRT's original 24-kHz monochrome signal is the key thing the replacement needs to handle. [6]

If you give me the **exact label on your existing monitor** (e.g. `MDT962B-1A`, `MDT962B-4A`, `BM09DF`, etc.) and ideally a **photo of the rear connectors**, I can identify the **specific LCD panel/retrofit and connector pinout** you should buy.

[7]""",
    },
    {
        "model": "FANUC A61L-0001-0116",
        "llm": "chatgpt",
        "query": "What LCD monitor replaces a FANUC A61L-0001-0116 9-inch plasma (PDP) display on a 0i-D system?",
        "answer": """For a **FANUC 0i-D** using the **A61L-0001-0116 9-inch color plasma (PDP)**, the most directly documented LCD replacement is:

### Recommended replacement

**FANUC A13B-0166-C011 LCD display unit**

*   **Replaces:** A61L-0001-0116
*   **Type:** 9-inch color LCD
*   **Application:** FANUC 16/18/21 and Power Mate i-series systems; the same PDP unit is also cataloged for the 0i family.
*   Radwell specifically identifies **A13B-0166-C011 as an LCD unit that replaces A61L-0001-0116**. [1]
*   The original **A61L-0001-0116 is discontinued**. [2]

There are also aftermarket **8.4-inch TFT/LCD retrofit monitors** specifically designed to replace the A61L-0001-0116. One documented replacement uses the original interface and is specified at **800x600**, with a 20-pin Honda connector. [3]

**Important:** Don't substitute the commonly advertised **A61L-0001-0093/0095 LCD replacements** just because they're 9-inch displays. Those are replacements for FANUC CRTs, not the **0116 plasma**. The 0116 is a different display/interface assembly. [4]

If you give me the **full 0i-D control/MDI part number** (for example, `A02B-...`) or a photo of the back of your existing A61L-0001-0116, I can identify the **exact plug-and-play LCD replacement**, including whether you need the **24 VDC or AC-powered version**. [5]

[6]""",
    },
    {
        "model": "Mazak MDT1283B / DR5614",
        "llm": "chatgpt",
        "query": "What LCD upgrade replaces a Mazak MDT1283B or DR5614 Mazatrol CRT display?",
        "answer": """Yes. There are **direct LCD/LED replacements** for both the Mazak/Mazatrol **MDT1283B** and **DR5614** CRTs.

*   **MDT1283B / MDT1283B-1A** - the common replacement is **QES1510-050**, a **10.4" LED-backlit LCD** designed as a plug-and-play replacement for the original 12" monochrome amber CRT. It retains the original mounting arrangement and TTL video interface. [1]
*   **DR5614 / P/N 800291** - the common replacement is **QES1512-205**, a **12.1" TFT-LCD with LED backlight** replacing the original 14" color CRT. It uses the Mazak-specific TTL timing and a 15-pin connector. [2]
*   A **12.1" TFT replacement sold as LCD12-0046** is another option that explicitly lists **both MDT1283B and DR-5614** among its compatible original monitor codes. It is specified for Mazatrol M2/M-2, M Plus, M32/T32 and related Mitsubishi controls. [3]
*   **DNC1283/DNC1283A** is another LED replacement specifically made for the MDT1283B-1A, with the original footprint/mounting holes and a 2-year warranty. [4]

### Which one should you buy?

If your CRT label actually says **MDT1283B**, I'd look for a **QES1510-050 / DNC1283-type replacement**.

If it says **DR5614**, use the **QES1512-205** or an equivalent **12.1" Mazatrol TFT replacement**.

**Important:** MDT1283B is normally a **12" monochrome CRT**, while DR5614 is a **14" color CRT**, so they aren't simply interchangeable despite some universal Mazatrol LCD suppliers listing both model numbers. [5]

If you give me the **Mazak machine model/year and the exact CRT label (including connector/photo)**, I can identify the **correct LCD part number, connector pinout, and a supplier in Europe**.

[6]""",
    },
]


def main():
    out = {
        "date": "2026-09-12",
        "note": (
            "复测：与 baseline_2026-08-09.json 同一组 query、同一来源 "
            "(Bright Data web_data_chatgpt_ai_insights)。对照组是 llms.txt 扩展"
            "(commit 453ff071, 2026-08-09)+110 条标题重写(commit 854a1c3d, 2026-09-12)之后。"
            "Perplexity 侧本轮取不到：web_data_perplexity_ai_insights 连续 3 次 600 秒超时，"
            "同日 search_engine 正常说明账号未停，属工具侧故障，待恢复补跑。"
        ),
        "results": ANSWERS,
    }
    dest = HERE / 'rerun_2026-09-12.json'
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print('written', dest)
    print('results', len(ANSWERS))


if __name__ == '__main__':
    main()
