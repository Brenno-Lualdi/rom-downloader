import os
import urllib

import requests
from bs4 import BeautifulSoup


def complemento():
    return 'super-nintendo'

def cria_pasta():
    dirName = 'H:/ROMs/' + complemento() + '/'
    try:
        os.makedirs(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

def download_url(host, resource, filename, save_path='H:/ROMs/complemento/', chunk_size=128):
    save_path = save_path.replace('complemento', complemento())
    url = host + urllib.parse.quote(resource, safe='')
    r = requests.get(url, headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Host': 'static.downloadroms.io',
        'Referer': 'https://www.romsgames.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }, stream=True)
    if '<!DOCTYPE HTML>' in r.text:
        raise Exception('Arquivo compactado invalido no site')
    if not r.ok:
        raise Exception('Erro no request de download')
    with open(save_path + filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


if __name__ == '__main__':
    cria_pasta()
    url_default = 'https://www.romsgames.net/roms/nomedoconsole/?letter=all&page=numerodapagina&sort=alphabetical'
    url_default = url_default.replace('nomedoconsole', complemento())
    pag1 = requests.get(url_default.replace('numerodapagina', '1'))
    soup = BeautifulSoup(pag1.text, 'html.parser')
    try:
        numPags = len(soup.select('#mainContainer > div:nth-child(18) > div > ul > li:nth-child(n)'))-1
        if numPags < 1:
            numPags = 2
    except Exception as e:
        numPags = 2
    range_paginas = range(1, numPags)

    for x in range_paginas:
        print(f'Acessando pagina {x}')
        url_atual = url_default.replace('numerodapagina', str(x))
        pag_atual = requests.get(url_atual)
        soup = BeautifulSoup(pag_atual.text, 'html.parser')
        lista_link_jogos = soup.select('#mainContainer > div:nth-child(n+4) > div:nth-child(n) > a')

        for link in lista_link_jogos:
            link_jogo = f'https://www.romsgames.net{link["href"]}'
            print(f'Acessando {link_jogo}')
            pagina_jogo = requests.get(link_jogo)
            soup = BeautifulSoup(pagina_jogo.text, 'html.parser')
            try:
                mediaId = soup.select('#download-form > button')[0]["dlid"]
            except Exception as ex4:
                print('mediaID nao encontrado.')
                continue
            click_download = requests.post('https://www.romsgames.net/download' + link["href"], data={"mediaId": mediaId})
            if 'Could not get your download ready' in click_download.text:
                print(f'Impossível baixar {link_jogo}')
                continue
            soup = BeautifulSoup(click_download.text, 'html.parser')
            try:
                link_redirect01 = soup.select('body > form')[0]['action']
            except Exception as ex3:
                continue
            val_redirect01 = soup.select('body > form > input')[0]['value']
            link_download = link_redirect01 + '?attach='
            nome_arquivo = val_redirect01
            try:
                nome_arquivo = val_redirect01.replace('%20', '-')
            except Exception as ex:
                pass

            try:
                download_url(link_download, val_redirect01, nome_arquivo)
                print('Download ok!')
            except Exception as ex2:
                print(f'Impossivel de baixar o {link_jogo}, Exception: {ex2}')

    print('Fim.')

