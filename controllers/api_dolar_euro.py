import requests
from bs4 import BeautifulSoup
#cambios para poder hacer commit

def valor_dolar_euro():

    imdb_url = 'https://www.bna.com.ar/Cotizador/MonedasHistorico'
    imdb_response = requests.get(imdb_url)
    imdb_soup = BeautifulSoup(imdb_response.text, 'html.parser')

    print(imdb_response.text)

    lista = imdb_soup.find_all('td', {'class': 'dest'})
    i = 0
    dolar = ""
    euro = ""

    for ll in lista:

        l = ll.text
        i += 1

        if i == 1:
            dolar = l
        if i == 5:
            euro = l

    return (dolar, euro)