clusters = 8
idioma = 'es' # Opciones: es (español), en (inglés)

import pandas as pd
import funciones
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

# Las primeras líneas son una copia del script kmeans.py, hasta obtener el
# objeto X_lsa

base = pd.read_pickle('pickles/base.pkl')
stop_words = funciones.obtener_stop_words(idioma)

rotulos = list(base['medio'].unique())
k_rotulos = len(rotulos)
data = base['lemas'].tolist()

vectorizer = TfidfVectorizer(
    max_df=0.5,
    min_df=5,
    stop_words=stop_words,
)
X_tfidf = vectorizer.fit_transform(data) # matriz vectorizada con Tf-idf
lsa = make_pipeline(TruncatedSVD(n_components=100, random_state=42), Normalizer(copy=False))
X_lsa = lsa.fit_transform(X_tfidf)

kmeans = KMeans(
    n_clusters=clusters,
    max_iter=300,
    n_init=10,
    random_state=42,
	)

kmeans.fit(X_lsa)

# Hasta acá lo que era copiado de kmeans.py


# Una vez hecho el gráfico, puede ser de utilidad graficar los clústers por separado,
# especialmente si están mezclados. Para eso seleccionar True e indicar el clúster
# a graficar
filtrar_cluster = False
mostrar_cluster = 3


# Reducimos a 2 dimensiones para graficar. PCA se usa en vez de TruncateSVD porque
# funciona mejor con matrices numéricas o con una matriz ya reducida como la que
# ya tengo en X_lsa
pca = PCA(n_components=2, random_state=42)
X_2d = pca.fit_transform(X_lsa)

# Etiquetas de los clusters
labels = kmeans.labels_

# Armamos un DataFrame para graficar. Está armado de acuerdo a lo que
# después necesita sns.scatterplot
df_plot = pd.DataFrame({
    'x': X_2d[:,0],
    'y': X_2d[:,1],
    'cluster': labels,
    'titulo': base['titulo'] if 'titulo' in base.columns else None
})



# Si quiero graficar un solo clúster, acá se seleccionan las filas correspondientes
# y se indica que el df a graficar es ese reducido. En caso contrario, el df a
# graficar es completo
if filtrar_cluster == True:
    df_cluster = df_plot[df_plot['cluster'] == mostrar_cluster]
    df_grafico = df_cluster
else:
    df_grafico = df_plot


# Graficamos
plt.figure(figsize=(10,7))
sns.scatterplot(
    data=df_grafico,
    x='x',
    y='y',
    hue='cluster',
    palette='tab10',
    s=60,
    alpha=0.7
)

# Opcional: marcar centroides
centroids_2d = pca.transform(kmeans.cluster_centers_)

plt.scatter(
    centroids_2d[:,0],
    centroids_2d[:,1],
    c='black',
    s=200,
    marker='X',
    label='Centroides'
)

plt.title("Distribución de nodos según KMeans")
plt.legend()
plt.show()
