#!/usr/bin/env python3
"""Diagnose CSDN editor page - show available elements"""
import sys, os, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from cross_poster.config import SESSIONS_DIR, VIEWPORT

storage_path = os.path.join(SESSIONS_DIR, "csdn_storage.json")
profile_dir = os.path.join(SESSIONS_DIR, "browser_profile_csdn")

async def main():
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(profile_dir, headless=False, viewport=VIEWPORT)

    # Load saved cookies
    if os.path.exists(storage_path):
        with open(storage_path) as f:
            state = json.load(f)
        await ctx.add_cookies(state.get("cookies", []))

    page = await ctx.new_page()
    await page.goto("https://mp.csdn.net/mp_blog/creation/editor", wait_until="networkidle", timeout=60000)
    await asyncio.sleep(5)

    # Print all important elements
    info = await page.evaluate("""() => {
        const els = [];
        // Textareas
        document.querySelectorAll('textarea').forEach(el => {
            els.push({tag: 'textarea', id: el.id, class: el.className?.slice(0,60), placeholder: el.placeholder, visible: el.offsetParent !== null});
        });
        // Contenteditables
        document.querySelectorAll('[contenteditable]').forEach(el => {
            els.push({tag: 'div[contenteditable]', id: el.id, class: el.className?.slice(0,60), text: el.textContent?.slice(0,50)});
        });
        // Inputs
        document.querySelectorAll('input[type=text], input:not([type])').forEach(el => {
            els.push({tag: 'input', id: el.id, class: el.className?.slice(0,60), placeholder: el.placeholder, name: el.name});
        });
        // Buttons
        document.querySelectorAll('button, input[type=submit], input[type=button]').forEach(el => {
            els.push({tag: el.tagName, id: el.id, class: el.className?.slice(0,40), text: el.textContent?.trim()?.slice(0,40)});
        });
        // Iframe editors (like wangEditor, CodeMirror)
        document.querySelectorAll('iframe').forEach(el => {
            els.push({tag: 'iframe', id: el.id, title: el.title, src: el.src?.slice(0,80)});
        });
        return els;
    }""")

    print(f"\nPage URL: {page.url}")
    print(f"\nAccessible elements:")
    for el in info:
        print(f"  <{el['tag']}> id={el.get('id','')} class={el.get('class','')[:50]} placeholder={el.get('placeholder','')} text={el.get('text','')}")

    await asyncio.sleep(300)  # Keep browser open for visual inspection
    await ctx.close()
    await pw.stop()

asyncio.run(main())
