import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import os
import time  # Add this import

# Seed URLs
seed_urls = [
    "https://www.ajc.com/education/georgia-students-planning-walkouts-to-demand-tougher-gun-safety-measures/DCMI56JLN5GKXKDRQ2EASQBA5U/",
    "https://www.abc15.com/us-news/threats-rise-nationwide-in-the-weeks-after-the-georgia-school-shooting",
    "https://www.wsbtv.com/news/local/barrow-county/im-sorry-mother-alleged-apalachee-school-shooter-received-cryptic-texts-son-that-day/FBL3DV6PZBBJTN4A35BEQPVDD4/",
    "https://www.yahoo.com/news/utah-learn-recent-school-shooting-000000917.html?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAADNElSVWdpyOVhTu7rbYz4t3G1fNdpL0k2xgfQW5mY__UEPpHp0I3f9_TPqdknLiYfxzCO5WLXgY_EFNw_L8ICOS1_gC1dVD2ADBibcl17uZQuh5dYjECi9-Z-tSuC88gz5QXCDSiMsgE9FoaY4fW-tYTnFJlQSzjpAp3kiZvf9Y",
    "https://www.wrdw.com/2024/09/19/georgia-texas-roadhouse-locations-donate-100-profits-apalachee-high-school/",
    "https://www.yahoo.com/news/apalachee-high-school-georgia-sets-181447519.html",
    "https://www.fox5atlanta.com/news/high-school-walkout-gun-laws-georgia-apalachee-shooting",
    "https://www.usatoday.com/story/news/nation/2024/09/13/georgia-school-shooter-father-colin-gray-jail-threats/75202607007/",
    "https://www.ncadvertiser.com/news/article/after-shooting-at-georgia-high-school-students-19772045.php", 
    "https://www.npr.org/2024/09/05/nx-s1-5101683/apalachee-high-school-georgia-shooting-victims",
    "https://www.usatoday.com/story/graphics/2024/09/04/georgia-high-school-shooting-timeline/75074179007/",
    "https://abc7news.com/post/Apalachee-High-School-shooting-911-calls-released-shooter-Colt-Gray-Barrow-County-Georgia/15305351/",
    "https://www.cnn.com/2024/09/13/us/georgia-school-shooting-911-calls/index.html",
    "https://www.wsbtv.com/news/local/barrow-county/apalachee-school-shooting-victim-issues-no-contact-order-colt-gray-colin-gray/LKAXLFF7GVGKNF4EK6EMTSEJJE/",
    "https://www.fox5atlanta.com/news/apalachee-high-school-students-rap-teacher-shooting"
]



from collections import deque
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Define the maximum number of pages to crawl
max_pages = 100
visited_urls = set()
queue = deque([(url, 1) for url in seed_urls])  # (url, score)

# Ensure output directory exists
os.makedirs("pages", exist_ok=True)

# Function to check if a page is relevant
def is_relevant(text):
    keywords = ["Apalachee High School", "mass shooting", "Georgia", "shooting"]
    return any(keyword.lower() in text.lower() for keyword in keywords)

# Function to extract links from a page
def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for anchor in soup.find_all('a', href=True):
        full_url = urljoin(base_url, anchor['href'])
        links.append((full_url, anchor.text))
    return links

# Main crawling loop
while queue and len(visited_urls) < max_pages:
    url, score = queue.popleft()
    if url in visited_urls:
        continue
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        
        if is_relevant(html):
            visited_urls.add(url)
            print(f"Visited: {url}")  # Track progress
            with open(f"pages/page_{len(visited_urls)}.html", "w", encoding='utf-8') as f:
                f.write(html)

            links = extract_links(html, url)
            for link, anchor_text in links:
                if link not in visited_urls and link not in [u[0] for u in queue]:
                    # Update the keywords to focus on Apalachee shooting
                    link_score = sum(1 for keyword in ["Apalachee", "shooting"] if keyword.lower() in anchor_text.lower())
                    queue.append((link, link_score))

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")

    time.sleep(1)  # Rate limiting

# Save the list of visited URLs
with open("visited_urls.txt", "w") as f:
    for v_url in visited_urls:
        f.write(v_url + "\n")
