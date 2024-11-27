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
                dynamicTextContent = 'I am a recruiter for';
                examplePlaceholder = 'Your company name';
                break;
            case 'freelancer':
                dynamicTextContent = 'I am looking for a freelancer to';
                examplePlaceholder = 'create a simple website';
                break;
            case 'general':
                dynamicTextContent = 'I am interested in';
                examplePlaceholder = 'your area of interest';
                break;
        }

        dynamicText.value = dynamicTextContent;
        exampleInput.placeholder = examplePlaceholder;
        exampleInput.value = ''; // Clear the input field
        updateOutputTextarea();
    }

    exampleInput.addEventListener('input', updateOutputTextarea);

    function updateOutputTextarea() {
        const selectedRole = document.querySelector('input[name="role"]:checked').value;
        const inputValue = exampleInput.value.trim() || exampleInput.placeholder;
        let outputContent = '';

        switch (selectedRole) {
            case 'recruiter':
                outputContent = `I am a recruiter for ${inputValue}. Analyze Markus Isaksson's IT credentials and evaluate his suitability for an IT-related role at our company.`;
                break;
            case 'freelancer':
                outputContent = `I am looking for a freelancer to ${inputValue}. Assess Markus Isaksson's suitability based on his IT credentials.`;
                break;
            case 'general':
                outputContent = `I am interested in ${inputValue}. Analyze Markus Isaksson's IT credentials with a focus on this area and provide a summary of his competencies.`;
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
        copyButton.textContent = 'Copied!';
        setTimeout(() => {
            copyButton.textContent = 'Copy';
        }, 2000);
    });

    // Initialize the content when the page loads
    document.querySelector('input[name="role"]:checked').dispatchEvent(new Event('change'));
});
