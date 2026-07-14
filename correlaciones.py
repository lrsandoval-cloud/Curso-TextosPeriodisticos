# Indicar los medios a comparar en el gráfico de correlación de palabras
# y en el top de palabras difereciadoras
medios = [pickles = ['lavanguardia', 'lanacion']]
idioma = 'es' # Opciones: es (español), en (inglés)

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from funciones import obtener_dic_palabras
from funciones import obtener_stop_words

base = pd.read_pickle('pickles/base.pkl')
rotulos = list(base['medio'].unique())

palabras = obtener_dic_palabras(base)
stop_words = obtener_stop_words('en')

vectorizer = CountVectorizer(stop_words=stop_words)
corpus = list(palabras.values())
X = vectorizer.fit_transform(corpus)
frecuencias = pd.DataFrame(X.toarray(), index=rotulos, columns=vectorizer.get_feature_names_out())

frecuencias = frecuencias.transpose()


from scipy.spatial.distance import cosine

def similitud_coseno(a,b):
    distancia = cosine(a,b)
    return 1-distancia

correlaciones = frecuencias.corr(method=similitud_coseno)
print('---------------CORRELACIÓN DE PALABRAS')
print(correlaciones)
print()




import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

f, ax = plt.subplots(figsize=(6, 4))
frecuencias = frecuencias.dropna()

index_medio = []
index_medio.append(frecuencias.columns.get_loc(medios[0]))
index_medio.append(frecuencias.columns.get_loc(medios[1]))

sns.regplot(
    x  = np.log(frecuencias[medios[0]] + 1), # El +1 es para evitar errores de cálculo de logaritmo por cero
    y  = np.log(frecuencias[medios[1]] + 1),
    scatter_kws =  {'alpha': 0.05}, # Esto le da transparencia a los puntos
    ax = ax # indica de dónde va a tomar las etiquetas de los puntos (palabras)
)

for i in np.random.choice(range(frecuencias.shape[0]), 100): # genera 100 números aleatorios entre 0 y la cantidad de filas del data frame
    ax.annotate( # para cada uno de esos 100 puntos va a generar una etiqueta
        text=frecuencias.index[i], # palabra que corresponde al índice i
        xy=(np.log(frecuencias.iloc[i, index_medio[0]] + 1), np.log(frecuencias.iloc[i, index_medio[1]] + 1)), # ubicación del punto
        alpha=0.7 # transparencia del rótulo
    )

plt.show()



lista_palabras = {}
for k, p in palabras.items():
    lista_palabras[k] = p.split(" ")


matriz = []
for fil, rotulo_fil in enumerate(rotulos):
    linea = []
    for col, rotulo_col in enumerate(rotulos):
        if rotulo_fil == rotulo_col:
            linea.append(np.nan)
        else:
            coincidencias =  len(set(lista_palabras[rotulo_fil]) & set(lista_palabras[rotulo_col])) # set establece un conjunto
                                                                                                    # que tiene solo términos no repetidos
            linea.append(coincidencias)
    matriz.append(linea)

intersecciones = pd.DataFrame(matriz, columns=rotulos)
intersecciones.index = rotulos
print('---------------PALABRAS COMUNES')
print(intersecciones)




