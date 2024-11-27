// Update this comment with the time for the latest update: 2024-11-27 14:42

document.addEventListener('DOMContentLoaded', () => {
  const textAreas = document.querySelectorAll('.code-container textarea');
  const copyButtons = document.querySelectorAll('.copy-button');

  if (textAreas.length === 0 || copyButtons.length === 0) {
    console.error("Error: Textareas or copy buttons are missing from the DOM.");
    return;
  }

  copyButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      const textArea = textAreas[index];
      if (!textArea) {
        console.error(`Error: No textarea found for button at index ${index}.`);
        return;
      }

      const text = textArea.value;

      // Try using the modern Clipboard API
      navigator.clipboard.writeText(text).then(() => {
        button.textContent = 'Kopierad!'; // Success feedback
        setTimeout(() => (button.textContent = 'Kopiera'), 2000);
      }).catch((err) => {
        console.error('Clipboard API failed. Using fallback:', err);
        fallbackCopyTextToClipboard(text, button);
      });
    });
  });
});

function fallbackCopyTextToClipboard(text, button) {
  const tempTextArea = document.createElement('textarea');
  tempTextArea.value = text;
  tempTextArea.style.position = 'fixed'; // Prevent scrolling
  document.body.appendChild(tempTextArea);
  tempTextArea.focus();
  tempTextArea.select();

  try {
    if (document.execCommand('copy')) {
      button.textContent = 'Kopierad!';
      setTimeout(() => (button.textContent = 'Kopiera'), 2000);
    } else {
      console.error('Fallback copy command failed.');
    }
  } catch (err) {
    console.error('Fallback: Unable to copy', err);
  }

  document.body.removeChild(tempTextArea);
}

function changeLanguage(lang) {
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop(); // Get the current file name
    const isSwedish = currentPath.includes('/sv/');
    const isEnglish = currentPath.includes('/en/');

    if (lang === 'sv' && isEnglish) {
        window.location.href = currentPath.replace('/en/', '/sv/');
    } else if (lang === 'en' && isSwedish) {
        window.location.href = currentPath.replace('/sv/', '/en/');
    } else {
        // Default to the homepage of the selected language
        window.location.href = `/${lang}/index.html`;
    }
}
