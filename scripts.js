// Language switching functionality
const langSv = document.getElementById('lang-sv');
const langEn = document.getElementById('lang-en');
const content = document.querySelector('main');

langSv.addEventListener('click', () => switchLanguage('sv'));
langEn.addEventListener('click', () => switchLanguage('en'));

function switchLanguage(language) {
    fetch(`lang/${language}.json`)
        .then((response) => response.json())
        .then((data) => {
            document.querySelector('title').textContent = data.title;
            content.innerHTML = `
                <section id="merits">
                    <h1>${data.meritsTitle}</h1>
                    <p>${data.meritsContent}</p>
                </section>
                <section id="showcase">
                    <h1>${data.showcaseTitle}</h1>
                    <p>${data.showcaseContent}</p>
                </section>
                <section id="certificates">
                    <h1>${data.certificatesTitle}</h1>
                    <p>${data.certificatesContent}</p>
                </section>
            `;
            document.querySelectorAll('.language-switch span').forEach(span => span.classList.remove('active-lang'));
            document.getElementById(`lang-${language}`).classList.add('active-lang');
        })
        .catch((error) => console.error('Error loading language file:', error));
}
