document.addEventListener("DOMContentLoaded", () => {
    const lang = document.documentElement.lang; // Detect language from the page
    const headerPath = `../components/header_${lang}.html`;
    const footerPath = `../components/footer_${lang}.html`;

    fetch(headerPath)
        .then(response => response.text())
        .then(data => {
            document.querySelector("header").innerHTML = data;
            disableCurrentLanguageButton(lang); // Call the function to disable the current language button
        })
        .catch(error => console.error("Error loading header:", error));

    fetch(footerPath)
        .then(response => response.text())
        .then(data => {
            document.querySelector("footer").innerHTML = data;
        })
        .catch(error => console.error("Error loading footer:", error));
});

function disableCurrentLanguageButton(currentLang) {
    const langButtons = document.querySelectorAll('.lang-icon');
    langButtons.forEach(button => {
        const lang = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        if (lang === currentLang) {
            // Disable the button for the current language
            button.style.opacity = "0.5";
            button.style.pointerEvents = "none";
            button.title = "You are already viewing this language";
        }
    });
}
