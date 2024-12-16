document.addEventListener("DOMContentLoaded", () => {
    const fileUrls = [
        '../assets/data/parsed_FCCdump_metadata_only.txt',
        '../assets/data/parsed_FCCdump_compact.txt',
        '../assets/data/parsed_FCCdump_verbose.txt',
    ];

    const textAreas = document.querySelectorAll('.code-container textarea');
    const copyButtons = document.querySelectorAll('.copy-button');

    // Load file content
    fileUrls.forEach((url, index) => {
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Failed to fetch ${url}`);
                return response.text();
            })
            .then(data => {
                textAreas[index].value = data;
            })
            .catch(error => console.error(`Error loading file: ${url}`, error));
    });

    // Copy to clipboard
    copyButtons.forEach((button, index) => {
        button.addEventListener("click", () => {
            textAreas[index].select();
            document.execCommand("copy");
            button.textContent = "Kopierad!";
            setTimeout(() => (button.textContent = "Kopiera"), 2000);
        });
    });
});
