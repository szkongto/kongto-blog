#!/usr/bin/env python3
"""
/product-images skill engine.
Batch process all product images: 800x800 white canvas, rembg for lcd_front.
Usage: python scripts/product_images.py [--product PRODUCT_FILENAME]
       python scripts/product_images.py  # all products
"""
import os, re, glob, sys, shutil
from PIL import Image

SRC = r'D:\工作资料\KONGTO\产品图片'
PROD = r'd:\code\seo_deploy\products'
IMG  = r'd:\code\seo_deploy\images'

# ============================================================
# SOURCE IMAGE MAPPING
# Each product -> list of (source_rel_path, image_type)
# ============================================================
MANUAL = {
    'fanuc-0m-0t-crt-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0072-1.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0072-2.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
    'fanuc-16i-18i-21i-lcd-upgrade.html': [
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
        ('FANUC/0096/A61L-0001-0096-crt.jpg', 'crt'),
        ('FANUC/0096/D14CM-01A 0096 CRT标签型号.jpg', 'label'),
    ],
        'fanuc-a02b-0094-c022-lcd-upgrade.html': [
        ('FANUC/A02B-0094-C022/8DS_0099.JPG', 'lcd_front'),
        ('FANUC/A02B-0094-C022/Fanuc - CRT A02B-0094-C022-BACK.jpg', 'lcd_back'),
        ('FANUC/A02B-0094-C022/Fanuc - CRT A02B-0094-C022-LABEL.jpg', 'label'),
        ('FANUC/A02B-0094-C022/Fanuc - CRT A02B-0094-C022.jpg', 'crt'),
    ],
    'fanuc-a02b-0099-c094-lcd-upgrade.html': [
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-01.jpg', 'lcd_front'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-04.jpg', 'lcd_back'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-03.jpg', 'crt'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-02.jpg', 'label'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-05.jpg', 'effect'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/A02B-06.jpg', 'connector'),
        ('FANUC/FANUC Series O-P A02B-0099-C094-PBM单绿色/FANUC SERIES O-PD.jpg', 'label'),
    ],
    'fanuc-a02b-0200-c071-lcd-upgrade.html': [
        ('FANUC/0074-0094/0074-94.jpg', 'lcd_front'),
        ('FANUC/0074-0094/0074-94-02.jpg', 'lcd_back'),
        ('FANUC/0074-0094/fanuc 替代效果.jpg', 'effect'),
    ],
    'fanuc-a61l-0001-0072-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/0092-0086-0076-BM.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0072-2.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
                'fanuc-a61l-0001-0074-lcd-upgrade.html': [
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/2018-0074-0094新液晶-V2.5/0094-74-1-1.jpg', 'lcd_front'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/2018-0074-0094新液晶-V2.5/2018-74-94-0005.jpg', 'lcd_back'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/替换效果/0094-0074安装效果背面.jpg', 'effect'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/替换效果/A61L-0001-0094_LCDV2.5-05.jpg', 'effect'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/C14C-1472D1F-A61L-0001-0094#A-LABEL.jpg', 'label'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/0074-OLD.jpg', 'crt'),
    ],
        'fanuc-a61l-0001-0076-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/0092-0086-0076-BM.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/FANUC A61L-0001-0092-0086-0076-zm.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/0086-0092-0076 LCD效果.jpg', 'crt'),
    ],
    'fanuc-a61l-0001-0077-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0072-1.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0072-2.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
    'fanuc-a61l-0001-0078-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0072-1.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0072-2.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
            'fanuc-a61l-0001-0086-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/0086.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/8DS_1646_副本.JPG', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/MATSUSHITA 0086-CRT.jpg', 'crt'),
    ],
    'fanuc-a61l-0001-0087-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0072-1.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/8DS_1646_副本.JPG', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/A61L-0001-0086  monitor.jpg', 'label'),
    ],
                'fanuc-a61l-0001-0090-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/21  FANUC_A61l-0001-0090/FANUC A61L-0001-0090-800M-02.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/21  FANUC_A61l-0001-0090/FANUC A61L-0001-0090-800M-06.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/21  FANUC_A61l-0001-0090/A61L-0001-0090-0M-CRT.jpg', 'crt'),
        ('FANUC/0072-0076-0086-0090-0092/21  FANUC_A61l-0001-0090/A61L-0001-0090-LBL.jpg', 'label'),
    ],
        'fanuc-a61l-0001-0092-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/FANUC A61L-0001-0092-0086-0076-zm.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/0092-0086-0076-BM.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0092-0086-0076-同款白底-NEW/QQ图片20190910164309.jpg', 'crt'),
    ],
        'fanuc-a61l-0001-0093-lcd-upgrade.html': [
        ('FANUC/0093/A61L-0001-0093-12.jpg', 'lcd_front'),
        ('FANUC/0093/最新款0093-V3.4 LCD/Fanuc 0093 背面安装后实拍图.jpg', 'lcd_back'),
        ('FANUC/0093/老CRT显示器/Fanuc - CRT A61L-0001-0093.jpg', 'crt'),
        ('FANUC/0093/老CRT显示器/Fanuc - CRT A61L-0001-0093 LABEL  KF-M7099H.jpg', 'label'),
        ('FANUC/0093/最新款0093-V3.4 LCD/替代实拍照.jpg', 'effect'),
    ],
                    'fanuc-a61l-0001-0094-lcd-upgrade.html': [
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/8DS_0107.JPG', 'lcd_front'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/替换效果/0094-0074安装效果背面.jpg', 'effect'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/替换效果/A61L-0001-0094_LCDV2.5-05.jpg', 'effect'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/C14C-1472D1F-A61L-0001-0094#A-LABEL.jpg', 'label'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/0074-OLD.jpg', 'crt'),
        ('FANUC/0074-0094/Fanuc发那科A61L-001-0074A61L-0001-0094 new/CRT/0094-V3 唐山.jpg', 'crt'),
    ],
            'fanuc-a61l-0001-0095-lcd-upgrade.html': [
        ('FANUC/0095/2019-FANUC A61L-0001-0095 V3.4/FANUC A61L-0001-0095 V3.4-02.jpg', 'lcd_front'),
        ('FANUC/0095/2019-FANUC A61L-0001-0095 V3.4/Fanuc-CRT A61L-0001-0095-LABEL.jpg', 'label'),
        ('FANUC/0095/2019-FANUC A61L-0001-0095 V3.4/Fanuc-CRT A61L-0001-0095.jpg', 'crt'),
        ('FANUC/0095/2019-FANUC A61L-0001-0095 V3.4/FANUC A61L-0001-0095 V3.4-03.jpg', 'effect'),
    ],
    'fanuc-a61l-0001-0096-lcd-upgrade.html': [
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
        ('FANUC/0096/A61L-0001-0096-crt.jpg', 'crt'),
        ('FANUC/0096/A61L-0001-0096-LCD替换效果.jpg', 'effect'),
        ('FANUC/0096/D14CM-01A 0096 CRT标签型号.jpg', 'label'),
    ],
    'fanuc-a61l-0001-0097-lcd-upgrade.html': [
        ('FANUC/0097/A61L-0001-0097 LCD正面照.jpg', 'lcd_front'),
        ('FANUC/0097/A61L-0001-0097 LCD背面照.jpg', 'lcd_back'),
        ('FANUC/0097/A61L-0001-0097 CRT.jpg', 'crt'),
        ('FANUC/0097/A61L-0001-0097接口.jpg', 'connector'),
    ],
    'fanuc-a61l-0001-0116-lcd-upgrade.html': [
        ('FANUC/A61L-0001-0116/A61L-0001-0116 LCD正面图.jpg', 'lcd_front'),
        ('FANUC/A61L-0001-0116/A61L-0001-0116 LCD背面图.jpg', 'lcd_back'),
        ('FANUC/A61L-0001-0116/A61L-0001-0116 旧显示背面图1.png', 'crt'),
    ],
        'fanuc-mdt947b-1a-lcd-upgrade.html': [
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT947B-1B  A61L-0001-0092/MDT947B-1B-A61L-0001-0092-1.jpg', 'lcd_front'),
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT947B-1B  A61L-0001-0092/MDT947B-1B-A61L-0001-0092.jpg', 'lcd_back'),
    ],
    'fanuc-om-d-display-lcd-upgrade.html': [
        ('FANUC/0072-0076-0086-0090-0092/0072-1.jpg', 'lcd_front'),
        ('FANUC/0072-0076-0086-0090-0092/0072-2.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
    'fanuc-tx-1424ab-lcd-upgrade.html': [
        ('FANUC/0074-0094/0074-94.jpg', 'lcd_front'),
        ('FANUC/0074-0094/0074-94-02.jpg', 'lcd_back'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/Matsushita - CRT  KF-M7099H.jpg', 'crt'),
    ],
    'flickering-screen.html': [
        ('FANUC/0093/发现crt老化问题.jpg', 'crt'),
        ('FANUC/0093/显示器故障排查.jpg', 'effect'),
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
    ],
    'haas-12inch-9pin-crt-lcd-upgrade.html': [
        ('Haas_哈斯/550老版本/Haas_Monitor_03.jpg', 'lcd_front'),
        ('Haas_哈斯/550老版本/Haas_Monitor_04.jpg', 'lcd_back'),
        ('Haas_哈斯/550老版本/Haas_Monitor_05.jpg', 'crt'),
    ],
    'haas-28hm-nm4-lcd-upgrade.html': [
        ('Haas_哈斯/550老版本/Haas_Monitor_03.jpg', 'lcd_front'),
        ('Haas_哈斯/550老版本/Haas_Monitor_04.jpg', 'lcd_back'),
    ],
    'haas-9-pin-monochrome-lcd-upgrade.html': [
        ('Haas_哈斯/550老版本/Haas_Monitor_05.jpg', 'lcd_front'),
        ('Haas_哈斯/550老版本/Haas_Monitor_06.jpg', 'lcd_back'),
        ('Haas_哈斯/550老版本/Haas_Monitor_09.jpg', 'crt'),
    ],
    'haas-9pin-mono-crt-lcd-upgrade.html': [
        ('Haas_哈斯/550老版本/Haas_Monitor_03.jpg', 'lcd_front'),
        ('Haas_哈斯/550老版本/Haas_Monitor_06.jpg', 'lcd_back'),
        ('Haas_哈斯/550老版本/Haas_Monitor_09.jpg', 'crt'),
    ],
    'heidenhain-bc110-lcd-upgrade.html': [
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
    ],
    'heidenhain-be211-lcd-upgrade.html': [
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
    ],
    'heidenhain-be411-lcd-upgrade.html': [
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
    ],
    'image-retention.html': [
        ('FANUC/0096/安装替换效果.jpg', 'effect'),
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0093/发现crt老化问题.jpg', 'crt'),
    ],
    'matsushita-tx1450ab-lcd-upgrade.html': [
        ('其它更多品牌CRT替换方案订制案例/Matsushita/Matsushita - CRT  KF-M7099H.jpg', 'crt'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/KF-M7099H显示器.jpg', 'lcd_front'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/KF-M7099H显示器-1.jpg', 'label'),
    ],
    'mazak-14-inch-crt-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-06.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/DR5614 LCD Mazatrol T-32-2/CRT.jpg', 'crt'),
        ('MAZAK马扎克-日立/CDM1472D1M/MAZAK 替代效果.jpg', 'effect'),
    ],
    'mazak-aiqa8dsp40-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/AIQA8DSP40/Mazak  CRT  AIQA8DSP40.jpg', 'crt'),
        ('MAZAK马扎克-日立/AIQA8DSP40/Mazak  AIQA8DSP40.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/AIQA8DSP40/IMG_20240524_161739.jpg', 'lcd_back'),
    ],
    'mazak-c5470ns-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/C-5470NS/C-5470NS_副本.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/C-5470NS/20160125112940.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/C-5470NS/20160125113005.jpg', 'crt'),
        ('MAZAK马扎克-日立/C-5470NS/QQ图片20160125112912.jpg', 'label'),
    ],
    'mazak-cd0910-dm-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/1472-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/1472-02.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/CDM1472D1M/MAZAK 替代效果.jpg', 'effect'),
    ],
    'mazak-cd1283-d1m-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT-1283B-1A Mazak .jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-03.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-04.jpg', 'crt'),
    ],
    'mazak-cd1472-d2m-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-06.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/CDM1472D1M/MAZAK 替代效果.jpg', 'effect'),
    ],
    'mazak-cd1472-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-06.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/CDM1472D1M/MAZAK 替代效果.jpg', 'effect'),
    ],
    'mazak-dr5614-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/DR5614 LCD Mazatrol T-32-2/DR5614 LCD Mazatrol T-32-2 正面.JPG', 'lcd_front'),
        ('MAZAK马扎克-日立/DR5614 LCD Mazatrol T-32-2/DR5614 LCD背面.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/DR5614 LCD Mazatrol T-32-2/CRT.jpg', 'crt'),
        ('MAZAK马扎克-日立/DR5614 LCD Mazatrol T-32-2/DR5614 LCD Mazatrol T-32-2替代效果.jpg', 'effect'),
    ],
    'mazak-du3461g-l-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/1472-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/1472-02.jpg', 'lcd_back'),
    ],
    'mazak-mdt1283b-1a-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT-1283B-1A Mazak .jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-03.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-04.jpg', 'crt'),
    ],
    'mazak-mdt1283b-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT-1283B-1A Mazak .jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-05.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/MDT-1283-V2.62-1600/MDT1283-2021-V2.62-04.jpg', 'crt'),
    ],
    'mazak-t3021-ah-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/1472-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/1472-02.jpg', 'lcd_back'),
    ],
        'mitsubishi-bm09df-lcd-upgrade.html': [
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/MDT962B-1A_BM09DF_FCUA-CT100_2.jpg', 'lcd_front'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/LCD背面图.png', 'lcd_back'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/老CRT/BM09DF-11.jpg', 'crt'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/液晶替代效果/替代效果正面.jpg', 'effect'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/三菱信号连接线.jpg', 'connector'),
    ],
    'mitsubishi-c3470-crt-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-01.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-06.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/CDM1472D1M/CD1472D1M-02.jpg', 'effect'),
    ],
    'mitsubishi-c5470-lcd-upgrade.html': [
        ('MAZAK马扎克-日立/C-5470NS/C-5470NS_副本.jpg', 'lcd_front'),
        ('MAZAK马扎克-日立/C-5470NS/20160125112940.jpg', 'lcd_back'),
        ('MAZAK马扎克-日立/C-5470NS/20160125113005.jpg', 'crt'),
        ('MAZAK马扎克-日立/C-5470NS/20160125112843.jpg', 'label'),
    ],
        'mitsubishi-fcua-ct100-lcd-upgrade.html': [
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/MDT962B-1A_BM09DF_FCUA-CT100-04.jpg', 'lcd_front'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/LCD背面图.png', 'lcd_back'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/老CRT/FCUA-CT1001.jpg', 'crt'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/液晶替代效果/MDT962B-1A_BM09DF_FCUA-CT100-01.jpg', 'effect'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/老CRT/FCUA-CT100.jpg', 'label'),
    ],
    'mitsubishi-kf-m7099h-lcd-upgrade.html': [
        ('其它更多品牌CRT替换方案订制案例/Matsushita/Matsushita - CRT  KF-M7099H.jpg', 'crt'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/KF-M7099H显示器.jpg', 'lcd_front'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/KF-M7099H显示器-1.jpg', 'label'),
    ],
    'mitsubishi-mdt-1283b-lcd-upgrade.html': [
        ('案例/三菱MDT1283B-1A- 12CRT单色-东莞-KTV148/mdt1283b-1a.jpg', 'lcd_front'),
        ('案例/三菱MDT1283B-1A- 12CRT单色-东莞-KTV148/mdt1283b-1a2.jpg', 'lcd_back'),
        ('案例/三菱MDT1283B-1A- 12CRT单色-东莞-KTV148/mdt1283b-1a3.jpg', 'crt'),
        ('案例/三菱MDT1283B-1A- 12CRT单色-东莞-KTV148/mdt1283b-1a4.jpg', 'label'),
    ],
    'mitsubishi-mdt925ps-lcd-upgrade.html': [
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT-925PS/MDT-925PS.jpg', 'lcd_front'),
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT-925PS/MDT-925PS(2).jpg', 'lcd_back'),
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT-925PS/MDT-925PS-LABEL.jpg', 'label'),
    ],
    'mitsubishi-mdt947b-lcd-upgrade.html': [
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT947B-1B  A61L-0001-0092/MDT947B-1B-A61L-0001-0092-1.jpg', 'lcd_front'),
        ('其它更多品牌CRT替换方案订制案例/TOTOKU/TOTOKU MDT947B-1B  A61L-0001-0092/MDT947B-1B-A61L-0001-0092.jpg', 'lcd_back'),
        ('FANUC/0072-0076-0086-0090-0092/0.JPG', 'crt'),
    ],
        'mitsubishi-mdt962b-lcd-upgrade.html': [
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/液晶LCD正面测试效果.jpg', 'lcd_front'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/LCD背面图.png', 'lcd_back'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/老CRT/Totoku Electric - CRT MDT962B-1A.jpg', 'crt'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/液晶替代效果/三菱显示器替换效果.jpg', 'effect'),
        ('三菱/SL三菱8.4（MDT962B,BM09DF,FCUA-CT100,FCU6-DSE71-1）/V3.4B/老CRT/Totoku Electric - CRT MDT962B-1A-LABEL.jpg', 'label'),
    ],
        'mitsubishi-tx-1450ab-lcd-upgrade.html': [
        ('FANUC/0074-0094/0074-94.jpg', 'lcd_front'),
        ('FANUC/0074-0094/0074-94-02.jpg', 'lcd_back'),
        ('其它更多品牌CRT替换方案订制案例/Matsushita/Matsushita - CRT  KF-M7099H.jpg', 'crt'),
    ],
    'no-display.html': [
        ('FANUC/0093/发现crt老化问题.jpg', 'crt'),
        ('FANUC/0093/原CRT升级LCD模块.jpg', 'effect'),
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
    ],
    'okuma-osp-crt-lcd-upgrade.html': [
        ('Okuma 5000-5020/OKUMA 5020-3.jpg', 'lcd_front'),
        ('Okuma 5000-5020/okuma.jpg', 'lcd_back'),
        ('Okuma 5000-5020/1-1.jpg', 'crt'),
    ],
    'okuma-osp5000-lcd-upgrade.html': [
        ('Okuma 5000-5020/OKUMA 5020-3.jpg', 'lcd_front'),
        ('Okuma 5000-5020/OKUMA 5020-9.jpg', 'lcd_back'),
        ('Okuma 5000-5020/2-1.jpg', 'label'),
    ],
    'okuma-osp5020-crt-lcd-upgrade.html': [
        ('Okuma 5000-5020/OKUMA 5020-3.jpg', 'lcd_front'),
        ('Okuma 5000-5020/OKUMA 5020-8.jpg', 'lcd_back'),
        ('Okuma 5000-5020/OKUMA 5020-81.jpg', 'effect'),
    ],
    'okuma-osp5020-lcd-upgrade.html': [
        ('Okuma 5000-5020/OKUMA 5020-3.jpg', 'lcd_front'),
        ('Okuma 5000-5020/OKUMA 5020-9.jpg', 'lcd_back'),
        ('Okuma 5000-5020/OKUMA 5020-8.jpg', 'effect'),
    ],
    'okuma-osp7000-crt-lcd-upgrade.html': [
        ('Okuma 5000-5020/OKUMA 5020-3.jpg', 'lcd_front'),
        ('Okuma 5000-5020/OKUMA 5020-9.jpg', 'lcd_back'),
        ('Okuma 5000-5020/OKUMA 5020-81.jpg', 'effect'),
    ],
    'siemens-6fc3988-7fa20-lcd-upgrade.html': [
        ('SIM西门子/6FC3988-7FA20-CRT.jpg', 'crt'),
        ('SIM西门子/6FC3988-7FA20-PIC.jpg', 'lcd_front'),
        ('SIM西门子/6FC3988-7FA20-PCB.jpg', 'lcd_back'),
    ],
    'siemens-6fc3998-7fa20-lcd-upgrade.html': [
        ('SIM西门子/SM西门子新版/6FC3998-7FA20 Siemens-SM0901 9 MONOCHROME 579417 TA.jpg', 'lcd_front'),
        ('SIM西门子/SM西门子新版/Siemens-SM0901-579417 TA_CRT.jpg', 'crt'),
        ('SIM西门子/SM西门子新版/Siemens-SM0901-579417 TA_TFT.jpg', 'lcd_back'),
    ],
    'siemens-6fc5103-lcd-upgrade.html': [
        ('SIM西门子/Siemens-SM1200 LCD B.jpg', 'lcd_front'),
        ('SIM西门子/Siemens-SM1200 LCD.JPG', 'lcd_back'),
        ('SIM西门子/SM1200 CRT.jpg', 'crt'),
    ],
    'siemens-6fc5203-lcd-upgrade.html': [
        ('SIM西门子/Siemens-SM1200 LCD B.jpg', 'lcd_front'),
        ('SIM西门子/Siemens-SM1200 LCD.JPG', 'lcd_back'),
        ('SIM西门子/SM1200 CRT BM.jpg', 'crt'),
    ],
    'siemens-8.4-inch-crt-lcd-upgrade.html': [
        ('SIM西门子/Siemens-SM1200 LCD B.jpg', 'lcd_front'),
        ('SIM西门子/Siemens-SM1200 LCD.JPG', 'lcd_back'),
        ('SIM西门子/6FC3988-7FA20-CRT.jpg', 'crt'),
    ],
    'siemens-sm0901-lcd-upgrade.html': [
        ('SIM西门子/SM西门子新版/Siemens-SM0901 579417TA-LCD.JPG', 'lcd_front'),
        ('SIM西门子/SM西门子新版/Siemens-SM0901-579417 TA_01.jpg', 'lcd_back'),
        ('SIM西门子/SM西门子新版/Siemens-SM0901-579417 TA_CRT.jpg', 'crt'),
        ('SIM西门子/SM西门子新版/Siemens-SM0901-579417 TA_install.jpg', 'effect'),
    ],
    'siemens-sm1200-lcd-upgrade.html': [
        ('SIM西门子/Siemens-SM1200 LCD B.jpg', 'lcd_front'),
        ('SIM西门子/Siemens-SM1200 LCD.JPG', 'lcd_back'),
        ('SIM西门子/SM1200 CRT.jpg', 'crt'),
    ],
    'toshiba-d14cm-01a-lcd-upgrade.html': [
        ('FANUC/0096/D14CM-01A 0096 CRT标签型号.jpg', 'label'),
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
    ],
    'toshiba-d15cm-lcd-upgrade.html': [
        ('FANUC/0095/0095-d9cm-01a.jpg', 'lcd_front'),
        ('FANUC/0097/A61L-0001-0097 LCD背面照.jpg', 'lcd_back'),
        ('FANUC/0097/A61L-0001-0097 CRT.jpg', 'crt'),
    ],
        'toshiba-d9mm-11a-lcd-upgrade.html': [
        ('FANUC/0096/D14CM-01A 0096 CRT标签型号.jpg', 'label'),
        ('FANUC/0096/A61L-0001-0096 LCD正面照片.JPG', 'lcd_front'),
        ('FANUC/0096/A61L-0001-0096 LCD背面照片.jpg', 'lcd_back'),
    ],
}


