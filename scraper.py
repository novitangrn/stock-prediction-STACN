import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

def scrape_news():
    base_url = "https://www.cnbcindonesia.com/news/indeks/3"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    
    titles = []
    for article in articles[:5]:  # Ambil 5 berita terbaru
        title_tag = article.find('h2')
        if title_tag:
            titles.append(clean_text(title_tag.text.strip()))
    
    return titles
