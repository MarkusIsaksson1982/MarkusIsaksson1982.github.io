@echo off
REM Detta skript kompilerar C++ koden till WebAssembly med Emscripten.

echo Bygger WebAssembly-modul...

emcc sorter.cpp -O2 -o sorter.js -s WASM=1 -s MODULARIZE=1 -s EXPORT_NAME="'SorterModule'" -s EXPORTED_FUNCTIONS="['_bubbleSort', '_malloc', '_free', '_set_array_value', '_get_array_value']"

if %errorlevel% neq 0 (
    echo.
    echo FEL: Kompileringen misslyckades.
    echo Kontrollera att Emscripten SDK är installerat och aktivt i denna terminal.
    exit /b 1
)

echo.
echo Klart! Filerna sorter.js och sorter.wasm har genererats.
