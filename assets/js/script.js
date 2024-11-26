function changeLanguage(lang) {
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'index.html'; // Default to 'index.html' if no filename is present

    // Define translations for each page
    const translations = {
        'index.html': 'index_eng.html',
        'index_eng.html': 'index.html',
        'certificates.html': 'certificates_eng.html',
        'certificates_eng.html': 'certificates.html',
        'showcase.html': 'showcase_eng.html',
        'showcase_eng.html': 'showcase.html'
    };

    if (lang === 'sv' && page.includes('_eng')) {
        // Switch to the Swedish version
        const swedishPage = Object.keys(translations).find(key => translations[key] === page);
        if (swedishPage) window.location.href = swedishPage;
    } else if (lang === 'en' && !page.includes('_eng')) {
        // Switch to the English version
        const englishPage = translations[page];
        if (englishPage) window.location.href = englishPage;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const textAreas = document.querySelectorAll('.code-container textarea');
    const copyButtons = document.querySelectorAll('.copy-button');

    if (textAreas.length >= 2) {
        // Load and display content of readjson.js
        fetch('https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/assets/js/readjson.js')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch readjson.js');
                return response.text();
            })
            .then(data => {
                textAreas[0].value = data;
            })
            .catch(error => console.error('Error loading readjson.js:', error));

        // Load and display content of parsed_FCCdump.txt
        fetch('https://raw.githubusercontent.com/MarkusIsaksson1982/MarkusIsaksson1982.github.io/main/assets/data/parsed_FCCdump.txt')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch parsed_FCCdump.txt');
                return response.text();
            })
            .then(data => {
                textAreas[1].value = data;
            })
            .catch(error => console.error('Error loading parsed_FCCdump.txt:', error));
    }

    // Detect the current language from the page URL and set button text accordingly
    const isEnglish = window.location.pathname.includes('_eng');
    copyButtons.forEach(button => button.textContent = isEnglish ? 'Copy' : 'Kopiera');

    // Add click event listeners to the buttons
    copyButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            if (textAreas[index]) {
                navigator.clipboard.writeText(textAreas[index].value)
                    .then(() => {
                        // Change the button text to indicate success
                        button.textContent = isEnglish ? 'Copied' : 'Kopierad';
                        setTimeout(() => {
                            // Revert the button text after a short delay
                            button.textContent = isEnglish ? 'Copy' : 'Kopiera';
                        }, 2000);
                    })
                    .catch(err => console.error('Failed to copy text:', err));
            }
        });
    });
});
