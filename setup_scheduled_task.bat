@echo off
schtasks /create /tn "CNCdisplay_Daily_Backlinks" /tr "C:\Python314\python.exe D:\code\seo_deploy\daily_backlinks.py" /sc daily /st 09:00 /f
echo.
echo Task created. Verify: schtasks /query /tn CNCdisplay_Daily_Backlinks
pause
