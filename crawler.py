from flask import Flask, request, render_template
from collections import deque
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

app = Flask(__name__)

# Ensure output directory exists
os.makedirs("pages", exist_ok=True)

# Function to check if a page is relevant
def is_relevant(text, keywords):
    return any(keyword.lower() in text.lower() for keyword in keywords)

# Function to extract links from a page
def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for anchor in soup.find_all('a', href=True):
        full_url = urljoin(base_url, anchor['href'])
        links.append((full_url, anchor.text))
    return links

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get user inputs
        seed_urls = request.form.get('seed_urls').splitlines()
        keywords = request.form.get('keywords').split(',')
        max_pages = int(request.form.get('max_pages', 100))
        
        visited_urls = set()
        queue = deque([(url, 1) for url in seed_urls])  # (url, score)

        # Crawling process
        while queue and len(visited_urls) < max_pages:
            url, score = queue.popleft()
            if url in visited_urls:
                continue
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                html = response.text
                
                if is_relevant(html, keywords):
                    visited_urls.add(url)
                    with open(f"pages/page_{len(visited_urls)}.html", "w", encoding='utf-8') as f:
                        f.write(html)

                    links = extract_links(html, url)
                    for link, anchor_text in links:
                        if link not in visited_urls and link not in [u[0] for u in queue]:
                            link_score = sum(1 for keyword in keywords if keyword.lower() in anchor_text.lower())
                            queue.append((link, link_score))
            except requests.RequestException as e:
                print(f"Could not fetch {url}: {e}")
            
            time.sleep(1)
        
        with open("visited_urls.txt", "w") as f:
            for v_url in visited_urls:
                f.write(v_url + "\n")
        
        return render_template('results.html', visited_urls=visited_urls)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

