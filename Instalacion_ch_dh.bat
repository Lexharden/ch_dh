@echo off

REM Verifica si el entorno virtual ya existe
IF NOT EXIST ".venv" (
    echo Creando el entorno virtual...
    python -m venv .venv

    REM Activar el entorno virtual
    echo Activando el entorno virtual por primera vez...
    call .venv\Scripts\activate

    REM Actualizar pip usando el módulo Python
    echo Actualizando pip...
    call .venv\Scripts\python.exe -m pip install --upgrade pip

    REM Instalar las dependencias del requirements.txt
    echo Instalando dependencias desde requirements.txt...
    call .venv\Scripts\python.exe -m pip install -r requirements.txt

    REM Confirmación de instalación y entorno listo
    echo Entorno virtual creado e inicializado con las dependencias instaladas.
) ELSE (
    echo El entorno virtual ya existe.
    REM Activar el entorno virtual si ya existe
    echo Activando el entorno virtual...
    call .venv\Scripts\activate
)

REM Verificar si la activación del entorno fue exitosa
IF NOT "%VIRTUAL_ENV%"=="" (
    REM Ejecutar el main.py si el entorno está activado correctamente
    echo Ejecutando la aplicación...
    call .venv\Scripts\python.exe main.py
) ELSE (
    echo Error: no se pudo activar el entorno virtual.
    pause
    exit /b
)

REM Desactivar el entorno virtual al terminar
echo Desactivando el entorno virtual...
deactivate
pause
