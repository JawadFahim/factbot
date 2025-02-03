import requests  # Import the requests library to handle HTTP requests
import time
from bs4 import BeautifulSoup  # Import BeautifulSoup for web scraping

def get_page_access_token(page_id, user_access_token):
    """
    Function to retrieve the Page Access Token using the user access token and page ID.
    """

    # Define the Graph API version and construct the API URL to request the Page Access Token
    version = 'v20.0'
    api_url_token = f'https://graph.facebook.com/{version}/{page_id}?fields=access_token&access_token={user_access_token}'

    try:
        # Make a GET request to the Facebook Graph API to fetch the Page Access Token
        response = requests.get(api_url_token)
        response.raise_for_status()  # Raise an exception if the request returns an HTTP error

        # Parse the response as JSON and return the access token
        data = response.json()
        return data['access_token']
    except requests.exceptions.RequestException as e:
        # Handle any exceptions (e.g., network issues, API errors) and print the error
        print("Error:", e)
        return None  # Return None if the access token retrieval fails

def scrape_paragraphs():
    url = 'https://factrepublic.com/random-facts-generator/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while True:
        response = requests.get(url, headers=headers, proxies={})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            first_paragraph = soup.find('span', class_='td-sml-description')
            if first_paragraph and any(word in first_paragraph.p.text.lower() for word in ['hitler', 'murder','sex','rape','nazi','reich','gun','shoot','shooting','marvel']):
                print("Found 'hitler' or 'murder' in the paragraph, retrying...")
                continue  # Retry the scraping process

            first_source_link = soup.find('a', class_='button source')
            first_image = soup.find('div', class_='td-item').find('img')

            paragraph_text = f"{first_paragraph.p.text.strip()}" if first_paragraph else "No paragraphs found on the page."
            source_link_text = f"Source Link: {first_source_link['href']}" if first_source_link else "No source link found on the page."
            image_src = f"{first_image['src']}" if first_image else None

            return paragraph_text, source_link_text, image_src
        else:
            return None, None, None

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open('temp_image.jpg', 'wb') as file:
            file.write(response.content)
        return 'temp_image.jpg'
    else:
        return None

def upload_image_to_facebook(page_id, page_access_token, image_path):
    url = f'https://graph.facebook.com/v20.0/{page_id}/photos'
    files = {'source': open(image_path, 'rb')}
    payload = {'access_token': page_access_token}

    response = requests.post(url, files=files, data=payload)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Failed to upload image: {response.status_code}")
        print(response.json())
        return None

def post_fb(page_id, page_access_token):
    paragraph_text, source_link_text, image_src = scrape_paragraphs()
    if paragraph_text and image_src:
        image_path = download_image(image_src)
        if image_path:
            url = f'https://graph.facebook.com/v20.0/{page_id}/photos'
            files = {'source': open(image_path, 'rb')}
            message = paragraph_text
            payload = {
                'caption': message,
                'access_token': page_access_token

            }

            response = requests.post(url, files=files, data=payload)
            if response.status_code == 200:
                print("Post successfully published!")
                post_id = response.json()['post_id']

                # Comment the source link under the post
                comment_url = f'https://graph.facebook.com/v20.0/{post_id}/comments'
                comment_payload = {
                    'message': source_link_text,
                    'access_token': page_access_token
                }
                comment_response = requests.post(comment_url, data=comment_payload)
                if comment_response.status_code == 200:
                    print("Comment successfully posted!")
                else:
                    print(f"Failed to post comment: {comment_response.status_code}")
                    print(comment_response.json())
            else:
                print(f"Failed to post: {response.status_code}")
                print(response.json())
        else:
            print("Failed to download image.")
    else:
        print("Failed to scrape content.")
# User access token (replace with your actual user access token)
user_access_token = 'EAAXJ2Cj3qjABOz27DEVP8sFhZCUmZAhccCXMuqplFjMWAWvhdI2Jha8oGhIJSVu6e5ecpI24tlurrxbHihIk3lnQUJZCA5bTipy7bwgRSiaGkdMg0EKORZBnIM3efoCYFHuvKpNhLLINOLUA5zmuIuJLhiZAGKy9GfejgEUOOSicwKGcj8au6PejV'

# Facebook Page ID (replace with your actual page ID)
page_id = '564130533441062'

# Retrieve the Page Access Token using the user access token and page ID
page_access_token = get_page_access_token(page_id, user_access_token)

# If the Page Access Token was successfully retrieved, publish the post
if page_access_token:
    while True:
        post_fb(page_id, page_access_token)
        time.sleep(3600)  # Wait for 5 minutes (300 seconds)
else:
    print("Failed to obtain Page Access Token.")  # Print an error if the token retrieval fails
