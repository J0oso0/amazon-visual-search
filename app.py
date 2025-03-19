from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import json
import requests
import re
from PIL import Image
import io
import numpy as np
import boto3
import time
import uuid
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Amazon Product API credentials (mock - you'll need to set up real credentials)
AMAZON_API_KEY = os.environ.get('AMAZON_API_KEY', 'your_amazon_api_key')
AMAZON_SECRET_KEY = os.environ.get('AMAZON_SECRET_KEY', 'your_amazon_secret_key')
AMAZON_PARTNER_TAG = os.environ.get('AMAZON_PARTNER_TAG', 'your_partner_tag')

# AWS credentials for Rekognition (mock - you'll need to set up real credentials)
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'your_aws_access_key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'your_aws_secret_key')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize AWS Rekognition client
try:
    rekognition_client = boto3.client(
        'rekognition',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
except Exception as e:
    logger.error(f"Failed to initialize AWS Rekognition client: {e}")
    rekognition_client = None

# Temporary storage directory for uploaded images
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/search', methods=['POST'])
def search_products():
    """
    Handle product search requests with image data
    """
    try:
        # Check if request contains image data
        if 'image' not in request.json:
            return jsonify({"error": "No image data provided"}), 400
        
        image_data = request.json['image']
        
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return jsonify({"error": "Invalid image data"}), 400
        
        # Process image with AWS Rekognition
        labels = detect_labels(image_bytes)
        
        if not labels:
            return jsonify({"error": "Could not detect any objects in the image"}), 400
        
        # Search Amazon for products based on detected labels
        products = search_amazon_products(labels)
        
        # Return the search results
        return jsonify({"products": products})
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

def detect_labels(image_bytes):
    """
    Detect labels in the image using AWS Rekognition
    """
    try:
        if rekognition_client is None:
            # Mock the response if AWS client isn't configured
            return mock_detect_labels(image_bytes)
        
        response = rekognition_client.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10,
            MinConfidence=70
        )
        
        # Extract labels with confidence
        labels = [
            {
                'name': label['Name'],
                'confidence': label['Confidence']
            }
            for label in response['Labels']
        ]
        
        # Sort by confidence
        labels.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"Detected labels: {labels}")
        return labels
    
    except Exception as e:
        logger.error(f"Error detecting labels: {e}")
        return mock_detect_labels(image_bytes)

def mock_detect_labels(image_bytes):
    """
    Mock label detection when AWS Rekognition is not available
    """
    try:
        # Try to open the image to check if it's valid
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify it's an image
        
        # Return mock labels - in a real app, you'd use actual AI here
        mock_labels = [
            {"name": "Headphones", "confidence": 98.5},
            {"name": "Electronics", "confidence": 96.2},
            {"name": "Wireless", "confidence": 85.7},
            {"name": "Audio", "confidence": 82.3}
        ]
        
        logger.info("Using mock label detection")
        return mock_labels
    
    except Exception as e:
        logger.error(f"Invalid image in mock detection: {e}")
        return []

def search_amazon_products(labels):
    """
    Search Amazon products based on detected labels
    """
    try:
        # In a real application, you would use Amazon's Product Advertising API
        # For this example, we'll return mock products
        
        # Extract the top label names
        search_terms = [label['name'] for label in labels[:3]]
        search_query = " ".join(search_terms)
        
        logger.info(f"Searching Amazon for: {search_query}")
        
        # Mock the API call
        return mock_amazon_api_call(search_query)
    
    except Exception as e:
        logger.error(f"Error searching Amazon products: {e}")
        return []

def mock_amazon_api_call(search_query):
    """
    Mock Amazon API call with realistic product data
    """
    # Generate deterministic but "random" products based on search query
    # This way, the same search terms will return the same products
    seed = sum(ord(c) for c in search_query)
    np.random.seed(seed)
    
    # Define possible product categories
    categories = {
        "Electronics": [
            {"title": "Wireless Bluetooth Earbuds", "price": "$49.99", "rating": 4.5},
            {"title": "Noise Cancelling Headphones", "price": "$129.99", "rating": 4.8},
            {"title": "Portable Bluetooth Speaker", "price": "$34.99", "rating": 4.7},
            {"title": "Smart Watch with Heart Rate Monitor", "price": "$79.99", "rating": 4.2},
            {"title": "Wireless Charging Pad", "price": "$25.99", "rating": 4.0}
        ],
        "Home": [
            {"title": "Smart LED Light Bulbs", "price": "$39.99", "rating": 4.6},
            {"title": "Robot Vacuum Cleaner", "price": "$199.99", "rating": 4.4},
            {"title": "Air Purifier with HEPA Filter", "price": "$89.99", "rating": 4.3},
            {"title": "Digital Kitchen Scale", "price": "$15.99", "rating": 4.5},
            {"title": "Non-Stick Cookware Set", "price": "$75.99", "rating": 4.7}
        ],
        "Apparel": [
            {"title": "Men's Running Shoes", "price": "$65.99", "rating": 4.2},
            {"title": "Women's Yoga Pants", "price": "$29.99", "rating": 4.6},
            {"title": "Waterproof Hiking Jacket", "price": "$79.99", "rating": 4.5},
            {"title": "Cotton T-Shirt 3-Pack", "price": "$24.99", "rating": 4.3},
            {"title": "Winter Thermal Gloves", "price": "$19.99", "rating": 4.4}
        ]
    }
    
    # Determine which category to use based on search query
    if any(word in search_query.lower() for word in ["headphone", "earbud", "speaker", "watch", "electronic"]):
        category = "Electronics"
    elif any(word in search_query.lower() for word in ["light", "vacuum", "kitchen", "home", "cook"]):
        category = "Home"
    else:
        category = "Apparel"
    
    # Select products and add random variation
    products = categories[category].copy()
    
    # Shuffle products deterministically
    indices = np.random.permutation(len(products))
    selected_products = [products[i] for i in indices[:4]]
    
    # Add product details
    for i, product in enumerate(selected_products):
        # Generate unique product ID
        product_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{search_query}-{i}"))
        
        # Add to product
        product["id"] = product_id
        product["image"] = f"https://via.placeholder.com/150?text={category}+Product"
        product["url"] = f"https://amazon.com/dp/{product_id}"
        
        # Add search relevance
        product["relevance"] = round(100 - i * 5 - np.random.randint(0, 10), 1)
    
    return selected_products

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    API health check endpoint
    """
    return jsonify({"status": "ok", "timestamp": time.time()})

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Set debug mode based on environment
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
