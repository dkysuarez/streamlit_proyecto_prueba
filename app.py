import streamlit as st
import pandas as pd
import numpy as np
import pybaseball as pyb
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt, patches
import seaborn as sns
from baseball_field_viz import transform_coords, draw_field, spraychart


st.write("Hola")
st.header("Soy Ali")
st.subheader("Analista de datos")

st.set_page_config(page_title= "Visualizacion de Beisbol", layout="wide")
st.title("Visualizacion de Beisbol")
st.markdown("---")

st.sidebar.header("Controles de visualizacion")

@st.cache_data
def load_data():
    return pyb.statcast_batter('2025-03-01','2025-11-01', player_id = 660271)


with st.spinner('Cargar datos...'):
    data = load_data()
    batting_data = data[data['events'].notnull()]

#Mostrar informacion basica en sidebar
st.sidebar.metric("Total de lanzamientos", len(data))
st.sidebar.metric("Eventos de bateo", len(batting_data))


#Selector de tipo de visualizacion
viz_type = st.sidebar.selectbox("Selecciona tipo de visualizacion",
                                ["Zonas de strike", "Mapa de Campo", "Tendencias", "Heatmaps", "Analisis Comparativo"]
                                )
if viz_type == "Zonas de strike":
    st.header("Analisis de zona de strike")
    st.markdown("Esta visualizacion muestra donde caen los lanzamientos que resultaron en contacto")

    col1, col2 = st.columns(2)

    with col1:
     #Grafico de zona de strik
     fig, ax = plt.subplots(figsize = (8,6))
     ax.add_patch(patches.Rectangle((-0.83,1.5), 1.66,2, fill= False, edgecolor='black',lw=2, label='Zona de Strike'))

     #Slider para filtrar por velocidad
     min_speed = st.slider("Velocidad minima (mph)",
     max_value = int(batting_data['release_speed'].max()),
     min_value = int(batting_data["release_speed"].min()),
     value = int(batting_data['release_speed'].min())
     )
     filtered_data = batting_data[batting_data['release_speed'] >= min_speed]
     sns.scatterplot(data=filtered_data, x='plate_x', y='plate_z', hue='events', alpha=0.7, ax=ax)
     ax.set_xlim(-2,2)
     ax.set_ylim(-0,5)
     ax.set_title(f"Zonas de Strike (Velocidad >= {min_speed} mph)")
     ax.set_xlabel("Posicion Horizontal")
     ax.set_ylabel("Posicion Vertical")
     ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
     st.pyplot(fig)


     with col2:
      #Heatmap de zona de strike
      st.subheader("Mapa de Campo - Zona de Strike")
      fig_heat, ax_heat = plt.subplots(figsize = (8,6))

      heatmap_data = pd.crosstab(
          pd.cut(batting_data['plate_z'], bins=10),
          pd.cut(batting_data['plate_x'], bins=10)
      )

      sns.heatmap(heatmap_data, ax=ax_heat, annot =  False, cbar_kws = {'label': 'Frecuencia'}, cmap= 'YlGnBu' )

      ax_heat.set_title("Densidad de Lanzamientos")
      ax_heat.set_xlabel("Posicion Horizontal")
      ax_heat.set_ylabel("Posicion Vertical")

      st.pyplot(fig_heat)