def find_case_insensitive(base, rel_path):
    """Find file with case-insensitive path matching"""
    parts = rel_path.replace('\\', '/').split('/')
    current = base
    for p in parts:
        if not os.path.exists(current):
            return None
        if os.path.exists(os.path.join(current, p)):
            current = os.path.join(current, p)
        else:
            found = None
            try:
                for f in os.listdir(current):
                    if f.lower() == p.lower():
                        found = f
                        break
            except:
                pass
            if found:
                current = os.path.join(current, found)
            else:
                return None
    return current if os.path.isfile(current) else None


def process_image(src_path, dst_path, use_rembg=False):
    """Process single image: resize to 800x800 canvas. Optionally remove bg."""
    from PIL import Image

    try:
        im = Image.open(src_path)
    except Exception as e:
        print(f"    ERROR: cannot open {src_path}: {e}")
        return False

    # Optional background removal for lcd_front
    if use_rembg:
        try:
            from rembg import remove, new_session
            # Resize to max 1200px on longest side (preserve aspect ratio)
            max_dim = 1200
            r = min(max_dim / im.width, max_dim / im.height)
            if r < 1:
                im_small = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
            else:
                im_small = im.copy()
            session = new_session('u2net')
            im = remove(im_small, session=session,
                       alpha_matting=True,
                       alpha_matting_foreground_threshold=240,
                       alpha_matting_background_threshold=20,
                       alpha_matting_erode_size=10)
        except Exception as e:
            print(f"    rembg failed ({e}), using original")
            im = im.convert('RGBA')

    # Ensure RGBA for paste operation
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    # Fit into 800x800 white canvas
    sz = 800
    ratio = min(sz / im.width, sz / im.height)
    nw = int(im.width * ratio)
    nh = int(im.height * ratio)
    resized = im.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new('RGBA', (sz, sz), (255, 255, 255, 255))
    canvas.paste(resized, ((sz - nw) // 2, (sz - nh) // 2), resized)
    canvas.convert('RGB').save(dst_path, 'JPEG', quality=95, optimize=True)

    return True


def update_gallery_thumbs(html_path, image_names):
    """Update HTML gallery-thumbs to reference new images"""
    with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()

    if not image_names:
        return False

    # Update main image src
    html = html.replace(
        'src="/images/product-fanuc',
        f'src="/images/{image_names[0]}'
    )
    # Also catch already-updated names
    import re as re_mod
    html = re_mod.sub(
        r'(<img id="mainImage" src=")/images/[^"]+(")',
        rf'\1/images/{image_names[0]}\2',
        html
    )

    # Update og:image
    html = re_mod.sub(
        r'<meta property="og:image" content="https?://cncdisplay\.com/images/[^"\s]+',
        f'<meta property="og:image" content="https://cncdisplay.com/images/{image_names[0]}',
        html
    )

    # Build new gallery thumbs
    thumbs = ['<div class="gallery-thumbs">']
    for i, name in enumerate(image_names):
        cls = 'active' if i == 0 else ''
        thumbs.append(f'<img src="/images/{name}" alt="Product image" class="{cls}" onclick="switchImage(this)">')
    thumbs.append('</div>')

    # Replace existing gallery-thumbs
    pattern = re_mod.compile(r'(?s)<div class="gallery-thumbs">.*?</div>')
    if pattern.search(html):
        html = pattern.sub('\n'.join(thumbs), html, count=1)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return True


def main():
    os.chdir(r'd:\code\seo_deploy')

    # Determine which products to process
    if len(sys.argv) > 1 and sys.argv[1].startswith('--product='):
        target = sys.argv[1].split('=', 1)[1]
        products_to_process = [target] if target in MANUAL else []
    else:
        products_to_process = sorted(MANUAL.keys())

    if not products_to_process:
        print("No products to process")
        return

    print(f"Processing {len(products_to_process)} products...")

    for fname in products_to_process:
        entries = MANUAL[fname]
        # Sort by type priority: lcd_front, lcd_back, effect, label, crt, connector
        type_order = {'lcd_front':0, 'lcd_back':1, 'effect':2, 'label':3, 'crt':4, 'connector':5, 'lcd':6, 'product':7, 'unknown':8}
        entries.sort(key=lambda e: type_order.get(e[1], 99))
        base = fname.replace('.html', '')
        print(f"\n  {fname}")

        # Skip 0093 lcd_front - user already processed it
        image_names = []
        for i, (rel_path, img_type) in enumerate(entries):
            # Determine source path
            src_path = find_case_insensitive(SRC, rel_path)
            if not src_path:
                src_path = os.path.join(SRC, rel_path)
                if not os.path.exists(src_path):
                    print(f"    MISSING: {rel_path}")
                    continue

            # Destination
            new_name = f"{base}_{img_type}_{i}.jpg"
            dst_path = os.path.join(IMG, new_name)

            # Use rembg only for lcd_front type
            use_bg_removal = (img_type == 'lcd_front' and '0093' not in base)

            if process_image(src_path, dst_path, use_rembg=use_bg_removal):
                image_names.append(new_name)
                kb = os.path.getsize(dst_path) // 1024
                print(f"    OK {new_name} ({kb}KB)")
            else:
                print(f"    FAIL {new_name}")

        # Update HTML
        html_path = os.path.join(PROD, fname)
        if os.path.exists(html_path) and image_names:
            update_gallery_thumbs(html_path, image_names)
            print(f"    HTML updated ({len(image_names)} images)")

    print(f"\nDone! {len(products_to_process)} products processed.")


if __name__ == '__main__':
    main()




