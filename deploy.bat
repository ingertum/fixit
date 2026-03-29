@echo off
echo Запуск развертывания Fixit CRM...
set DEPLOY_PASSWORD=wPuj287.NFDqgg
call deploy-ci.sh
echo.
echo Развертывание завершено!
echo Проверьте приложение: http://ea16c5c76414.vps.myjino.ru:8000
pause