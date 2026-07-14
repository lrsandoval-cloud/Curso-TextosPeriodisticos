import pandas as pd


def formato_fecha(fecha):
    import re
    from datetime import datetime

    meses = {
        'ene': 1, 'enero': 1,
        'feb': 2, 'febrero': 2,
        'mar': 3, 'marzo': 3,
        'abr': 4, 'abril': 4,
        'may': 5, 'mayo': 5,
        'jun': 6, 'junio': 6,
        'jul': 7, 'julio': 7,
        'ago': 8, 'agosto': 8,
        'sep': 9, 'sept': 9, 'septiembre': 9,
        'oct': 10, 'octubre': 10,
        'nov': 11, 'noviembre': 11,
        'dic': 12, 'diciembre': 12
    }
    fecha = fecha.strip()
    #def parsear_fecha(fecha_str):
    # Buscar algo tipo "23 de octubre de 2024"
    #patron = r'(\d{1,2})\s*(?:de\s*)?([a-zñ]+)\s*(?:de\s*)?(\d{4})'
    patron = r'(\d{1,2})\s*(?:de\s*)?([a-zñ]+)\s*(?:de\s*)?(\d{4})'
    match = re.search(patron, fecha.lower())
    if match:
        dia, mes_texto, anio = match.groups()
        mes = meses.get(mes_texto)
        if mes:
            return f"{anio}-{mes}-{int(dia):02d}"

    try:
        fecha = fecha.replace(',', '')
        fecha_formateada = datetime.strptime(fecha, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d")
    except ValueError:
        fecha_formateada = '0000-00-00'

    if fecha_formateada == '0000-00-00':
        try:
            fecha = fecha[:16].replace('.', '/')
            fecha_formateada = datetime.strptime(fecha[:16], "%d/%m/%Y %H:%M").strftime("%Y-%m-%d")
        except ValueError:
            fecha_formateada = '0000-00-00'

    return fecha_formateada


def obtener_stop_words(idioma='es'):
    if idioma == 'es':
        with open('spanish.txt') as f:
            stop_words = f.read().splitlines()
    elif idioma == 'en':
        # import nltk
        from nltk.corpus import stopwords
        # nltk.download('stopwords')
        stop_words = list(stopwords.words('english'))
    with open('mas_stopwords.txt') as f:
        agregar = f.read().splitlines()
    stop_words = stop_words + agregar
    return stop_words


def obtener_dic_palabras(base):
    rotulos = list(base['medio'].unique())
    palabras = {}

    for rotulo in rotulos:
        segmento = base.query("medio == '" + rotulo + "'")
        texto = " ".join(segmento['lemas'].dropna())
        palabras[rotulo] = texto

    return palabras


def tipo_producto(producto):
    if producto == 'Huevos':
        forma = 'docena'
    else:
        forma = 'kg'
    return forma




def obtiene_json(sopa, campo=False):

    import json

    for script in sopa.find_all("script", type="application/ld+json"):

        try:
            data = json.loads(script.string)

            if not isinstance(data, dict):
                continue

            tipo = data.get("@type")

            if (
                tipo == "NewsArticle"
                or tipo == "Article"
                or tipo == "ReportageNewsArticle"
                or (
                    isinstance(tipo, list)
                    and "NewsArticle" in tipo
                )
            ):
                if campo:
                    campos = {'titulo' : 'headline', 'copete' : "description", 'fecha' : 'datePublished', 'texto' : 'articleBody'}
                    if campo == 'fecha':
                        dato = data['datePublished'][:10]
                    else:
                        dato = data[campos[campo]]
                    return dato
                else:
                    return data

        except Exception:
            continue

    return None