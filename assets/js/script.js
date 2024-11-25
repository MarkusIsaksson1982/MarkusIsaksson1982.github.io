// assets/js/script.js
function changeLanguage(lang) {
    const path = window.location.pathname;
    const page = path.split('/').pop();

    const translations = {
        'index.html': 'index_eng.html',
        'index_eng.html': 'index.html',
        'certificates.html': 'certificates_eng.html',
        'certificates_eng.html': 'certificates.html',
        'showcase.html': 'showcase_eng.html',
        'showcase_eng.html': 'showcase.html'
    };

    const newPage = lang === 'sv' ? translations[page] : translations[page];
    if (newPage) {
        window.location.href = newPage;
    }
}
