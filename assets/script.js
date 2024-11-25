document.querySelector('.language-switch').addEventListener('click', (event) => {
    const target = event.target.dataset.lang;
    if (target) {
        alert(`Language switched to ${target}`);
        // Placeholder for language-switching logic
    }
});
