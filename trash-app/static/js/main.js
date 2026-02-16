document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('file-input');
    const chooseFileBtn = document.getElementById('choose-file-btn');
    const uploadArea = document.getElementById('upload-area');
    const uploadedImageDisplay = document.getElementById('uploaded-image-display');
    const uploadedPreviewImg = document.getElementById('uploaded-preview-img');
    const uploadedFileName = document.getElementById('uploaded-file-name');
    const uploadedFileSize = document.getElementById('uploaded-file-size');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const classifyBtn = document.getElementById('classify-btn');

    // Function to reset the upload section
    function resetUploadSection() {
        uploadArea.classList.remove('hidden');
        uploadedImageDisplay.classList.add('hidden');
        uploadedPreviewImg.src = '#';
        fileInput.value = '';
    }

    // --- All your existing JavaScript for file handling ---
    if (chooseFileBtn) {
        chooseFileBtn.addEventListener('click', () => fileInput.click());
    }

    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    uploadArea.classList.add('hidden');
                    uploadedImageDisplay.classList.remove('hidden');
                    uploadedPreviewImg.src = e.target.result;
                    uploadedFileName.textContent = file.name;
                    uploadedFileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ... (Your drag/drop and remove image functions are here) ...

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', resetUploadSection);
    }

    // --- NEW: LOGIC FOR GEMINI SUGGESTIONS ---

    const suggestionBtn = document.getElementById('get-suggestion-btn');
    const suggestionContainer = document.getElementById('suggestion-container');

    if (suggestionBtn) {
        suggestionBtn.addEventListener('click', async function () {
            const trashType = this.dataset.trashType;
            
            suggestionContainer.classList.remove('hidden');
            suggestionContainer.innerHTML = '<p class="loading-message">♻️ Asking the AI for disposal tips...</p>'; // Added a class for potential styling

            try {
                const response = await fetch('/get_disposal_suggestion', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ trash_type: trashType }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();

                if (data.error) {
                    suggestionContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                } else {
                    // --- NEW: Convert Markdown to HTML using marked.js ---
                    const htmlContent = marked.parse(data.suggestion);
                    suggestionContainer.innerHTML = htmlContent;
                }

            } catch (error) {
                console.error('Error fetching disposal suggestion:', error);
                suggestionContainer.innerHTML = '<p style="color: red;">Sorry, something went wrong. Please try again.</p>';
            }
        });
    }
});