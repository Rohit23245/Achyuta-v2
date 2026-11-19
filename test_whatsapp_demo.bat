@echo off
title Achyuta WhatsApp Demo Tester
color 0A
cls
echo ========================================================
echo        ACHYUTA WHATSAPP DEMO TESTER (NEVER-EXPIRING)
echo ========================================================
echo.
echo Recipient Number : +91 87075 26283 (Default)
echo WhatsApp App     : Kavya API Tool
echo System User      : KavyaBackendSystemUser (Permanent Token)
echo.
echo Sending test demo message now...
echo.

python -c "import sys; sys.path.append(r'%~dp0'); import whatsapp_client; res = whatsapp_client.send_template('918707526283', 'hello_world'); print('\nResult:', res); input('\nPress Enter to exit...')"
