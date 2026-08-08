#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add HowTo Schema to English installation/guide pages."""

import os
import json
import re

BASE = r'C:\Users\Administrator\WorkBuddy\2026-06-15-17-02-27\repo'

HOWTO_SCHEMAS_EN = {
    'en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html': {
        "name": "FANUC CRT to LCD Upgrade - Complete Installation Guide",
        "description": "Step-by-step guide to upgrade FANUC CNC display from CRT to LCD. 7 steps, plug-and-play, no machine modification needed.",
        "totalTime": "PT30M",
        "tool": [
            {"@type": "HowToTool", "name": "Phillips screwdriver"},
            {"@type": "HowToTool", "name": "Torque wrench (≤5 Nm)"},
            {"@type": "HowToTool", "name": "Anti-static wrist strap"},
            {"@type": "HowToTool", "name": "Cleaning cloth and alcohol (70%)"},
        ],
        "step": [
            {
                "@type": "HowToStep",
                "name": "Power Off & ESD Protection",
                "text": "Turn off CNC machine main power, disconnect display power cable. Wear anti-static wrist strap and ground it. Verify all power indicator lights are off to prevent residual high voltage.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step1"
            },
            {
                "@type": "HowToStep",
                "name": "Remove Original CRT",
                "text": "Loosen 4-6 mounting screws (varies by model). Carefully disconnect the HONDA 20-pin signal cable and 24V power cable. Pull connectors straight out to avoid damaging latch mechanisms.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step2"
            },
            {
                "@type": "HowToStep",
                "name": "Clean Mounting Surface",
                "text": "Wipe the original bracket and enclosure contact surface with alcohol cloth to remove oil and dust. Do not use corrosive solvents that may damage metal surfaces.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step3"
            },
            {
                "@type": "HowToStep",
                "name": "Place LCD Panel",
                "text": "Align the FANUC A61L-0001-0093 LCD with the original mounting holes. Press four corners lightly to engage automatic latches. Confirm LCD is fully seated against bracket to avoid signal contact issues.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step4"
            },
            {
                "@type": "HowToStep",
                "name": "Connect Cables",
                "text": "Insert HONDA 20-pin connector (align direction marker '1'). Connect 24V DC power cable (red/black polarity same as original CRT). Ensure connectors are fully seated to prevent vibration-induced disconnection.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step5"
            },
            {
                "@type": "HowToStep",
                "name": "Tighten Mounting Screws",
                "text": "Use torque wrench to tighten mounting screws to 4-5 Nm. Avoid over-tightening which may cause panel cracks. Keep threads clean to avoid metal debris entering display internals.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step6"
            },
            {
                "@type": "HowToStep",
                "name": "Power-On Test",
                "text": "Power on, enter FANUC System → Parameters → Display Settings. Confirm display resolution is 800x600 (or system default). If display is abnormal, recheck signal cable connection. Observe for 5 minutes on first power-up to confirm backlight and color uniformity.",
                "url": "https://cncdisplay.com/en/posts/FANUC_CRT_to_LCD_Upgrade_Complete_Guide.html#step7"
            },
        ],
    },
    'en/posts/Industrial_CNC_Display_Troubleshooting_Repair_Guide.html': {
        "name": "Industrial CNC Display Troubleshooting & Repair Guide",
        "description": "Step-by-step guide to diagnose and repair common CNC display problems: no display, flickering, color issues, and CRT-to-LCD upgrade options.",
        "totalTime": "PT45M",
        "tool": [
            {"@type": "HowToTool", "name": "Multimeter"},
            {"@type": "HowToTool", "name": "Screwdriver set"},
            {"@type": "HowToTool", "name": "Replacement LCD kit"},
        ],
        "step": [
            {"@type": "HowToStep", "name": "Identify Symptoms", "text": "Record display abnormality: no display, flickering, color distortion, horizontal bars, or dim image. Note when the problem occurs (startup, after warmup, under load)."},
            {"@type": "HowToStep", "name": "Check Power Supply", "text": "Measure 24V DC output with multimeter. Check power cable connectors for looseness or corrosion. Verify power LED on display is lit."},
            {"@type": "HowToStep", "name": "Check Signal Connection", "text": "Re-seat HONDA 20-pin signal cable. Inspect pins for bending or oxidation. Try reconnecting and power cycling the CNC system."},
            {"@type": "HowToStep", "name": "Diagnose CRT vs LCD", "text": "If image is flickering, dim, or has horizontal bars → CRT is likely aged. Recommend upgrading to LCD. If no image at all, check inverter and backlight."},
            {"@type": "HowToStep", "name": "Install LCD Upgrade Kit", "text": "Replace CRT with LCD upgrade kit (A61L-0001-0093 or equivalent). Plug-and-play, matches original mounting holes, no machine modification needed."},
        ],
    },
    'en/posts/CGA_EGA_to_RGBHV_Industrial_Display_Retrofit_Guide.html': {
        "name": "CGA/EGA to RGBHV Industrial Display Retrofit Guide",
        "description": "Guide to retrofitting older CGA/EGA industrial displays to modern RGBHV LCD solutions. Covers signal conversion and installation.",
        "totalTime": "PT60M",
        "tool": [
            {"@type": "HowToTool", "name": "Video signal converter (e.g. GBS-8219)"},
            {"@type": "HowToTool", "name": "Screwdriver"},
            {"@type": "HowToTool", "name": "Multimeter"},
        ],
        "step": [
            {"@type": "HowToStep", "name": "Identify Original Interface", "text": "Check original display video interface: CGA (4-pin), EGA (9-pin), or RGBHV (5 BNC). Note pin definitions from machine manual."},
            {"@type": "HowToStep", "name": "Select Signal Converter", "text": "Choose appropriate video signal converter based on original interface. For CGA/EGA to VGA/RGBHV, use a compatible converter box."},
            {"@type": "HowToStep", "name": "Mount Converter", "text": "Secure converter inside machine enclosure. Connect original signal cable to converter input. Use shielded cables to avoid EMI."},
            {"@type": "HowToStep", "name": "Connect LCD Display", "text": "Connect converter output to LCD display via VGA or RGBHV cable. Confirm 24V DC power supply to both converter and display."},
            {"@type": "HowToStep", "name": "Test and Adjust", "text": "Power on and test display. Adjust converter settings if image is off-center or has incorrect timing. Verify stability under machine operation."},
        ],
    },
    'en/posts/Industrial_RGBHV_Retrofit_Guide_CGA_EGA_to_HD.html': {
        "name": "Industrial RGBHV Retrofit Guide - CGA/EGA to HD LCD",
        "description": "Complete retrofit guide for upgrading industrial RGBHV displays from CGA/EGA to modern HD LCD panels.",
        "totalTime": "PT60M",
        "tool": [
            {"@type": "HowToTool", "name": "RGBHV-to-HD converter"},
            {"@type": "HowToTool", "name": "Screwdriver set"},
        ],
        "step": [
            {"@type": "HowToStep", "name": "Verify Original Signal Type", "text": "Confirm original display uses RGBHV (5 BNC), CGA, or EGA interface. Check machine manual for pinout diagram."},
            {"@type": "HowToStep", "name": "Select HD LCD Panel", "text": "Choose industrial LCD panel with RGBHV or VGA input, 800x600 or higher resolution, 400+ cd/m² brightness."},
            {"@type": "HowToStep", "name": "Install Signal Converter", "text": "Connect original RGBHV/CGA/EGA signal to converter input. Mount converter securely inside enclosure."},
            {"@type": "HowToStep", "name": "Connect and Power On", "text": "Connect converter output to LCD. Supply 24V DC power. Power on and verify image stability and color accuracy."},
        ],
    },
}


