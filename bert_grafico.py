import pickle
import pandas as pd
import plotly.io as pio

with open('pickles/modelo_bertopic.pkl', 'rb') as f:
    topic_model = pickle.load(f)

fig = topic_model.visualize_topics()
pio.renderers.default = "browser"
fig.show()

# Descomentar si se quiere guardar el gráfico
#fig.write_html("grafico_bertopic.html")