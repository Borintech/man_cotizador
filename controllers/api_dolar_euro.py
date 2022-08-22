import requests
from bs4 import BeautifulSoup

def valor_dolar_euro():

    imdb_url = 'https://www.bna.com.ar/Cotizador/MonedasHistorico'
    imdb_response = requests.get(imdb_url)
    imdb_soup = BeautifulSoup(imdb_response.text, 'html.parser')

    #print(imdb_response.text)

    lista = imdb_soup.find_all('td', {'class': 'dest'})
    i = 0
    dolar = ""
    euro = ""
    print(lista)
    for ll in lista:

        l = ll.text
        i += 1

        if i == 2:
            dolar = l
        if i == 6:
            euro = l
    print(euro)
    print(dolar)
    return (dolar, euro)