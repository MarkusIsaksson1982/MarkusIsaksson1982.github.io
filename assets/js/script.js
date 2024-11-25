// assets/js/script.js
function changeLanguage(lang) {
    const path = window.location.pathname;
    const page = path.split('/').pop();

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
