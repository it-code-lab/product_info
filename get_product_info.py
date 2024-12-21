from bs4 import BeautifulSoup

def generate_product_html(local_html_path):
    try:
        # Read the local HTML file
        with open(local_html_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract the main product image
        main_image = soup.find("img", {"id": "landingImage"})
        main_image_url = main_image['src'] if main_image else "No main image found"
        
        # Extract thumbnail images
        thumbnail_div = soup.find("div", {"id": "altImages"})
        thumbnail_images = []
        if thumbnail_div:
            thumbnails = thumbnail_div.find_all("img")
            for thumb in thumbnails:
                if 'src' in thumb.attrs:
                    thumbnail_images.append(thumb['src'])
        
        # Extract rating and review count
        rating = soup.find("span", {"class": "a-icon-alt"})
        rating_text = rating.get_text(strip=True) if rating else "No rating found"
        stars = float(rating_text.split()[0]) if rating else 0  # Extract star rating
        review_count = soup.find("span", {"id": "acrCustomerReviewText"})
        review_count_text = review_count.get_text(strip=True) if review_count else "0 reviews"
        
        # Generate HTML snippet
        html_snippet = f"""
        <div class="product-container">
            <div class="product-main-image">
                <img src="{main_image_url}" alt="Main Product Image" id="mainImage">
            </div>
            <div class="product-thumbnails">
                {''.join([f'<img src="{img}" alt="Thumbnail" onclick="changeMainImage(\'{img}\')">' for img in thumbnail_images])}
            </div>
            <div class="product-reviews">
                <div class="stars" style="--rating: {stars};" aria-label="Rating of {stars} out of 5"></div>
                <p>{review_count_text}</p>
            </div>
        </div>
        """
        return html_snippet
    
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"

# Example usage
local_html_path = "product_page.html"  # Replace with your local HTML file path
product_html = generate_product_html(local_html_path)

with open("output_snippet.html", "w", encoding="utf-8") as output_file:
    output_file.write(product_html)
