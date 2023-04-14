"""
programme qui scrape des mangas
"""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup as bs
from variables import cookies, headers

# pylint: disable=W0621
# pylint: disable=W3101
# pylint: disable=R1732
# pylint: disable=W1514
# pylint: disable=W0702
def mkdir(file):
    """
    Crée un répertoire s'il n'existe pas déjà.

    Args:
        file (str): Le nom du répertoire à créer.
    """
    if not os.path.exists(file):
        os.mkdir(file)


def back():
    """
    Reviens au répertoire parent.
    """
    root = os.getcwd().split("/")
    del root[-1]
    os.chdir("/".join(root))


anime = "https://www.scan-vf.net/my-hero-academia/chapitre-1/1".split("/")[3]


def scrape_all_chapters(title_anime):
    """
    Scrapes les liens des images pour tous les chapitres d'un anime donné.

    Args:
        anime (str): Le nom de l'anime.
    """
    title_liens = []
    nbs = range(1, 2101)
    with requests.Session() as session:
        try:
            open("liens " + title_anime + ".txt", "r").readlines()
        except:

            def scrape(number_chapter, title_liens, session):
                """
                Fonction pour le scraping des liens d'images pour un chapitre donné.

                Args:
                    x (int): Le numéro du chapitre.
                    title_liens (list): La liste des liens d'images.
                    session (Session): L'objet de session pour les requêtes HTTP.

                """
                url = "https://www.scan-vf.net/" + title_anime + "/chapitre-" + str(number_chapter)
                response = session.get(url, stream=True, cookies=cookies, headers=headers)
                if response:
                    try:
                        soup = bs(response.text, "html.parser")
                        imgs = soup.find_all("img")
                        for img in imgs:
                            try:
                                title_liens.append(img["data-src"].replace(" ", ""))
                                print(img["data-src"])
                            except:
                                pass
                    except:
                        pass

            with ThreadPoolExecutor(max_workers=100) as execut:
                execut.map(scrape, nbs, [title_liens]*len(nbs), [session]*len(nbs))
            title_liens.sort()
            for i, lien in enumerate(title_liens):
                title_liens[i] = lien + "\n"
            with open("title_liens " + title_anime + ".txt", "w") as file:
                file.writelines(title_liens)

scrape_all_chapters(anime)
print("Fini de scraper les liens")

liens = open("liens " + anime + ".txt", "r").readlines()
for i, lien in enumerate(liens):
    liens[i] = lien.replace("\n", "")

liens = open("liens " + anime + ".txt", "r").readlines()
mkdir(anime)
os.chdir(anime)
files = os.listdir(os.getcwd())


def download(url):
    """
    Télécharge une image à partir de l'URL donnée.

    Args:
        url (str): L'URL de l'image à télécharger.
    """
    url = url.replace("\n", "").replace("scan-vf.co", "scan-vf.net")
    chapitre = url.split("/")[7].replace("-", "_")
    page = url.split("/")[8]
    file_name = chapitre + "," + "page:" + page

    if chapitre not in files or chapitre + ".pdf" not in files:
        print(url)
        with open(file_name, "wb") as handle:
            response = requests.get(url, stream=True, cookies=cookies, headers=headers)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)


with ThreadPoolExecutor(max_workers=100) as execut:
    execut.map(download, liens)
print("Fini de scraper les images")
files = os.listdir(os.getcwd())
for x in files:
    chapitre = x.split(",")[0].replace(":", "_")
    mkdir(chapitre)
    os.system("mv " + x + " " + chapitre + "/" + x)


def merge_images_to_pdf(name):
    """
    convert all images to pdf
    """
    os.system("convert * " + name + ".pdf")


files = os.listdir(os.getcwd())

for x in files:
    print(x)
    chapitre = x
    if not os.path.exists(chapitre + ".pdf"):
        os.chdir(x)
        if not os.path.exists(chapitre + ".pdf"):
            merge_images_to_pdf(chapitre)
        back()
