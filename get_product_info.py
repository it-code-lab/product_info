import pandas as pd
from bs4 import BeautifulSoup
import os
import requests
import shutil

def load_mapping(mapping_file):
    """Load the mapping of Amazon URLs to local product pages from an Excel file."""
    mapping = pd.read_excel(mapping_file)
    return {row['URL']: row['Local HTML'] for _, row in mapping.iterrows()}

def copy_image_to_img_folder(image_url, img_folder):
    """Copy image to the 'img' folder and return the new relative path."""
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)  # Create the folder if it doesn't exist

    # Extract the image filename
    image_filename = os.path.basename(image_url)

    # Determine the source and destination paths
    source_path = image_url
    destination_path = os.path.join(img_folder, image_filename)

    # Copy the image to the 'img' folder
    shutil.copy(source_path, destination_path)

    # Return the new relative path for the HTML
    return f"img/{image_filename}"

def generate_product_html(local_html_path, base_path="saved_product_pages/", affiliate_link="", img_folder="img"):
    """Generate the product HTML content for a given local HTML file."""
    try:
        # Read the local HTML file
        with open(local_html_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all images with class "a-dynamic-image"
        dynamic_images = soup.find_all("img", {"class": "a-dynamic-image"})
        if not dynamic_images:
            return "<p>No images found with class 'a-dynamic-image'.</p>"
        
        # Extract all unique image URLs and copy them to 'img' folder
        image_urls = []
        for img in dynamic_images:
            src = img.get("src")
            if src and src not in image_urls:
                src = src[2:]  # Remove "./" prefix if present
                full_src = os.path.join(base_path, src)  # Full path to the image
                new_path = copy_image_to_img_folder(full_src, img_folder)  # Copy image
                image_urls.append(new_path)

        if not image_urls:
            return "<p>No valid image URLs found.</p>"

        # Use the first image as the default large display image
        main_image_url = image_urls[0]

        # Extract price to pay
        price_to_pay = soup.find("span", {"class": "priceToPay"})
        price_to_pay_text = price_to_pay.get_text(strip=True) if price_to_pay else "No price found"

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
            f'<p><strong>Price:</strong> {price_to_pay_text}</p>'
            '</div>'
            '<div class="product-reviews">'
            f'<div class="stars" style="--rating: {stars};" aria-label="Rating of {stars} out of 5"></div>'
            f'<p>{review_count_text}</p>'
            '</div>'
            '<div class="product-amazon-button">'
            f'<a href="{affiliate_link}" target="_blank" style="display: inline-block; text-decoration: none; color: white; background-color: #ff9900; padding: 10px 20px; font-size: 16px; border-radius: 5px; font-weight: bold;">'
            '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" alt="Amazon" style="width: 20px; height: auto; vertical-align: middle; margin-right: 10px;">'
            'Find Best Price on Amazon'
            '</a>'
            '</div>'
            '</div>'
        )
        return html_snippet
    
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"

def fetch_html_content(path):
    """Fetch HTML content from a URL or local file."""
    if path.startswith("http://") or path.startswith("https://"):
        # Fetch content from URL
        response = requests.get(path)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.text
    else:
        # Read content from local file
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

def update_songlyrics_html(article_html_path, mapping_file, base_path="saved_product_pages/"):
    """Update only the content of the 'songLyrics' div in the article HTML."""
    # Load the mapping
    url_to_local_html = load_mapping(mapping_file)
    
    # Fetch the HTML content (from URL or local file)
    article_html = fetch_html_content(article_html_path)
    
    soup = BeautifulSoup(article_html, "html.parser")
    
    # Find the 'songLyrics' div
    song_lyrics_div = soup.find("div", {"class": "songLyrics"})
    if not song_lyrics_div:
        return "No 'songLyrics' div found in the HTML."

    # Update the content within the 'songLyrics' div
    for a_tag in song_lyrics_div.find_all("a", href=True):
        url = a_tag['href']
        if url in url_to_local_html:
            # Get the corresponding local HTML file for the URL
            local_html_path = url_to_local_html[url]
            if os.path.exists(local_html_path):
                # Generate product HTML
                affiliate_link = url  # Use the original affiliate link
                product_html = generate_product_html(local_html_path, base_path, affiliate_link)
                # Replace the anchor tag with the product HTML
                a_tag.replace_with(BeautifulSoup(product_html, "html.parser"))
    
    # Working-Do Not Delete - Save the updated HTML
    # updated_html_path = "updated_article.html"
    # with open(updated_html_path, "w", encoding="utf-8") as file:
    #     file.write(str(soup))

    updated_html_path = "output_snippet.html"
    with open(updated_html_path, "w", encoding="utf-8") as file:
        file.write(song_lyrics_div.decode_contents())  # Write innerHTML only

    return updated_html_path

# Example usage
article_html_path = "https://readernook.com/topics/products/Top-5-Dash-Cameras-for-Cars-in-2025"  # Replace with the path to your article HTML file
img_folder = "img"  # Folder to copy images into
mapping_file = "product_mapping.xlsx"  # Replace with the path to your mapping Excel file
updated_article_path = update_songlyrics_html(article_html_path, mapping_file)

print(f"Updated article saved to: {updated_article_path}")
