import streamlit as st
import requests
import folium
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

# Configuración inicial
st.set_page_config(page_title="Análisis y Visualización de Propiedades", layout="wide")

# Función para obtener propiedades de la API de Serper
def obtener_propiedades(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": st.secrets["serper_api_key"],
        "Content-Type": "application/json"
    }
    data = {
        "q": query
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener datos de Serper: {response.status_code}")
        return None

# Función para hacer predicciones con la API de Together
def predecir_precio(model, messages):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['together_api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener predicción de Together: {response.status_code}")
        return None

# Función para crear un mapa interactivo
def crear_mapa_interactivo(propiedades):
    m = folium.Map(location=[-34.603722, -58.381592], zoom_start=12)
    geolocator = Nominatim(user_agent="geoapiExercises")
    
    for propiedad in propiedades:
        ubicacion = propiedad["direccion"]
        location = geolocator.geocode(ubicacion)
        if location:
            folium.Marker(
                location=[location.latitude, location.longitude],
                popup=f"{propiedad['titulo']}: ${propiedad['precio']}",
                tooltip="Haz clic para más información"
            ).add_to(m)
    
    folium_static(m)

# Función para generar gráficos de tendencias
def mostrar_grafico_tendencias(precios, fechas):
    fig = px.line(x=fechas, y=precios, labels={'x': 'Fecha', 'y': 'Precio'}, title="Tendencia de Precios")
    st.plotly_chart(fig)

# Barra lateral para seleccionar la ciudad y otros filtros
st.sidebar.title("Filtros de Búsqueda")
ciudad = st.sidebar.text_input("Ciudad", "Buenos Aires")
rango_precio = st.sidebar.slider("Rango de precio", 50000, 1000000, (100000, 500000))

# Búsqueda de propiedades
st.title("Aplicación de Análisis y Visualización de Propiedades")
st.write("Busque propiedades disponibles en el mercado y visualice tendencias de precios.")

if st.sidebar.button("Buscar propiedades"):
    query = f"propiedades en {ciudad}"
    resultado = obtener_propiedades(query)
    if resultado:
        propiedades = resultado.get("organic", [])  # Ajusta esto según los datos que devuelva la API de Serper
        st.subheader(f"Propiedades en {ciudad}")
        for propiedad in propiedades[:5]:  # Mostramos solo las primeras 5 propiedades
            st.write(f"**{propiedad['title']}** - {propiedad['snippet']}")
            
        # Mapa interactivo (puedes adaptar las ubicaciones según los resultados)
        st.subheader("Mapa de propiedades")
        crear_mapa_interactivo(propiedades)
    else:
        st.write("No se encontraron propiedades.")

# Predicción de precios
st.sidebar.title("Predicción de Precios")
if st.sidebar.button("Predecir tendencia de precios"):
    if ciudad:
        modelo = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
        mensajes = [{"role": "user", "content": f"Predice la tendencia de precios de propiedades en {ciudad}"}]
        prediccion = predecir_precio(modelo, mensajes)
        if prediccion:
            contenido = prediccion['choices'][0]['message']['content']
            st.subheader("Predicción de Precios")
            st.write(f"Predicción: {contenido}")
else:
    st.write("No se seleccionó ninguna ciudad para predicción.")

# Visualización comparativa (si se necesitan más detalles, puedes expandir esta sección)
st.sidebar.title("Comparar propiedades")
if st.sidebar.button("Comparar"):
    if ciudad:
        st.subheader("Comparación de Propiedades")
        st.write("Comparación de precios por metro cuadrado, proximidad a servicios, etc.")
else:
    st.write("No hay suficientes datos para comparar.")