def make_howto_script(schema_data):
    """Generate JSON-LD script block for HowTo schema."""
    schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": schema_data["name"],
        "description": schema_data["description"],
        "totalTime": schema_data.get("totalTime", "PT30M"),
        "tool": schema_data.get("tool", []),
        "step": schema_data["step"],
    }
    json_str = json.dumps(schema, ensure_ascii=False, indent=2)
    # Make JSON-LD safe inside HTML script tag
    json_str = json_str.replace('</', r'<\/')
    return f'<script type="application/ld+json">\n{json_str}\n</script>'


def add_howto_to_page(filepath, schema_data):
    """Add HowTo schema before </head> if not already present."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '"@type": "HowTo"' in content or 'HowTo' in content:
        print(f'  [SKIP] Already has HowTo: {os.path.basename(filepath)}')
        return False

    script_block = make_howto_script(schema_data)

    if '</head>' in content:
        content = content.replace('</head>', script_block + '\n\n</head>', 1)
    else:
        print(f'  [WARN] No </head> found: {os.path.basename(filepath)}')
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  [OK] Added HowTo: {os.path.basename(filepath)}')
    return True


if __name__ == '__main__':
    print('Adding HowTo Schema to English installation/guide pages...\n')
    for rel_path, schema_data in HOWTO_SCHEMAS_EN.items():
        filepath = os.path.join(BASE, rel_path)
        if os.path.exists(filepath):
            print(f'Processing: {rel_path}')
            add_howto_to_page(filepath, schema_data)
        else:
            print(f'  [NOT FOUND] {rel_path}')
    print('\nDone!')
