// edited 16 Dec 2024 1708
document.addEventListener("DOMContentLoaded", () => {
    const lang = document.documentElement.lang; // Detect language from the page
    const headerPath = `../components/header_${lang}.html`;
    const footerPath = `../components/footer_${lang}.html`;

    fetch(headerPath)
        .then(response => response.text())
        .then(data => {
            document.querySelector("header").innerHTML = data;
            setupLanguageSwitching(); // Ensure language switching works
        })
        .catch(error => console.error("Error loading header:", error));

    fetch(footerPath)
        .then(response => response.text())
        .then(data => {
            document.querySelector("footer").innerHTML = data;
        })
        .catch(error => console.error("Error loading footer:", error));

    function setupLanguageSwitching() {
        const langButtons = document.querySelectorAll('.lang-icon');
        langButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetLang = button.getAttribute('onclick').match(/'([^']+)'/)[1];
                switchLanguage(targetLang);
            });
        });
    }

    function switchLanguage(targetLang) {
        const currentPath = window.location.pathname;
        const currentPage = currentPath.split('/').pop(); // Get the current file name
        const isSwedish = currentPath.includes('/sv/');
        const isEnglish = currentPath.includes('/en/');

        if (targetLang === 'sv' && isEnglish) {
            window.location.href = currentPath.replace('/en/', '/sv/');
        } else if (targetLang === 'en' && isSwedish) {
            window.location.href = currentPath.replace('/sv/', '/en/');
        } else {
            // Default to the homepage of the selected language
            window.location.href = `/${targetLang}/index.html`;
        }
    }
});
