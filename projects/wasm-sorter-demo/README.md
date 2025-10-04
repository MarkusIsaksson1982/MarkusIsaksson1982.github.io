# WebAssembly Performance Demo: Bubble Sort (C++ vs. JS)

Detta projekt är en tydlig och minimal demonstration av WebAssemblys (Wasm) prestandafördelar för CPU-intensiva uppgifter jämfört med ren JavaScript.

En klassisk sorteringsalgoritm, Bubble Sort, har implementerats i både C++ (kompilerad till Wasm) och JavaScript. Applikationen kör båda versionerna på samma stora datamängd och mäter tiden det tar för varje, vilket tydligt visar hastighetsskillnaden.

**Live Demo:** [Klicka här för att se live-demonstrationen](./live-demo/)

---

## Vad projektet demonstrerar

*   **Kompilering från C++ till WebAssembly:** Använder Emscripten för att kompilera C++-kod till en `.wasm`-modul och tillhörande JavaScript "lim-kod".
*   **Dynamisk laddning av Wasm:** Laddar och instansierar en Wasm-modul i en modern webbläsare.
*   **Robust dataöverföring:** Använder anrop till exporterade C++-funktioner (`setValue`/`getValue`) för att skriva och läsa data till/från Wasm-modulens minne. Denna metod är garanterad att fungera oavsett Emscriptens aggressiva optimeringar som annars kan ta bort minnesvyer som `HEAP32`.
*   **Konkret prestandajämförelse:** Ger en tydlig, mätbar demonstration av Wasm:s hastighetsfördelar för algoritmiska beräkningar.

## Teknologistack

*   **HTML5**
*   **CSS3**
*   **JavaScript (ES6+)**
*   **C++**
*   **WebAssembly (Wasm)**
*   **Emscripten SDK** (för kompilering)

## Filstruktur

```
/wasm_sorter_app
|-- sorter.cpp             # C++ källkod för Wasm-modulen.
|-- index.html             # Applikationens UI.
|-- style.css              # Styling.
|-- main.js                # Huvudsaklig JS-logik, Wasm-interaktion och prestandatest.
|
|-- build.bat              # Byggskript för Windows.
|-- build.sh               # Byggskript för Linux/macOS.
|
|-- sorter.js              # (Genereras av build-skriptet) JS "lim-kod".
|-- sorter.wasm            # (Genereras av build-skriptet) Den kompilerade Wasm-modulen.
|
|-- README.md              # Denna fil.
|-- LICENSE                # Projektlicens.
```

---

## Hur man bygger och kör lokalt

Du måste ha **Emscripten SDK** installerat och aktiverat i din terminal.

1.  **Klona projektet** (eller ladda ner filerna till en mapp).

2.  **Kör byggskriptet.** Navigera till projektmappen i din terminal och kör det skript som passar ditt operativsystem:

    *   **På Windows:**
        ```shell
        .\build.bat
        ```
    *   **På Linux eller macOS:**
        ```shell
        chmod +x build.sh
        ./build.sh
        ```
    Detta kommando anropar `emcc` (Emscripten Compiler) och genererar filerna `sorter.js` och `sorter.wasm`.

3.  **Starta en lokal webbserver.** Detta är nödvändigt eftersom webbläsare av säkerhetsskäl inte kan ladda Wasm-filer via `file://`-protokollet.
    ```shell
    python -m http.server
    ```

4.  **Öppna i webbläsaren.** Gå till `http://localhost:8000`.

