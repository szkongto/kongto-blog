# Practical Machinist — 论坛帖子
## 板块: CNC Machining / Machine Reconditioning

### 标题
Anyone replaced their old CNC CRT with LCD? My experience + cost breakdown

### 正文

I've now retrofitted 3 machines from CRT to LCD — a FANUC 18T, a Mitsubishi M64, and most recently a Mazak T-32. Sharing what I learned:

1. ALL were truly plug-and-play. Original connectors, no parameter changes, no soldering. The CNC controller literally can't tell the difference — it's getting the same composite video signal and same DC24V supply.

2. Cost comparison over 5 years:
   - CRT repair x3: $300-800 per repair, 3-12 months between failures = $2,000-4,000+
   - One LCD upgrade: $150-280, 5-7 years continuous operation = $150-280 total

3. The connector type matters more than the brand name:
   - FANUC = Honda MR-20M (20-pin)
   - Mitsubishi = 20-pin or 26-pin
   - Mazak = 26-pin
   - Siemens = DB-25, and uses AC110V (don't mix with DC!)

4. Consumer LCD panels WILL die in a shop environment. Vibration, oil mist, temperature swings. Industrial-grade Sharp/AUO panels only.

I documented the whole process with model-specific guides: https://cncdisplay.com

Anyone else done these retrofits? Which machines have you converted?

---
*发布到: https://www.practicalmachinist.com/forum/*
