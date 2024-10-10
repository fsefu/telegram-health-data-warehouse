import os
import time
import requests
from bs4 import BeautifulSoup
import re  # For extracting numerical parts from the post IDs
import csv  # For saving data to CSV


class TelegramScraper:
    def __init__(self, telegram_username):
        # Initialize the class with a single Telegram username
        self.telegram_username = telegram_username

    def make_request_with_retries(self, url, retries=3, delay=3):
        """
        Makes a GET request to the specified URL with retries on failure.

        Args:
            url (str): The URL to request.
            retries (int): Number of retries before giving up.
            delay (int): Delay in seconds between retries.

        Returns:
            Response object or None if all retries fail.
        """
        for attempt in range(retries):
            try:
                response = requests.get(url)
                # Check if the request was successful
                if response.status_code == 200:
                    return response
                else:
                    print(
                        f"Attempt {attempt + 1}: Received status code {response.status_code}."
                    )
            except requests.ConnectionError as e:
                print(f"Attempt {attempt + 1}: Connection error: {e}")

            # Wait before the next attempt
            time.sleep(delay)

        print(f"Failed to retrieve data from {url} after {retries} attempts.")
        return None

    def scrape_data_posts(self):
        all_posts = []

        username = self.telegram_username
        url = f"https://t.me/s/{username}"
        response = self.make_request_with_retries(url)
        # requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract all elements with 'data-post' attribute
            post_elements = soup.find_all("div", {"class": "tgme_widget_message"})
            # channel_name=soup.find("div", {"class": "tgme_widget_message"})
            # Find the element by class name
            header_title = soup.find(class_="tgme_header_title")
            channel_name = None
            # Extract the text
            if header_title:
                text = header_title.get_text(strip=True)
                print(text)
                channel_name = text
            else:
                print("Element not found.")

            # Collect data-post values
            post_ids = [
                post.get("data-post") for post in post_elements if post.get("data-post")
            ]

            # Store the results for the current username
            all_posts = {"post_ids": post_ids, "channel_name": channel_name}
        else:
            print(f"Failed to retrieve data from {url}")

        return all_posts

    def get_largest_post_number_and_channel_name(self):
        # Scrape the posts
        posts = self.scrape_data_posts()

        if not posts:
            return None

        # Extract the numerical part of the post IDs and convert to integers
        post_numbers = [
            int(re.search(r"/(\d+)$", post).group(1)) for post in posts.get("post_ids")
        ]

        # Find and return the largest post number
        return {"largest": max(post_numbers), "channel_name": posts.get("channel_name")}

    def download_image(self, img_name, image_url, index, folder="../../data/tg_image"):
        # Create folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Set the image filename (include index in the name)
        image_name = f"{img_name}_{index}.jpg"
        image_path = os.path.join(folder, image_name)

        # Download and save the image
        response = self.make_request_with_retries(image_url)
        # requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

        # Return the path where the image is stored
        return image_path

    def scrape_post_content(self, username, post_id):
        data_post = f"{username}/{post_id}"
        print("data_post: ", data_post)
        """
        Scrapes a Telegram post based on the provided user/post_id.

        Args:
            html_content (str): The HTML content of the page to scrape.
            user_post_id (str): The user and post id to match (e.g., 'yetenaweg/1175').

        Returns:
            dict: A dictionary containing post details if matched, otherwise None.
        """
        url = f"https://t.me/s/{username}/{post_id}"
        response = self.make_request_with_retries(url)
        # requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup)
        # Find the post container with the matching data-post attribute
        post_container = soup.find(
            "div", class_="tgme_widget_message", attrs={"data-post": data_post}
        )

        if post_container:

            # Extract the message text from the 'tgme_widget_message_text' div
            # message_text_div = soup.find("div", class_="tgme_widget_message_text")

            # Initialize an empty dictionary to store the scraped data
            scraped_data = {}
            # Find the div with class 'tgme_widget_message_text js-message_text before_footer'
            message_div = post_container.find("div", class_="tgme_widget_message_text")
            if message_div:

                # Remove emoji tags
                for emoji in message_div.find_all("i", class_="emoji"):
                    emoji.decompose()

                # Extract the cleaned text
                message_text = message_div.get_text(strip=True)
                scraped_data["message_text"] = message_text
            else:
                print("no message div")
            # Extract view count
            views_span = post_container.find("span", class_="tgme_widget_message_views")
            if views_span:
                scraped_data["views"] = views_span.get_text(strip=True)

            # Extract author and timestamp
            message_meta = post_container.find(
                "span", class_="tgme_widget_message_meta"
            )
            if message_meta:
                author = message_meta.find(
                    "span", class_="tgme_widget_message_from_author"
                )
                timestamp = message_meta.find("time")

                if author:
                    scraped_data["author"] = author.get_text(strip=True)

                if timestamp:
                    scraped_data["timestamp"] = timestamp.get("datetime")

            # Extract image URL if present
            # Extract image URLs if present
            image_wraps = post_container.find_all(
                "a", class_="tgme_widget_message_photo_wrap"
            )

            # Initialize a list to store image URLs
            image_urls = []
            image_paths = []

            # Loop through all found image wraps and extract the URLs
            # for image_wrap in image_wraps:
            for index, image_wrap in enumerate(image_wraps):

                if "background-image" in image_wrap.attrs.get("style", ""):
                    image_url = re.search(
                        r"url\(\'(.*?)\'\)", image_wrap["style"]
                    ).group(1)
                    image_urls.append(image_url)
                    # image_path = download_image(image_url, index)
                    image_path = self.download_image(
                        f"{username}_{post_id}", image_url, index
                    )

                    image_paths.append(image_path)

            if image_urls:
                scraped_data["image_urls"] = image_urls
            if image_paths:
                scraped_data["image_paths"] = image_paths
            return scraped_data

        else:
            print("no id")
            # Return None if no matching post was found
            return None

    def save_to_csv(self, data, file_name="../../data/telegram_data.csv"):
        """
        Save scraped data to a CSV file.
        Args:
            data (dict): The scraped post data.
            file_name (str): The name of the CSV file (default is 'telegram_data.csv').
        """
        # Define the CSV header
        csv_columns = [
            "post_id",
            "channel_name",
            "channel_username",
            "author",
            "message_text",
            "views",
            "timestamp",
            "image_urls",
            "image_paths",
            "source",
        ]

        # Check if the file exists
        file_exists = os.path.isfile(file_name)

        # Open the CSV file in append mode
        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=csv_columns)

            # If the file does not exist, write the header
            if not file_exists:
                writer.writeheader()

            # Write the row of data
            writer.writerow(data)


# Example usage:
if __name__ == "__main__":
    # Array of Telegram usernames
    telegram_usernames = ["EAHCI", "lobelia4cosmetics", "yetenaweg", "DoctorsET"]
    # telegram_usernames = ["EAHCI"]
    total_post_count = 0
    for username in telegram_usernames:
        scraper = TelegramScraper(username)  # Pass each username individually
        post_info = scraper.get_largest_post_number_and_channel_name()

        # print(f"Largest post for {username}: {largest_post}")
        if post_info:
            for i in range(1, post_info.get("largest")):
                result = scraper.scrape_post_content(username, i)
                print("result: ", result)
                if result:
                    result["post_id"] = f"{username}_{i}"
                    result["channel_name"] = f'{post_info.get("channel_name")}'
                    result["channel_username"] = f"{username}"
                    result["source"] = "Telegram"
                    if result:
                        scraper.save_to_csv(result)
                        total_post_count += 1
                        print("total: ", total_post_count)
