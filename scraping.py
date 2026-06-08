from bs4 import BeautifulSoup
import funciones
import pandas as pd
import time

#########################################################################################
########         CONFIGURACIÓN DE ACUERDO AL SITIO ESPECÍFICO     #######################
#########################################################################################

# Colocar True para verificar que obtiene la página de acuerdo al enfoque seleccionado
prueba_url = False

# Colocar True para verificar que captura bien los campos (título, copete, texto, fecha)
prueba_captura = False

# Los enfoques posibles son 'requests', 'scraper' y 'selenium'. request funciona por defecto
enfoque = ''

sitio = 'elespectador'

d_titulo = {
    'tag' : 'h1',
    'attrs' : {'class' : 'ArticleHeader-Title'}
}

d_copete = {
    'tag' : 'h2',
    'attrs' : {'class': 'ArticleHeader-Hook'}
}

contenedor = True
d_texto = {
    'tag' : 'div',
    'attrs' : {'class' : 'Article-Content'}
}
cadenas_para_eliminar = ['Escucha este artículo.', 'Audio generado con IA de Google.', '0:00. /. 0:00.']

d_fecha = {
    'tag': 'div',
    'attrs' : {'class' : 'ArticleHeader-Date'}
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

direcciones = open('listados/' + sitio + '.txt', 'r')
ranking = 1
for l in direcciones:
    url = l[:-1]
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
        print(contenido)
        break

    sopa = BeautifulSoup(contenido, 'lxml')
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

    if prueba_captura:
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

if prueba_url == False and prueba_captura == False:
    df.to_pickle('pickles/' + sitio + '.pkl')
    print(df)