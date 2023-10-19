import os
import requests
import threading
import time
from bs4 import BeautifulSoup

############################################################################################################

# KHINSIDER ALBUM DOWNLOADER, PLEASE USE SPARINGLY!!

#~~~ Configure: ~~~#
# URL of album to download
url = "https://downloads.khinsider.com/game-soundtracks/album/genshin-impact-forest-of-jnana-and-vidya-original-game-soundtrack-2022"
# Songs to download based on order listed, leave empty to download all
which_songs = []
# Will download as MP3 if False, or as FLAC if True (Make sure the album actually has FLAC format available)
flac = False
# Browser header
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"}

############################################################################################################


response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
links = [element.find("a", href=True)["href"] for element in soup.find_all("td", class_ = "playlistDownloadSong")]

for num in which_songs:
    if num < 1 or num > len(links):
        raise Exception("Requested to download a song that doesn't exist (check which_songs!)")

album_name = soup.find("h2").get_text()
print(f"Downloading album: {album_name}")

def parse_and_download(link: str):
    download_page = requests.get(f"https://downloads.khinsider.com{link}")
    if download_page.status_code == 200:
        download_page_soup = BeautifulSoup(download_page.content, "html.parser")
        title = download_page_soup.find("div", id="pageContent").findAll("p", {"align": "left"})[1].findAll("b")[1].get_text()
        print(f"{title}.{'mp3' if flac == False else 'flac'}")

        if flac == False:
            audio_file = download_page_soup.find("audio")["src"]
        else:
            audio_file = download_page_soup.find("div", id="pageContent").find_all("p")[4].find("a", href=True)["href"]

        with open(os.path.join(album_name, f"{title}.{'mp3' if flac == False else 'flac'}"), "wb") as file:
            file.write(requests.get(audio_file).content)

if not os.path.exists(album_name):
    os.makedirs(album_name)
if not os.path.exists(album_name):
    print("Error creating album directory")
else:
    if len(which_songs) == 0:
        threads = [threading.Thread(target=parse_and_download, args=[link]) for link in links]
    else:
        threads = [threading.Thread(target=parse_and_download, args=[link]) for index, link in enumerate(links) if index + 1 in which_songs]
    
    start_time = time.time()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    print(f"\nDownloaded {len(threads)} song(s) in {round(elapsed_time, 2)} seconds")
