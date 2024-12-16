document.addEventListener('DOMContentLoaded', () => {
    const fileUrls = [
        '../assets/data/parsed_FCCdump_metadata_only.txt',
        '../assets/data/parsed_FCCdump_compact.txt',
        '../assets/data/parsed_FCCdump_verbose.txt',
    ];

    const textAreas = document.querySelectorAll('.code-container textarea');
    const copyButtons = document.querySelectorAll('.copy-button');
    const introTextArea = document.getElementById('intro-text');

    // Load file content with prefilled intro text
    fileUrls.forEach((url, index) => {
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Failed to fetch ${url}`);
                return response.text();
            })
            .then(data => {
                textAreas[index].value = `${introTextArea.value.trim()}\n\n${data}`; // Combine intro text and fetched content
            })
            .catch(error => console.error(`Error loading file: ${url}`, error));
    });

    // Update text areas when the intro text is modified
    introTextArea.addEventListener('input', () => {
        fileUrls.forEach((url, index) => {
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error(`Failed to fetch ${url}`);
                    return response.text();
                })
                .then(data => {
                    textAreas[index].value = `${introTextArea.value.trim()}\n\n${data}`;
                })
                .catch(error => console.error(`Error updating file: ${url}`, error));
        });
    });

    // Copy to clipboard functionality
    copyButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            textAreas[index].select();
            navigator.clipboard.writeText(textAreas[index].value)
                .then(() => {
                    button.textContent = 'Copied!';
                    setTimeout(() => (button.textContent = 'Copy'), 2000);
                })
                .catch(err => console.error('Error copying text:', err));
        });
    });
});
