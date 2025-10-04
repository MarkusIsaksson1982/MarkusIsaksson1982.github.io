/**
 * main.js
 * 
 * Denna fil innehåller huvudlogiken för webbapplikationen.
 * Den ansvarar för:
 *  1. Ladda WebAssembly-modulen via `SorterModule`-funktionen som genereras av Emscripten.
 *  2. Hantera UI-händelser (knapptryckningar).
 *  3. Genomföra ett prestandatest mellan Wasm-funktionen och en motsvarande JS-funktion.
 *  4. Använda C++-hjälpfunktioner för att robust överföra data till och från Wasm-minnet.
 *  5. Visualisera den osorterade och sorterade datan i DOM.
 */

// sorter.js kommer att skapa en global funktion `SorterModule`.
const wasmReady = SorterModule();

// Hämta referenser till DOM-element
const sortButton = document.getElementById('sortButton');
const resetButton = document.getElementById('resetButton');
const unsortedContainer = document.getElementById('unsorted-container');
const sortedContainer = document.getElementById('sorted-container');
const wasmTimeSpan = document.getElementById('wasm-time');
const jsTimeSpan = document.getElementById('js-time');

const ARRAY_SIZE = 30000;
let data = [];

function generateData() {
    data = [];
    for (let i = 0; i < ARRAY_SIZE; i++) {
        data.push(Math.floor(Math.random() * 1000) + 1);
    }
    console.log(`Ny data genererad med ${ARRAY_SIZE} element.`);
}

function visualizeData(array, container) {
    container.innerHTML = '';
    const maxValue = Math.max(...array, 1000);
    const itemsToVisualize = array.slice(0, 1000);
    for (const value of itemsToVisualize) {
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = `${(value / maxValue) * 100}%`;
        container.appendChild(bar);
    }
}

function bubbleSortJS(arr) {
    const size = arr.length;
    for (let i = 0; i < size - 1; i++) {
        for (let j = 0; j < size - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                let temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

async function runPerformanceTest() {
    sortButton.disabled = true;
    sortButton.textContent = 'Kör prestandatest...';
    wasmTimeSpan.textContent = 'Kör...';
    jsTimeSpan.textContent = 'Väntar...';

    const Module = await wasmReady;
    console.log("Wasm-modulen är redo (via modularisering).");

    // --- Test 1: WebAssembly --- 
    console.log("Startar WebAssembly-sortering...");
    const t0_wasm = performance.now();

    const dataByteLength = data.length * 4;
    const dataPtr = Module._malloc(dataByteLength);

    // SKRIV TILL MINNET: Använd vår nya hjälpfunktion i en loop.
    // Detta är långsammare än en bulk-kopiering, men garanterat att fungera.
    for (let i = 0; i < data.length; i++) {
        Module._set_array_value(dataPtr, i, data[i]);
    }

    // KÖR SORTERING
    Module._bubbleSort(dataPtr, data.length);

    // LÄS FRÅN MINNET: Använd vår andra hjälpfunktion för att läsa tillbaka datan.
    const sortedDataFromWasm = new Int32Array(data.length);
    for (let i = 0; i < data.length; i++) {
        sortedDataFromWasm[i] = Module._get_array_value(dataPtr, i);
    }

    Module._free(dataPtr);

    const t1_wasm = performance.now();
    const wasmTime = (t1_wasm - t0_wasm).toFixed(2);
    wasmTimeSpan.textContent = `${wasmTime} ms`;
    console.log(`WebAssembly sortering tog: ${wasmTime} ms`);

    visualizeData(sortedDataFromWasm, sortedContainer);

    // --- Test 2: JavaScript ---
    setTimeout(() => {
        jsTimeSpan.textContent = 'Kör...';
        console.log("Startar JavaScript-sortering...");
        const dataCopy = [...data];

        const t0_js = performance.now();
        bubbleSortJS(dataCopy);
        const t1_js = performance.now();

        const jsTime = (t1_js - t0_js).toFixed(2);
        jsTimeSpan.textContent = `${jsTime} ms`;
        console.log(`JavaScript sortering tog: ${jsTime} ms`);

        sortButton.textContent = 'Jämför Prestanda (Wasm vs. JS)';
        sortButton.disabled = false;
    }, 50);
}

function reset() {
    generateData();
    visualizeData(data, unsortedContainer);
    sortedContainer.innerHTML = '';
    wasmTimeSpan.textContent = '...';
    jsTimeSpan.textContent = '...';
    sortButton.disabled = false;
}

// Händelselyssnare
resetButton.addEventListener('click', reset);
sortButton.addEventListener('click', runPerformanceTest);

// Initiera
reset();