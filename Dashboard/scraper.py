import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def clean_text(text):
    """Membersihkan karakter tak terlihat dari teks."""
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

def scrape_page(url):
    """Mengambil artikel dari halaman utama CNBC Indonesia."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return [], [], []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')

    titles, links, dates = [], [], []
    
    for article in articles:
        a_tag = article.find('a')
        title_tag = article.find('h2')
        date_tag = article.find('span', class_='date')

        if a_tag and title_tag:
            link = a_tag['href']
            title = title_tag.text.strip()
            date = date_tag.text.strip() if date_tag else 'No date found'

            titles.append(clean_text(title))
            links.append(link)
            dates.append(clean_text(date))

    return titles, links, dates

def scrape_news(target_date, max_pages=1, max_news=5):
    """Mengambil berita dari CNBC Indonesia berdasarkan tanggal."""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%d/%m/%Y").date()

    base_url = "https://www.cnbcindonesia.com/news/indeks/3"
    all_data = []

    for i in range(1, max_pages + 1):
        url = f"{base_url}?page={i}"
        titles, _, _ = scrape_page(url)

        if titles:
            all_data.extend(titles)

        if len(all_data) >= max_news:
            break

    return all_data[:max_news] if all_data else ["Tidak ada berita ditemukan"]

# Contoh pemanggilan
berita = scrape_news("01/03/2025")
print(berita)
