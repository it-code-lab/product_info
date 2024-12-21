from bs4 import BeautifulSoup
import json

def generate_product_html(local_html_path, base_path="saved_product_pages/"):
    try:
        # Read the local HTML file
        with open(local_html_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all images with class "a-dynamic-image"
        dynamic_images = soup.find_all("img", {"class": "a-dynamic-image"})
        if not dynamic_images:
            return "<p>No images found with class 'a-dynamic-image'.</p>"
        
        # Extract all unique image URLs
        image_urls = []
        for img in dynamic_images:
            src = img.get("src")
            if src and src not in image_urls:
                src = src[2:]
                image_urls.append(base_path + src)

        if not image_urls:
            return "<p>No valid image URLs found.</p>"

        # Use the first image as the default large display image
        main_image_url = image_urls[0]

        # Extract price to pay
        price_to_pay = soup.find("span", {"class": "priceToPay"})
        price_to_pay_text = price_to_pay.get_text(strip=True) if rating else "No price found"

        # Extract rating and review count
        rating = soup.find("span", {"class": "a-icon-alt"})
        rating_text = rating.get_text(strip=True) if rating else "No rating found"
        stars = float(rating_text.split()[0]) if rating else 0  # Extract star rating
        review_count = soup.find("span", {"id": "acrCustomerReviewText"})
        review_count_text = review_count.get_text(strip=True) if review_count else "0 reviews"

        # Generate HTML snippet
        html_snippet = (
            '<div class="product-container">'
            '<div class="product-main-image">'
            f'<img src="{main_image_url}" alt="Main Product Image" id="mainImage">'
            '</div>'
            '<div class="product-thumbnails">'
            + ''.join(
                f'<img src="{img}" alt="Thumbnail" style="width: 50px; height: auto;" onclick="changeMainImage(\'{img}\')">' for img in image_urls
            ) +
            '</div>'
            '<div class="product-reviews">'
            f'<p>{price_to_pay_text}</p>'
            '</div>'
            '<div class="product-reviews">'
            f'<div class="stars" style="--rating: {stars};" aria-label="Rating of {stars} out of 5"></div>'
            f'<p>{review_count_text}</p>'
            '</div>'
            '</div>'
        )
        return html_snippet
    
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"

# Example usage
local_html_path = "saved_product_pages/1.html"  # Replace with your local HTML file path
product_html = generate_product_html(local_html_path)

with open("output_snippet.html", "w", encoding="utf-8") as output_file:
    output_file.write(product_html)

