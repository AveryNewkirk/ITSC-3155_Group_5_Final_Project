document.addEventListener('DOMContentLoaded', function () {
    // Function to update the preview
    function updatePreview() {
        // Get the values from the form elements
        const title = document.getElementById('listing-title').value;
        const price = document.getElementById('price').value;
        const description = document.getElementById('item-description').value;

        // Set the values in the preview elements
        document.getElementById('listing-title-preview').textContent = title || 'Listing Title';
        document.getElementById('listing-price-preview').textContent = price ? `$${price}` : '$0.00';
        document.getElementById('listing-description-preview').textContent = description || 'Description preview...';
    }

    // Add event listeners to form fields
    document.getElementById('listing-title').addEventListener('input', updatePreview);
    document.getElementById('price').addEventListener('input', updatePreview);
    document.getElementById('item-description').addEventListener('input', updatePreview);

    document.getElementById('generate-description').addEventListener('click', function () {
        let album_id = document.getElementById('album-id').value;
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
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Get the file input and the image preview container
    const fileInput = document.getElementById('upload-pictures');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const listingPreviewImage = document.getElementById('listing-image-preview-img');

    fileInput.addEventListener('change', function (event) {
        // Clear out the previous images
        imagePreviewContainer.innerHTML = '';

        // Get the files from the input
        const files = event.target.files;
        let firstImageRendered = false;

        // Loop through the FileList and render image files as thumbnails.
        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // Only process image files.
            if (!file.type.match('image.*')) {
                continue;
            }

            const reader = new FileReader();

            // Closure to capture the file information.
            reader.onload = (function (theFile) {
                return function (e) {
                    // Render thumbnail.
                    const span = document.createElement('span');
                    span.innerHTML = `<img class="thumb" src="${e.target.result}" title="${escape(theFile.name)}"/>`;
                    imagePreviewContainer.insertBefore(span, null);

                    // If it's the first image and it hasn't been rendered in the preview yet
                    if (!firstImageRendered) {
                        listingPreviewImage.src = e.target.result; // Set the first image as the preview
                        listingPreviewImage.classList.toggle('hide');
                        firstImageRendered = true;
                    }
                };
            })(file);

            // Read in the image file as a data URL.
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
        .catch(error => console.error('Error: ', error))
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
    fetch('/generate_pictures', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ description: description })
    })
        .then(response => response.json())
        .then(data => {
            image_url = data.image_url;
            console.log(image_url)
            const modelImages = document.querySelectorAll('.model-img');
            console.log(modelImages)
            modelImages.forEach(image => {
                if (!image.classList.contains('populated')) {
                    image.setAttribute('src', image_url);
                    console.log(image)
                    return
                }
            })
        })
        .catch(error => console.error('Error: ', error))
}