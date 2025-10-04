/**
 * sorter.cpp
 * 
 * Denna fil innehåller C++-implementationen av en Bubble Sort-algoritm samt
 * hjälpfunktioner för att skriva och läsa data till/från WebAssembly-minnet.
 * 
 * Funktionerna är avsedda att kompileras till WebAssembly (Wasm) med Emscripten
 * och anropas från JavaScript. `EMSCRIPTEN_KEEPALIVE` säkerställer att funktionerna
 * inte optimeras bort av kompilatorn.
 */

#include <emscripten.h>

// Använd extern "C" för att förhindra C++ name mangling,
// vilket gör det enklare att anropa från JavaScript.
extern "C" {

// Sorteringsalgoritmen
EMSCRIPTEN_KEEPALIVE
void bubbleSort(int* arr, int size) {
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

// Ny hjälpfunktion för att skriva ett värde till en array från JS
EMSCRIPTEN_KEEPALIVE
void set_array_value(int* arr, int index, int value) {
    arr[index] = value;
}

// Ny hjälpfunktion för att läsa ett värde från en array från JS
EMSCRIPTEN_KEEPALIVE
int get_array_value(int* arr, int index) {
    return arr[index];
}

} // extern "C"