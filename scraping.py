from bs4 import BeautifulSoup
import requests
import cloudscraper
import funciones
import pandas as pd
import time

sitio = 'elpais-uy'

d_titulo = {
    'tag' : 'h1',
    'attrs' : {'class': 'Page-headline'}
}

d_copete = {
    'tag' : 'h2',
    'attrs' : {'class': 'Page-subHeadline'}
}

contenedor = True
d_texto = {
    'tag' : 'div',
    'attrs' : {'class' : 'RichTextArticleBody'}
}
cadenas_para_eliminar = []

d_fecha = {
    'tag': 'div',
    'attrs' : {'class': 'Page-datePublished'}
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

df = pd.DataFrame(columns = ['medio', 'titulo', 'fecha', 'copete', 'texto', 'url', 'ranking'])

direcciones = open('listados/' + sitio + '.txt', 'r')
scraper = cloudscraper.create_scraper()
ranking = 1
for l in direcciones:
    url = l[:-1]
    print(ranking, url)
    pagina = requests.get(url, headers=headers)
    #pagina = scraper.get(url)
    contenido = pagina.text
    #print(contenido)
    #exit()

    pagina.encoding = 'utf-8'
    sopa = BeautifulSoup(pagina.text, 'lxml')
    cuerpo = sopa.find('body')

    titulo = ''
    titulo1 = cuerpo.find(d_titulo['tag'], d_titulo.get('attrs', {}))
    if titulo1:
        try:
            titulo = titulo1.text
        except AttributeError:
            titulo = ''

    texto = ''
    if contenedor:
        for divisor in cuerpo.find_all(d_texto['tag'], d_texto.get('attrs', {})):
            for parrafo in divisor.select('p, h2, h3, li'):
                p_limpio = parrafo.text.rstrip()
                if p_limpio[-1:] != '.':
                    texto += p_limpio + '. '
                else:
                    texto += p_limpio + ' '
    else:
        for parrafo in cuerpo.find_all(d_texto['tag'], d_texto.get('attrs', {})):
            p_limpio = parrafo.text.rstrip()
            if p_limpio[-1:] != '.':
                texto += p_limpio + '. '
            else:
                texto += p_limpio + ' '
    for cadena in cadenas_para_eliminar:
        texto = texto.replace(cadena, '')

    copete = ''
    copete = cuerpo.find(d_copete['tag'], d_copete.get('attrs', {}))
    if copete:
        try:
            copete = copete.text.strip()
        except AttributeError:
            copete = ''

    fecha = ''
    fecha1 = cuerpo.find(d_fecha['tag'], d_fecha.get('attrs', {}))
    if fecha1:
        try:
            fecha = funciones.formato_fecha(fecha1.text)
        except AttributeError:
            fecha = ''

    print(titulo)
    print(copete)
    print(texto)
    print(fecha)
    exit()


    df.loc[len(df)] = {
        'medio' : sitio,
        'titulo' : titulo,
        'fecha' : fecha,
        'copete' : copete,
        'texto' : texto,
        'url' : url,
        'ranking' : ranking
    }

    ranking += 1
    time.sleep(1)
    if ranking % 10 == 0:
        df.to_pickle('pickles/' + sitio + '.pkl')

df.to_pickle('pickles/' + sitio + '.pkl')

print(df)