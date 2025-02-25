import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

def scrape_news(target_date, max_pages=1):
    if isinstance(target_date, str):  # Jika menerima string, ubah ke datetime
        target_date = datetime.strptime(target_date, "%d/%m/%Y").date()
    
    formatted_date = target_date.strftime("%d/%m/%Y")  # Format tanggal yang benar

    base_url = "https://www.cnbcindonesia.com/news/indeks/3"
    all_data = []

    for i in range(1, max_pages + 1):
        url = f"{base_url}?date={formatted_date}&tipe=artikel"
        titles, _, _ = scrape_page(url)

        if titles:
            all_data.extend(titles)

    return all_data if all_data else ["Tidak ada berita ditemukan"]
