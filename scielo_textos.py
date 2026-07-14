import pickle
import pandas as pd
from bs4 import BeautifulSoup
import requests

keyword = 'redes sociales'

with open('pickles/scielo_uy_keywords.pkl', 'rb') as f:
    palabras = pickle.load(f)

palabras_ordenadas = dict(
    sorted(palabras.items(), key=lambda item: item[1], reverse=True)[:50]
)

#print(palabras_ordenadas)
#exit()

base = pd.read_pickle('pickles/scielo_uy.pkl')

articulos = []
for i, row in base.iterrows():
    keyw = row['keywords'].lower().split(', ')
    if keyword in keyw:
        articulos.append(row['URL'])

headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

for url in articulos:
    pagina = requests.get(url, headers=headers)
    contenido = pagina.text
    pagina.encoding = 'utf-8'
    sopa = BeautifulSoup(contenido, 'lxml')
    for bloque in sopa.find_all('div', {'class' : 'box'}):
        for l in bloque.find_all('a'):
            link = l.get('href')
            #print(link)
            try:
                if '.pdf' in link and ('Espa' in l.text or 'Spa' in l.text):
                    nombre_archivo = link.split('/')[-1]
                    link = 'http://www.scielo.edu.uy' + link
                    archivo = requests.get(link, headers=headers)
                    with open('papers/' + nombre_archivo, 'wb') as file:
                        file.write(archivo.content)
                    print(link)
            except TypeError:
                continue

