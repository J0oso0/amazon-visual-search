// Updated searchProducts function for the frontend
// Replace the current searchProducts function with this one

function searchProducts() {
    // Show loading spinner
    loading.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Get the image data
    const imageData = capturedImage.src;
    
    // Send the image to the backend
    fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: imageData
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server error');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        loading.style.display = 'none';
        
        // Check if we have products
        if (data.products && data.products.length > 0) {
            // Display the products
            displayProducts(data.products);
            resultsContainer.style.display = 'block';
        } else {
            alert('No products found. Please try a different image.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loading.style.display = 'none';
        alert('Error searching for products. Please try again.');
    });
}

// New function to display real products
function displayProducts(products) {
    // Clear previous results
    productResults.innerHTML = '';
    
    // Add products to the results
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.innerHTML = `
            <img src="${product.image}" alt="${product.title}">
            <h3>${product.title}</h3>
            <div class="price">${product.price}</div>
            <div>Rating: ${product.rating}★</div>
            <button class="button" onclick="window.open('${product.url}', '_blank')">View on Amazon</button>
        `;
        productResults.appendChild(productCard);
    });
}