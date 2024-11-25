document.querySelectorAll('.lang-icon').forEach(icon => {
    icon.addEventListener('click', (event) => {
        const targetLang = event.target.dataset.lang;
        alert(`Language switched to: ${targetLang}`); // Placeholder for language switching logic
        // Future implementation to dynamically load language-specific content
    });
});
