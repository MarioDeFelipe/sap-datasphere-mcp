@echo off
echo ========================================
echo  Ailien Studio Website Deployment
echo ========================================
echo.

echo This script will help you deploy your website to Hostinger
echo.

echo Step 1: Open your Hostinger File Manager
echo - Login to your Hostinger control panel
echo - Navigate to File Manager
echo - Go to public_html folder
echo.

echo Step 2: Upload these files to public_html:
echo - index.html (Homepage)
echo - services.html (Services page)
echo - styles.css (All styling)
echo - script.js (Interactive features)
echo.

echo Step 3: Verify deployment
echo - Visit your domain to test the website
echo - Check mobile responsiveness
echo - Test contact forms
echo.

echo Files ready for upload are in this directory:
echo %~dp0
echo.

echo Opening file explorer to this directory...
start explorer "%~dp0"

echo.
echo ========================================
echo  Deployment Instructions Complete
echo ========================================
echo.
echo Your website files are ready!
echo Upload them to Hostinger's public_html folder.
echo.
pause