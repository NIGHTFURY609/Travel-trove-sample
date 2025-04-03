const API_KEY = 'KEM2fmcdYRAg7pZRErRWCirS4VXAd1eTeD3QInkEpZmm9KmD7JuTPhVR';
const API_URL = 'https://api.pexels.com/v1/search?query=';

// Fetch a product image from Pexels
async function fetchProductImage(query) {
  try {
    const response = await fetch(API_URL + query + '&per_page=1', {
      headers: {
        Authorization: API_KEY
      }
    });
    const data = await response.json();
    return data.photos.length > 0 ? data.photos[0].src.medium : 'https://via.placeholder.com/150';
  } catch (error) {
    console.error('Error fetching image:', error);
    return 'https://via.placeholder.com/150';
  }
}

// Update each product's image and display them
async function updateProductImages() {
  for (let product of products) {
    product.image = await fetchProductImage(product.name);
  }
  displayProducts(products);
}

// Sample product data
const products = [
  { id: 1, name: 'Hiking Backpack', category: 'hiking', price: 49.99 },
  { id: 2, name: 'Travel Gloves', category: 'travel', price: 29.99 },
  { id: 3, name: 'Camping Tent', category: 'camping', price: 199.99 },
  { id: 4, name: 'Hiking Boots', category: 'hiking', price: 89.99 },
  { id: 5, name: 'Lightweight Sleeping Bag', category: 'camping', price: 2799 },
  { id: 6, name: 'Climbing Rope', category: 'hiking', price: 3499 },
  { id: 7, name: 'Solar Power Bank', category: 'travel', price: 2299 },
  { id: 8, name: 'Waterproof Hiking Jacket', category: 'hiking', price: 5999 },
  { id: 9, name: 'Portable Folding Table', category: 'camping', price: 4499 },
  { id: 10, name: 'Multi-tool Survival Knife', category: 'camping', price: 1599 },
  { id: 11, name: 'LED Headlamp', category: 'camping', price: 999 },
  { id: 12, name: 'Inflatable Kayak', category: 'water sports', price: 18999 },
  { id: 13, name: 'Outdoor Cooking Set', category: 'camping', price: 3999 },
  { id: 14, name: 'Trekking Backpack', category: 'hiking', price: 6499 },
  { id: 15, name: 'Ski Goggles', category: 'skiing', price: 3299 },
  { id: 16, name: 'Compression Packing Bags', category: 'travel', price: 2499 },
  { id: 17, name: 'Hiking GPS Device', category: 'hiking', price: 15999 },
  { id: 18, name: 'Emergency Thermal Blanket', category: 'camping', price: 499 },
  { id: 19, name: 'Underwater Waterproof Camera', category: 'travel', price: 12999 },
  { id: 20, name: 'Portable Hammock with Stand', category: 'camping', price: 9999 },
  { id: 21, name: 'Cycling Hydration Pack', category: 'cycling', price: 3499 },
  { id: 22, name: 'Camping Fire Starter Kit', category: 'camping', price: 799 },
  { id: 23, name: 'Tactical Flashlight', category: 'camping', price: 1299 },
  { id: 24, name: 'Foldable Fishing Rod', category: 'fishing', price: 4599 },
];

// Function to display products on the page
function displayProducts(productsToDisplay) {
  const productDisplay = document.getElementById('productDisplay');
  productDisplay.innerHTML = ''; // Clear previous products

  productsToDisplay.forEach(product => {
    const productElement = document.createElement('div');
    productElement.className = 'product';
    productElement.innerHTML = `
      <img src="${product.image}" alt="${product.name}">
      <h3>${product.name}</h3>
      <p>Price: $${product.price.toFixed(2)}</p>
      <div class="product-actions">
        <button class="add-to-cart" onclick="addToCart(${product.id})">Add to Cart</button>
        <button class="buy-now" onclick="buyNow(${product.id})">Buy Now</button>
      </div>
    `;
    productDisplay.appendChild(productElement);
  });
}

// Filter function to handle category, price range, and sort order
function filterProducts() {
  const categoryFilter = document.getElementById('categoryFilter').value;
  const priceRange = document.getElementById('priceRange').value;
  const sortOrder = document.getElementById('sortOrder').value;

  let filteredProducts = [...products]; // Create a copy of the products array

  // Filter by category
  if (categoryFilter !== 'all') {
    filteredProducts = filteredProducts.filter(product => product.category === categoryFilter);
  }

  // Filter by price range
  if (priceRange !== 'all') {
    const [minPrice, maxPrice] = priceRange.split('-').map(Number);
    filteredProducts = filteredProducts.filter(product => product.price >= minPrice && product.price <= maxPrice);
  }

  // Sort products
  if (sortOrder === 'price-low-high') {
    filteredProducts.sort((a, b) => a.price - b.price);
  } else if (sortOrder === 'price-high-low') {
    filteredProducts.sort((a, b) => b.price - a.price);
  }
  
  displayProducts(filteredProducts);
}

// Function to handle "Add to Cart" action
function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  alert(`${product.name} has been added to your cart!`);
}

// Function to handle "Buy Now" action
function buyNow(productId) {
  const product = products.find(p => p.id === productId);
  alert(`You have purchased ${product.name}!`);
}

// Fetch images and update product display on page load
updateProductImages();
