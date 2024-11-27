document.addEventListener('DOMContentLoaded', () => {
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const dynamicText = document.getElementById('dynamic-text');
    const exampleInput = document.getElementById('example-input');
    const outputTextarea = document.getElementById('output-textarea');
    const copyButton = document.getElementById('copy-button');

    roleRadios.forEach(radio => {
        radio.addEventListener('change', updateDynamicContent);
    });

    function updateDynamicContent() {
        const selectedRole = document.querySelector('input[name="role"]:checked').value;
        let dynamicTextContent = '';
        let examplePlaceholder = '';

        switch (selectedRole) {
            case 'recruiter':
                dynamicTextContent = 'Jag är rekryterare för';
                examplePlaceholder = 'Namn på ditt företag';
                break;
            case 'freelancer':
                dynamicTextContent = 'Jag söker en frilansare för';
                examplePlaceholder = 'att skapa en enkel hemsida';
                break;
            case 'general':
                dynamicTextContent = 'Jag är intresserad av';
                examplePlaceholder = 'intresseområde';
                break;
        }

        dynamicText.value = dynamicTextContent;
        exampleInput.placeholder = examplePlaceholder;
        exampleInput.value = ''; // Rensa input-fältet
        updateOutputTextarea();
    }

    exampleInput.addEventListener('input', updateOutputTextarea);

    function updateOutputTextarea() {
        const selectedRole = document.querySelector('input[name="role"]:checked').value;
        const inputValue = exampleInput.value.trim() || exampleInput.placeholder;
        let outputContent = '';

        switch (selectedRole) {
            case 'recruiter':
                outputContent = `Jag är rekryterare för ${inputValue}. Analysera Markus Isakssons IT-meriter och ge en bedömning av hans lämplighet för en IT-relaterad roll hos oss.`;
                break;
            case 'freelancer':
                outputContent = `Jag söker en frilansare för ${inputValue}. Bedöm Markus Isakssons lämplighet baserat på hans IT-meriter.`;
                break;
            case 'general':
                outputContent = `Jag är intresserad av ${inputValue}. Analysera Markus Isakssons IT-meriter med fokus på detta område och ge en sammanfattning av hans kompetenser.`;
                break;
        }

        fetch('../assets/data/parsed_FCCdump.txt')
            .then(response => response.text())
            .then(data => {
                outputTextarea.value = outputContent + '\n\n---\n\n' + data;
            })
            .catch(error => console.error('Error loading FCCdump:', error));
    }

    copyButton.addEventListener('click', () => {
        outputTextarea.select();
        document.execCommand('copy');
        copyButton.textContent = 'Kopierad!';
        setTimeout(() => {
            copyButton.textContent = 'Kopiera';
        }, 2000);
    });

    // Initiera innehållet när sidan laddas
    document.querySelector('input[name="role"]:checked').dispatchEvent(new Event('change'));
});