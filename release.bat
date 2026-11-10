@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  Release - Automacao Conveniar Email
echo ============================================

:: Usa .venv local se existir
if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
    set PIP=.venv\Scripts\pip.exe
    set PYINST=.venv\Scripts\pyinstaller.exe
) else (
    set PY=python
    set PIP=pip
    set PYINST=pyinstaller
)

:: Le VERSION direto do version.py na raiz
for /f "usebackq delims=" %%v in (`%PY% -c "from version import VERSION; print(VERSION)"`) do set VERSION=%%v
if "%VERSION%"=="" (
    echo ERRO: nao foi possivel ler VERSION de version.py
    pause & exit /b 1
)
set TAG=v%VERSION%
echo Versao detectada: %TAG%
echo.

:: Verifica se a tag ja existe remotamente
git fetch --tags -q
git rev-parse "%TAG%" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ERRO: tag %TAG% ja existe.
    echo Incremente VERSION em version.py antes de fazer release.
    pause & exit /b 1
)

:: Instala dependencias de build
echo [1/5] Instalando dependencias de build...
%PIP% install -r requirements-build.txt -q
if %ERRORLEVEL% neq 0 ( echo ERRO ao instalar dependencias & pause & exit /b 1 )

:: Roda testes (pula se nao houver pasta tests/)
echo [2/5] Verificando testes...
if exist "tests" (
    %PY% -m pytest tests -q
    if %ERRORLEVEL% neq 0 ( echo ERRO nos testes & pause & exit /b 1 )
) else (
    echo    Sem pasta tests/ — pulando testes.
)

:: Compila o executavel
echo [3/5] Compilando executavel...
if exist dist rmdir /s /q dist
%PYINST% AutomacaoConveniarEmail.spec --noconfirm
if %ERRORLEVEL% neq 0 ( echo ERRO no PyInstaller & pause & exit /b 1 )
if not exist "dist\AutomacaoConveniarEmail.exe" (
    echo ERRO: dist\AutomacaoConveniarEmail.exe nao encontrado
    pause & exit /b 1
)

:: Calcula SHA-256 para verificacao de integridade
echo [4/5] Calculando SHA-256...
for /f "usebackq delims=" %%h in (`powershell -NoProfile -Command "(Get-FileHash 'dist\AutomacaoConveniarEmail.exe' -Algorithm SHA256).Hash.ToLower()"`) do set SHA256=%%h
echo %SHA256%  AutomacaoConveniarEmail.exe > dist\AutomacaoConveniarEmail.exe.sha256
echo SHA-256: %SHA256%

:: Cria tag, envia e publica release com EXE e SHA-256
echo [5/5] Publicando release %TAG% no GitHub...
git tag %TAG%
git push origin %TAG%
if %ERRORLEVEL% neq 0 (
    git tag -d %TAG% >nul 2>&1
    echo ERRO ao enviar tag para o GitHub
    pause & exit /b 1
)

set NOTES_FILE=%TEMP%\release_notes_%VERSION%.md
(
    echo ## Instalacao
    echo.
    echo 1. Baixe AutomacaoConveniarEmail.exe
    echo 2. Coloque na pasta do projeto junto com o .env configurado
    echo 3. Execute AutomacaoConveniarEmail.exe
    echo.
    echo **SHA-256:** %SHA256%
) > "%NOTES_FILE%"

gh release create %TAG% ^
    "dist\AutomacaoConveniarEmail.exe" ^
    "dist\AutomacaoConveniarEmail.exe.sha256" ^
    --title "Automacao Conveniar Email %TAG%" ^
    --notes-file "%NOTES_FILE%"

if %ERRORLEVEL% neq 0 (
    echo ERRO ao criar release no GitHub
    del "%NOTES_FILE%" >nul 2>&1
    pause & exit /b 1
)
del "%NOTES_FILE%" >nul 2>&1

echo.
echo ============================================
echo  Release %TAG% publicada com sucesso!
echo  https://github.com/DaviTSelect/download-comprovantes-relatorios-email/releases/tag/%TAG%
echo ============================================
pause
