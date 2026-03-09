import streamlit as st
import pandas as pd
import numpy as np
import pybaseball as pyb
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt, patches
import seaborn as sns
from baseball_field_viz import transform_coords, draw_field, spraychart

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
     plt.close()


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
      plt.close()

      #Mapa campo interactivo
elif viz_type == "Mapa de Campo":
    st.header("Mapa de Bateo")
    st.markdown("Visualizacion de donde caen las bolas bateadas en el campo")

    color_by = st.radio("Colorea por:", ['events', 'launch_speed', 'launch_angle'])
    fig2,ax2 = plt.subplots(figsize = (12,10))
    spraychart(ax2,batting_data,color_by = color_by, title = f"Distribucion de Bateo - Coloreado por "
                                                             f"{color_by}")
    st.pyplot(fig2)
    plt.close()

#Grafico de Tendencias
elif viz_type == "Tendencias":
    st.header("Tendencias y Estadisticas")
    st.markdown("Analisis de tendencias en el rendimiento del bateador")

    st.subheader("Evolucion del Velocidad de salida")

    batting_data['game_date'] = pd.to_datetime(batting_data['game_date'])
    daily_stats =  batting_data.groupby('game_date').agg({
        'launch_speed': 'mean',
        'launch_angle': 'mean',
        'events' : 'count'
    }).reset_index()

    col1, col2 =  st.columns(2)
    with col1:
        fig_hist = px.histogram(batting_data, x='launch_speed', nbins = 30,
                                title='Histograma de velocidad de Salida',
                                labels = {'launch_speed': 'Velocidad (mph)'})
        st.plotly_chart(fig_hist, use_cotainer_width = True)

    with col2:
        st.subheader("Velocidad vs Angulo de Salida")
        fig_scatter = px.scatter(batting_data, x="launch_speed", y="launch_angle",
                                 color = 'events', hover_data = ['events'],
                                 title = 'Relacion Velocidad-Angulo',
                                 labels = {'launch_speed': 'Velocidad (mph)',
                                           'launch_angle': 'Angulo (grados)'})
        st.plotly_chart(fig_scatter, use_container  = True)





