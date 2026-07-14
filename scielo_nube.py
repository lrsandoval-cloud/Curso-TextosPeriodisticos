import pandas as pd
from langdetect import detect
from tqdm import tqdm
import pickle

base = pd.read_pickle('pickles/scielo_uy.pkl')
maximo = len(base)

lista_palabras = []
for i, row in tqdm(base.iterrows(), desc="Procesando datos", colour="green", unit=' artículos', total=maximo):
    lista = row['keywords'].split(', ')
    if i > maximo:
        break
    for t in lista:
        try:
            if detect(t) == "es":
                lista_palabras.append(t.lower())
        except Exception:
            continue


palabras = {}
for l in lista_palabras:
    if l in palabras:
        palabras[l] += 1
    else:
        palabras[l] = 1

with open('pickles/scielo_uy_keywords.pkl', 'wb') as f:
    pickle.dump(palabras, f)

from wordcloud import WordCloud
import matplotlib.pyplot as plt

wordcloud = WordCloud(width=800, height=400, background_color='white', colormap="plasma", max_words=50).generate_from_frequencies(palabras)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud)
plt.axis('off')
plt.title("SciELO Uruguay - Nube de palabras clave ")
plt.show()
