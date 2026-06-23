from bs4 import BeautifulSoup
import funciones
import pandas as pd
import time

#########################################################################################
########         CONFIGURACIÓN DE ACUERDO AL SITIO ESPECÍFICO     #######################
#########################################################################################

sitio = 'lanacion'

url_prueba = 20

# Los enfoques posibles son 'requests', 'scraper' y 'selenium'. requests funciona por defecto
enfoque = ''

# Colocar True para verificar que obtiene la página de acuerdo al enfoque seleccionado
prueba_url = False

# Prueba JSON. Colocar True para averiguar si captura los datos con JSON
prueba_json = False

# En caso de que alguno de los campos pueda capturarse desde JSON, es mejor.
# Elegir True y especificar los campos que pueden capturarse así
usa_json = False
campos_json = ['titulo', 'fecha', 'copete', 'texto'] # Campos posibles: 'titulo', 'fecha', 'copete', 'texto'

# Colocar True para verificar que captura bien los campos (título, copete, texto, fecha)
prueba_captura = True

d_titulo = {
    'tag' : 'h1',
    'attrs' : {}
}

d_copete = {
    'tag' : ['h2', 'p'],
    'attrs' : {'class': ['com-subhead', 'ln-text', 'nd-apertura-bajada']}
}

contenedor = False
d_texto = {
    'tag' : ['p', 'h2', 'li'],
    'attrs' : {'class' : ['com-paragraph', 'font-primary', 'com-item', 'nd-parrafo-txt', 'nd-card-subtitle']}
}
tags_contenedor = 'p, h2, h3, li, div'
cadenas_para_eliminar = []
tags_a_eliminar = []
clases_a_eliminar = []

d_fecha = {
    'tag': 'time',
    'attrs' : {}
}


########################################################################
######     FINAL DE CONFIGURACIÓN     ##################################
########################################################################



if enfoque == 'scraper':
    import cloudscraper
    scraper = cloudscraper.create_scraper()
elif enfoque == 'selenium':
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    import platform
    from subprocess import getoutput
    options = Options()
    options.set_preference("javascript.enabled", False)
    sistema_actual = platform.system()
    if sistema_actual == "Linux":
        options.binary_location = getoutput("find /snap/firefox -name firefox").split("\n")[-1]
        driver = webdriver.Firefox(
            service=Service(executable_path=getoutput("find /snap/firefox -name geckodriver").split("\n")[-1]),
            options=options)
    elif sistema_actual == "Windows":
        driver = webdriver.Firefox(options=options)
else:
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

df = pd.DataFrame(columns = ['medio', 'titulo', 'fecha', 'copete', 'texto', 'url', 'ranking'])

#direcciones = open('listados/' + sitio + '.txt', 'r')
with open('listados/' + sitio + '.txt', 'r', encoding="utf-8") as archivo:
    direcciones =  [direcciones.strip() for direcciones in archivo]


ranking = 1
for url in direcciones:

    if sitio not in url:
        continue
    if prueba_url or prueba_json or prueba_captura:
       url = direcciones[url_prueba]

    print(ranking, url)
    if enfoque == 'scraper':
        pagina = scraper.get(url)
        pagina.encoding = 'utf-8'
        contenido = pagina.text
    elif enfoque == 'selenium':
        driver.get(url)
        pagina = driver.page_source
        contenido = pagina
    else:
        pagina = requests.get(url, headers=headers)
        contenido = pagina.text
        pagina.encoding = 'utf-8'

    if prueba_url:
        sopa = BeautifulSoup(contenido, 'lxml')
        cuerpo = sopa.find('body')
        print(cuerpo.text)
        break

    if prueba_json:
        print('PRUEBA DE CAMPOS JSON', end='\n\n')
        sopa = BeautifulSoup(contenido, 'lxml')
        data = funciones.obtiene_json(sopa)
        print('TITULO')
        try:
            print(data["headline"])
        except TypeError:
            print('No existe un campo JSON para el título')
        print('\nCOPETE')
        try:
            print(data["description"])
        except TypeError:
            print('No existe un campo JSON para el copete')
        print('\nFECHA')
        try:
            print(data["datePublished"])
        except TypeError:
            print('No existe un campo JSON para la fecha')
        print('\nTEXTO')
        try:
            print(data["articleBody"])
        except TypeError:
            print('No existe un campo JSON para el texto')
        break



    sopa = BeautifulSoup(contenido, 'lxml')
    cuerpo = sopa.find('body')

    for k, t in enumerate(tags_a_eliminar):
        for tag_eliminable in cuerpo.find_all(t, class_=clases_a_eliminar[k]):
            tag_eliminable.decompose()


    if usa_json and 'titulo' in campos_json:
        titulo = funciones.obtiene_json(sopa, 'titulo')
    else:
        titulo1 = cuerpo.find(d_titulo['tag'], d_titulo.get('attrs', {}))
        if titulo1:
            try:
                titulo = titulo1.text
            except AttributeError:
                titulo = ''

    if usa_json and 'texto' in campos_json:
        texto = funciones.obtiene_json(sopa, 'texto')
    else:
        texto = ''
        if contenedor:
            for divisor in cuerpo.find_all(d_texto['tag'], d_texto.get('attrs', {})):
                for parrafo in divisor.select(tags_contenedor):
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

    if usa_json and 'copete' in campos_json:
        copete = funciones.obtiene_json(sopa, 'copete')
    else:
        copete = ''
        copete = cuerpo.find(d_copete['tag'], d_copete.get('attrs', {}))
        if copete:
            try:
                copete = copete.text.strip()
            except AttributeError:
                copete = ''

    if usa_json and 'fecha' in campos_json:
        fecha = funciones.obtiene_json(sopa, 'fecha')
    else:
        fecha = ''
        fecha1 = cuerpo.find(d_fecha['tag'], d_fecha.get('attrs', {}))
        if fecha1:
            try:
                fecha = funciones.formato_fecha(fecha1.text)
            except AttributeError:
                fecha = ''


    if prueba_captura == True:
        print('TITULO:\n', titulo, end='\n\n')
        print('COPETE:\n', copete, end='\n\n')
        print('TEXTO:\n', texto, end='\n\n')
        print('FECHA:\n', fecha)
        break

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

if enfoque == 'selenium':
    driver.quit()

if prueba_url == False and prueba_captura == False and prueba_json == False:
    df.to_pickle('pickles/' + sitio + '.pkl')
    print(df)