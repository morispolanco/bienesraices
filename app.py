import streamlit as st
import requests
import folium
import plotly.express as px
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

# Configuración inicial
st.set_page_config(page_title="Análisis y Visualización de Propiedades en Ciudad de Guatemala", layout="wide")

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

# Función para crear un mapa interactivo y renderizarlo en Streamlit
def crear_mapa_interactivo(propiedades):
    # Coordenadas para Ciudad de Guatemala
    m = folium.Map(location=[14.634915, -90.506882], zoom_start=12)
    geolocator = Nominatim(user_agent="geoapiExercises")

    for propiedad in propiedades:
        ubicacion = propiedad.get("direccion", None)
        if ubicacion:
            location = geolocator.geocode(ubicacion)
            if location:
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup=f"{propiedad.get('title', 'Sin título')}: ${propiedad.get('precio', 'N/D')}",
                    tooltip="Haz clic para más información"
                ).add_to(m)

    # Renderiza el mapa como HTML en Streamlit
    folium_static(m)

# Función para generar un gráfico de comparación de propiedades
def mostrar_comparacion_propiedades(propiedades):
    if propiedades:
        nombres = [p.get("title", "Sin título") for p in propiedades]
        precios = [int(p.get("precio", 0)) for p in propiedades]

        # Generar gráfico de barras comparando los precios
        fig = px.bar(x=nombres, y=precios, labels={'x': 'Propiedad', 'y': 'Precio'}, title="Comparación de Precios de Propiedades")
        st.plotly_chart(fig)
    else:
        st.write("No se seleccionaron propiedades para comparar.")

# Barra lateral para seleccionar la ciudad y otros filtros
st.sidebar.title("Filtros de Búsqueda")
ciudad = st.sidebar.text_input("Ciudad", "Ciudad de Guatemala")  # Ciudad de Guatemala por defecto
rango_precio = st.sidebar.slider("Rango de precio", 50000, 1000000, (100000, 500000))

# Búsqueda de propiedades
st.title("Aplicación de Análisis y Visualización de Propiedades en Ciudad de Guatemala")
st.write("Busque propiedades disponibles en el mercado y visualice tendencias de precios.")

if st.sidebar.button("Buscar propiedades"):
    query = f"propiedades en {ciudad}"
    resultado = obtener_propiedades(query)
    
    if resultado:
        propiedades = resultado.get("organic", [])  # Ajusta esto según los datos que devuelva Serper
        st.write("Resultado obtenido de Serper:", propiedades)  # Inspeccionamos los datos obtenidos
        if propiedades:
            st.subheader(f"Propiedades en {ciudad}")
            seleccionadas = []
            
            # Inicializamos el estado de cada propiedad en session_state
            if 'propiedades_seleccionadas' not in st.session_state:
                st.session_state.propiedades_seleccionadas = {i: False for i in range(len(propiedades))}
            
            # Mostrar propiedades con casillas de verificación
            for i, propiedad in enumerate(propiedades):
                title = propiedad.get('title', 'Sin título')
                snippet = propiedad.get('snippet', 'No hay descripción disponible.')
                precio = propiedad.get('precio', 'N/D')
                
                # Mostramos una casilla de verificación por cada propiedad y guardamos su estado
                st.session_state.propiedades_seleccionadas[i] = st.checkbox(f"{title} - {snippet} - Precio: {precio}", value=st.session_state.propiedades_seleccionadas[i])
            
            # Mapa interactivo
            st.subheader("Mapa de propiedades")
            crear_mapa_interactivo(propiedades)

            # Botón para comparar propiedades seleccionadas
            if st.button("Comparar propiedades seleccionadas"):
                # Filtrar propiedades seleccionadas por su estado en session_state
                propiedades_seleccionadas = [propiedades[i] for i, seleccionado in st.session_state.propiedades_seleccionadas.items() if seleccionado]
                if propiedades_seleccionadas:
                    mostrar_comparacion_propiedades(propiedades_seleccionadas)
                else:
                    st.write("No se seleccionaron propiedades para comparar.")
        else:
            st.write("No se encontraron propiedades.")
    else:
        st.write("No se encontraron propiedades.")
