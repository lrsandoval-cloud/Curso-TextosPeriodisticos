clusters = 9    # Indicar el número de grupos que se quiere establecer
titulares = 5   # Indicar la cantidad de notas que me indicará como emblemáticas del clúster
idioma = 'es' # Opciones: es (español), en (inglés)

import pandas as pd
base = pd.read_pickle('pickles/scielo_uy.pkl').query("Idioma == 'es'")
base.reset_index(drop=True, inplace=True)


from funciones import obtener_stop_words
stop_words = obtener_stop_words(idioma)

data = base['lemas'].tolist()

from sklearn.feature_extraction.text import TfidfVectorizer

# Creo el objeto vectorizer que va a medir tf-idf considerando las palabras
# que estén en al menos 5 artículos (min_df=5) y en no más de la mitad del
# corpus (max_df=0.5) y que no estén entre las incluidas en stop_words
vectorizer = TfidfVectorizer(
    max_df=0.5,
    min_df=5,
    stop_words=stop_words,
)
X_tfidf = vectorizer.fit_transform(data) # matriz vectorizada con Tf-idf


from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans

# make_pipeline sirve para hacer varias cosas al mismo tiempo (aplica la siguiente función
# al resultado de la anterior). En este caso reduce las dimensiones de la matriz a 100 columnas
# y normaliza la escala para que todos los vectores sean comparables (si no se hace esto puede
# influir la diferente extensión de las notas)
lsa = make_pipeline(TruncatedSVD(n_components=100, random_state=42), Normalizer(copy=False))
X_lsa = lsa.fit_transform(X_tfidf)

# Se crea el objeto kmeans, que tiene como parámetros la cantidad de clústers, el máximo de
# iteraciones, cuántas veces prueba antes de elegir los centroides (n_init), quedándose
# con la mejor solución (la que tenga la menor suma de distancias internas o "inercia").
# Asignar un valor a random_state permite fijar los resultados ya que si no se lo indica,
# cada vez que se corre el script el resultado es distinto. 42 es un valor aleatorio,
# un guiño a "Guía del autoestopista galáctico" de Douglas Adams, donde 42 es
# "la respuesta a la pregunta fundamental sobre la vida, el universo y todo".
kmeans = KMeans(
    n_clusters=clusters,
    max_iter=300,
    n_init=10,
    random_state=42,
	)

# Y a continuación se "llena" el objeto kmeans con la matriz reducida, con lo que asigna
# cada artículo a uno de los clústers
kmeans.fit(X_lsa)

# cluster_centers_ es una propiedad del objeto kmeans que contiene el peso de cada término
# respecto a cada uno de los centroides (valor más alto es más peso, o sea más importante o
# significativo para ese clúster), pero al construir el modelo con el espacio reducido, va a
# contener solo esas 100 distancias. Con el método inverse_transform del modelo lsa
# (que tiene dos pasos indicados con el índice: [0] para TruncatedSVD, [1] para Normalizer)
# recupero todos los términos
centroides = lsa[0].inverse_transform(kmeans.cluster_centers_)


# En esta línea argsort obtiene las posiciones (empezando por 0) de cada valor en la matriz,
# ordenados de menor a mayor. El parámetro "[:, ::-1]" es indexación de NumPy e indica que
# considere todas las filas (:) pero que las de vuelta, o sea de mayor a menor (::-1)
centroides_ordenados = centroides.argsort()[:, ::-1]


# Recupero las palabras en sí como un array unidimensional en el cual el índice es
# el mismo que en centroides y centroides_ordenados. O sea:
# a) i = centroides_ordenados[1, 9] contiene el índice del décimo término en importancia
#   (porque empieza en 0) para el clúster 1.
# b) terminos[i] tiene la palabra que corresponde a ese índice
# b) centroides[1, i] contiene el peso del término en el clúster 1
terminos = vectorizer.get_feature_names_out()


# Armo una lista de listas en la cual para cada clúster va a tener una lista
# con las 20 palabras más significativas (o sea que tengan más peso)
keywords = []
for c in range(clusters):
    palabras = []
    for i in centroides_ordenados[c, :20]:
        palabras.append(terminos[i])
    keywords.append(palabras)


from sklearn.metrics import pairwise_distances
cercanos = pairwise_distances(centroides, X_tfidf)
cercanos_lista = cercanos.tolist()

# Obtengo una lista donde los índices son los de los artículos y los valores el
# clúster asignado a cada una de las notas
ks = kmeans.labels_.tolist()
base['cluster'] = ks
base['distancia'] = 0.0
for i, row in base.iterrows():
    # Recorro base y asigno a la celda que corresponde a la columna 'distancia'
    # el valor que obtengo de mirar en la fila a qué clúster corresponde la nota
    # (base.loc[i, 'cluster']) y cuál es el índice de la nota (i)
    base.loc[i, 'distancia'] = cercanos_lista[base.loc[i, 'cluster']][i]


# Recorro los clústers para obtener los títulos y las urls de los más representativos
titulos = []
urls = []
for c in range(clusters):
    # Limito el df a los que corresponden al clúster, los ordeno de acuerdo a la
    # distancia (de menor a mayor) y limito la consulta a la cantidad indicada en "titulares"
    articulos_k = base.query('cluster ==' + str(c)).sort_values('distancia')[:titulares].copy()
    titu = []
    url = []
    # Recorro ese df reducido y obtengo títulos y urls que incluyo en listas
    for i, row in articulos_k.iterrows():
        titu.append(row['Título'])
        url.append(row['URL'])
    titulos.append(titu)
    urls.append(url)

# Guardo la base, que ahora va a tener dos columnas más: 'cluster' y 'distancia'
#pd.to_pickle(base, 'pickles/scielo_uy_esp.pkl')


# El último fragmento de código genera un archivo HTML con las palabras clave y los títulos
# (y enlaces) de los artículos emblemáticos de cada clúster
texto = '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n'

for c in range(clusters):
    texto += '<h3>CLUSTER ' + str(c) + '</h3>\n'
    texto += '<p>'
    for kl in keywords[c]:
        texto += kl + ' '
    texto += '</p>\n<ul>'
    for ind, tit in enumerate(titulos[c]):
        texto += '<li><a href="' + urls[c][ind] + '">' + tit + '</a></li>\n'
    texto += '</ul>\n'

texto +"</body>\n</html>"

listado = open('scielo_clusters.html', 'w')
listado.write(texto)
listado.close()

