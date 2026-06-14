# Reddit r/CNC — 帖子

### 标题
CNC CRT connector types reference — FANUC vs Mitsubishi vs Mazak vs Siemens

### 正文

Sharing because this confused me at first — different CNC brands use completely different CRT connectors:

- FANUC: Honda MR-20M (20-pin), DC24V
- Mitsubishi: 20-pin or 26-pin, DC24V
- Mazak: 26-pin, DC24V
- Siemens SINUMERIK: DB-25 (25-pin D-Sub), AC110V ⚠️ IMPORTANT: AC, not DC!
- Okuma: 14-pin or 20-pin, DC24V
- Haas early models: 9-pin D-Sub, DC12V

I learned the Siemens AC110V difference the hard way — don't repeat my mistake. If you're buying a replacement, triple-check: (1) connector type, (2) power supply voltage, (3) screen size.

Full compatibility matrix with 95+ model numbers: https://cncdisplay.com/en/compatibility-matrix.html

Mods, this is just a reference I wish I had when starting out. Hope it helps someone avoid buying the wrong replacement.

