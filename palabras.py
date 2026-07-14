import pandas as pd
from funciones import obtener_dic_palabras
from funciones import obtener_stop_words

idioma = 'en' # Opciones: es (español), en (inglés)
base = pd.read_pickle('pickles/base_eng.pkl')

rotulos = list(base['medio'].unique())

palabras = obtener_dic_palabras(base)

stop_words = obtener_stop_words(idioma)

from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(stop_words=stop_words)
corpus = list(palabras.values())
X = vectorizer.fit_transform(corpus)
frecuencias = pd.DataFrame(X.toarray(), index=rotulos, columns=vectorizer.get_feature_names_out())

for rotulo in rotulos:
    top = frecuencias.loc[rotulo].sort_values(ascending=False).head(20)
    print(rotulo)
    for i, v in top.items():
        print(i + " (" + str(v) + "), ", end='')
    print()
    print()



from wordcloud import WordCloud
import matplotlib.pyplot as plt

for rotulo in rotulos:
    cantidad = frecuencias.loc[rotulo].to_dict()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(cantidad)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.title("Nube de palabras - " + rotulo)
    plt.show()




