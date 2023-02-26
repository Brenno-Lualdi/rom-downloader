import os
import urllib

import requests
from bs4 import BeautifulSoup


def save_to():
    return f'H:/ROMs/{console()}/'


def console():
    return 'tandy-color-computer'


def create_folder():
    dirName = save_to()
    try:
        os.makedirs(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists")


def download_url(url, filename, chunk_size=128):
    r = requests.get(url, headers=download_headers(), stream=True)
    if '<!DOCTYPE HTML>' in r.text:
        raise Exception('Arquivo compactado invalido no site')
    if not r.ok:
        raise Exception('Erro no request de download')
    with open(save_to() + filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def download_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': 'static.romsgames.net',
        'Referer': 'https://www.romsgames.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/110.0.0.0 Safari/537.36 '
    }


def get_number_of_pages(soup):
    try:
        number_of_pages = len(soup.find_all('ul', class_='pagination')[-1].select('li')) - 1
        if number_of_pages < 1:  # todo que porra é essa?
            number_of_pages = 2
    except Exception as e:
        print(e)
        number_of_pages = 2
    return number_of_pages


def get_soup_from_url(url: str):
    pag1 = requests.get(url)
    return BeautifulSoup(pag1.text, 'html.parser')


def download_game_from_link(link: dict):
    link_jogo = f'https://www.romsgames.net{link["href"]}'
    print(f'Acessando {link_jogo}')
    soup = get_soup_from_url(link_jogo)
    try:
        mediaId = soup.select('#download-form > button')[0]["dlid"]
    except Exception as ex4:
        print('mediaID nao encontrado.')
        return None
    click_download = requests.post('https://www.romsgames.net/download' + link["href"], data={"mediaId": mediaId})
    if 'Could not get your download ready' in click_download.text:
        print(f'Impossível baixar {link_jogo}')
        return None
    soup = BeautifulSoup(click_download.text, 'html.parser')
    try:
        link_redirect01 = soup.select('div > form')[0]['action']
    except Exception as ex3:
        return None
    val_redirect01 = soup.select('div > form > input')[0]['value']
    link_download = f'{link_redirect01}?attach={val_redirect01}'
    nome_arquivo = val_redirect01
    try:
        nome_arquivo = val_redirect01.replace('%20', '-')
    except Exception as ex:
        pass
    try:
        download_url(link_download, nome_arquivo)
        print('Download ok!')
    except Exception as ex2:
        print(f'Impossivel de baixar o {link_jogo}, Exception: {ex2}')


def run_trough_pages(number_of_page: int):
    print(f'Acessando pagina {number_of_page}')
    url_atual = f'https://www.romsgames.net/roms/{console()}/?letter=all&page={number_of_page}&sort=alphabetical'
    soup = get_soup_from_url(url_atual)
    lista_link_jogos = soup.select('#main-container > ul:nth-child(n) > li:nth-child(n) > a')
    for link in lista_link_jogos:
        download_game_from_link(link)


if __name__ == '__main__':
    create_folder()
    first_url = f'https://www.romsgames.net/roms/{console()}/?letter=all&page=1&sort=alphabetical'
    range_paginas = range(1, get_number_of_pages(get_soup_from_url(first_url)))

    for page_number in range_paginas:
        run_trough_pages(page_number)
    print('Fim.')
