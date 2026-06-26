import requests
from bs4 import BeautifulSoup


def _parse_bna_float(value):
    """Convierte formato argentino '1.451,00' a float 1451.0"""
    try:
        cleaned = str(value).strip().replace('.', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


def valor_dolar_euro():
    try:
        imdb_url = 'https://www.bna.com.ar/Cotizador/MonedasHistorico'
        imdb_response = requests.get(imdb_url, timeout=10)
        imdb_soup = BeautifulSoup(imdb_response.text, 'html.parser')

        lista = imdb_soup.find_all('td', {'class': 'dest'})
        i = 0
        dolar = 0.0
        euro = 0.0
        for ll in lista:
            l = ll.text
            i += 1
            if i == 2:
                dolar = _parse_bna_float(l)
            if i == 6:
                euro = _parse_bna_float(l)
        return (dolar, euro)
    except Exception as e:
        print(f"Error al obtener cotización BNA: {e}")
        return (0.0, 0.0)