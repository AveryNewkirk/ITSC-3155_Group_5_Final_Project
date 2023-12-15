document.addEventListener('DOMContentLoaded', function () {
    function updatePreview() {
        let title = document.getElementById('listing-title').value;
        let price = document.getElementById('price').value;
        let description = document.getElementById('item-description').value;
        if (description.length > 90) {
            description = description.substring(0, 180);
        }

        document.getElementById('listing-title-preview').textContent = title || 'Listing Title';
        document.getElementById('listing-price-preview').textContent = price ? `$${price}` : '$0.00';
        document.getElementById('listing-description-preview').textContent = description || 'Description preview...';
    }

    document.getElementById('listing-title').addEventListener('input', updatePreview);
    document.getElementById('price').addEventListener('input', updatePreview);
    document.getElementById('item-description').addEventListener('input', updatePreview);

    document.getElementById('generate-description').addEventListener('click', function () {
        if (document.getElementById('upload-pictures').files.length == 0) {
            alert('Please upload an image first!')
            throw new Error('No files uploaded')
        }
        let album_id = document.getElementById('album-id').value;
        toggleLoadingOverlay()
        fetch('/generate_description', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ album_id: album_id })
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('item-description').value = data.description;
                updatePreview();
            })
            .catch(error => console.error('Error: ', error))
            .finally(() => toggleLoadingOverlay())
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('upload-pictures');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const listingPreviewImageContainer = document.getElementById('listing-image-preview');
    const listingPreviewImage = document.getElementById('listing-image-preview-img');

    fileInput.addEventListener('change', function (event) {
        imagePreviewContainer.innerHTML = '';

        const files = event.target.files;
        let firstImageRendered = false;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            if (!file.type.match('image.*')) {
                continue;
            }

            const reader = new FileReader();

            reader.onload = (function (theFile) {
                return function (e) {
                    const span = document.createElement('span');
                    span.innerHTML = `<img class="thumb" src="${e.target.result}" title="${escape(theFile.name)}"/>`;
                    imagePreviewContainer.insertBefore(span, null);

                    if (!firstImageRendered) {
                        listingPreviewImage.src = e.target.result;
                        listingPreviewImage.classList.toggle('hidden');
                        listingPreviewImageContainer.classList.toggle('empty');
                        firstImageRendered = true;
                    }
                };
            })(file);

            reader.readAsDataURL(file);
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('upload-pictures').addEventListener('change', function (event) {
        uploadFiles(event.target.files);
    });
})

function uploadFiles(files) {
    let formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('upload-pictures', files[i]);
    }
    fetch('/upload_images', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            let album_id = data.album_id;
            document.getElementById('album-id').value = album_id;
        })
        .catch(error => {
            console.error('Error: ', error)
        })
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('generate-images').addEventListener('click', function () {
        description = document.getElementById('item-description').value
        if (description) {
            generateImages(description);
        } else {
            alert('Please generate or write your own detailed description first!');
        }
    })
})

function generateImages(description) {
    const image_placeholders = document.querySelectorAll('.image-placeholder')
    if (!image_placeholders.item(3).classList.contains('empty')) {
        alert('Number of generated photos limit reached!')
        throw new Error('Container for generated images (div.generated-images) is full.')
    }
    toggleLoadingOverlay()
    fetch('/generate_pictures', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ description: description })
    })
        .then(response => response.json())
        .then(data => {
            const image_url = data.image_url;
            for (const container of image_placeholders) {
                if (!container.childElementCount > 0) {
                    const image = document.createElement('img')
                    image.classList.add('model-img', 'populated')
                    image.src = image_url
                    container.appendChild(image)
                    container.classList.toggle('empty')
                    break
                }
            };
        })
        .catch(error => console.error('Error: ', error))
        .finally(() => toggleLoadingOverlay())
}

function toggleLoadingOverlay() {
    document.querySelector('.loading').classList.toggle('hidden')
}

function populatedSelectedImages() {
    let checkboxes = document.querySelectorAll('.image-checkbox input[type="checkbox"]:checked');
    let i = 1
    checkboxes.forEach(checkbox => {
        let image_url = checkbox.nextElementSibling.querySelector('.model-img').src;
        let hidden_input_id = `model-image-url-${i++}`;
        let hidden_input = document.getElementById(hidden_input_id)
        hidden_input.value = image_url;
    })
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('sell-form').onsubmit = populatedSelectedImages;
})
