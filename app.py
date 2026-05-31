import streamlit as st #Libreria para la interfaz principal
import streamlit.components.v1 as components

from data import TunjaData
print(TunjaData.NODOS)
from grafo import Grafo
from mapa import Mapa


#Configurar pagina

st.set_page_config (
    page_title = "AJ - MapsTunja",
    page_icon= "🗺️",
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items={"About": "Aplicación de rutas usando Dijkstra"}
)

st.markdown("""
<style>
  .stApp {background-color: #0f1117; color: #e8eaf0; }
 
  section[data-testid="stSidebar"] {
    background-color: #181c27;
    border-right: 1px solid #2a3050;
  }
 
  /* Tarjetas de métricas */
  .metrica {
    background: #1e2336;
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
  }
  .metrica-valor {
    font-size: 2rem;
    font-weight: 700;
    color: #3ecf8e;
    font-family: 'Space Mono', monospace;
  }
  .metrica-label {
    font-size: .78rem;
    color: #7a82a0;
    margin-top: 4px;
  }
 
  /* Pasos de Dijkstra */
  .paso {
    background: #1e2336;
    border-left: 3px solid #4f8ef7;
    padding: 6px 14px;
    margin: 3px 0;
    border-radius: 0 8px 8px 0;
    font-family: monospace;
    font-size: .82rem;
    color: #e8eaf0;
  }
</style>
""", unsafe_allow_html=True)


#CACHÉ: cada modo tiene su propio grafo, se guardan por separado en memoria
@st.cache_resource(
    show_spinner="⏳ Descargando red vehicular de Tunja…"
)
def cargar_grafo_vehicular() -> Grafo:
    g = Grafo(modo = "drive")
    g.cargar_lugares(TunjaData.NODOS)
    return g

@st.cache_resource(
    show_spinner="⏳ Descargando red peatonal de Tunja…"
)
def cargar_grafo_peatonal() -> Grafo:
    g = Grafo(modo = "walk")
    g.cargar_lugares(TunjaData.NODOS)
    return g

if "ruta_actual" not in st.session_state: #ultimo Dijkstra ejecutado
    st.session_state.ruta_actual = None 

if "modo_previo" not in st.session_state: #limpiar ruta anterior
    st.session_state.modo_previo = None


with st.sidebar:
    st.markdown("# 🗺️ MapsTunja")
    st.markdown(
        "**Explora rutas en Tunja con el algoritmo de Dijkstra.** "
        "Selecciona tu modo de transporte y descubre el camino más eficiente entre dos puntos de interés. \n" 
        "UPTC - Ingeniería de Sistemas y Computación"
    )
    st.divider()
    
    #Seleccionar modo de transporte
    st.markdown("## 🚗 Modo de transporte")
    modo = st.radio(
        "Tipo de ruta:",
        options = ["🚗  Vehicular", "🚶  Peatonal"],
        horizontal = True,
        label_visibility = "collapsed",
    )

    if modo != st.session_state.modo_previo: #si el usuario cambio el modo de transporte
        st.session_state.ruta_actual = None #limpiar ruta anterior
        st.session_state.modo_previo = modo #guardar modo anterior

    #Cargar grafo segun modo seleccionado
    if "Vehicular" in modo:
        grafo = cargar_grafo_vehicular()
        etiqueta = "🚗 Vehicular"
    else:
        grafo = cargar_grafo_peatonal()
        etiqueta = "🚶 Peatonal"

    st.divider()

    #Seleccionar origen y destino
    lugares = grafo.lista_lugares()
    st.markdown("## 📍 Origen")
    origen = st.selectbox(
        "Origen:",
        options = lugares,
        index = 0,
        label_visibility = "collapsed",
        key = "select_origen"
    )

    st.markdown("## 🏁 Destino")
    destino = st.selectbox(
        "Destino:",
        options = [l for l in lugares if l != origen],
        index = 0,
        label_visibility = "collapsed",
        key = "select_destino"
    )

    #Calcular ruta al hacer click
    st.markdown("")
    if st.button(
        "🔍  Encontrar ruta más corta",
        use_container_width = True,
        type = "primary",
    ):
        with st.spinner(f"Ejecutando Dijkstra sobre red{etiqueta}…"):
            resultado = grafo.ruta(origen, destino)

        if "error" in resultado:
            st.error(resultado["error"])
        else:
            st.session_state.ruta_actual = resultado
            st.success(f"✅ Ruta encontrada con éxito!: **{resultado['distancia_km']} km**")

    st.divider()

    #Agregar nuevo lugar
    with st.expander("➕  Agregar nuevo lugar"):
        st.markdown(
            "<small>El nuevo lugar se agrega como punto de interés. "
            "Al seleccionarlo como origen o destino, Dijkstra lo conecta "
            "automáticamente a la red vial más cercana.</small>",
            unsafe_allow_html=True
        )
        st.markdown("")

        nuevo_nombre = st.text_input(
            "Nombre del lugar:",
            placeholder = "Ej: Biblioteca Patiño Rocelli de Tunja",
            key = "nuevo_nombre"
        )
        nueva_desc = st.text_input(
            "Descripción breve:",
            placeholder = "Ej: Biblioteca pública ubicada en el Parque Pinzon de Tunja",
            key = "nueva_desc"
        )
        nuevo_icono = st.selectbox(
            "Icono:",
            options = ["📍","🏛️","⛪","🏢","🏫","🏥","🎓",
                       "🌲","🌳","🏞️","🔧","🩺","⚽","🚌",
                       "🏬","📚","🛍️","🚉","⚙️","🍽️","🏨"],
            key = "nuevo_icono"
        )

        col_lat, col_lng = st.columns(2)
        with col_lat:
            nueva_lat = st.number_input(
                "Latitud:",
                value = 5.5340,
                format = "%.5f",
                step = 0.0001,
                key = "nueva_lat"
            )
        with col_lng:
            nueva_lng = st.number_input(
                "Longitud:",
                value = -73.3630,
                format = "%.5f",
                step = 0.0001,
                key = "nueva_lng"
            )

        st.markdown(
            "<small>💡 Busca coordenadas en "
            "<a href='https://www.google.com/maps' target='_blank'>Google Maps</a>: "
            "clic derecho → ¿Qué hay aquí?</small>",
            unsafe_allow_html=True
        )

        if st.button("Agregar al mapa", use_container_width = True):
            ok, msg = grafo.agregar_lugar(
                nuevo_nombre,
                {
                    "coords": [nueva_lat, nueva_lng],
                    "icono": nuevo_icono,
                    "info": nueva_desc or "Lugar agregado por el usuario",
                }
            )
            if ok:
                st.success(msg)
                st.rerun() #recargar la app para mostrar el nuevo lugar en el mapa
            else:
                st.error(msg)

    #Grafo cargado
    st.divider()
    st.markdown(
        f"<small>🛣️ Red **{etiqueta}** cargada:  \n"
        f"**{len(grafo.G.nodes):,}** nodos · **{len(grafo.G.edges):,}** aristas  \n"
        f"📍 **{len(grafo.lugares)}** lugares de interés</small>",
        unsafe_allow_html=True
    )

##Parte principal - Mapa y resultados
st.markdown(f"## 🗺️ Mapa de Tunja — Red {etiqueta} (OpenStreetMap)")

ruta = st.session_state.ruta_actual
mapa_gen = Mapa()

if ruta:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metrica">
            <div class="metrica-valor">{ruta['distancia_km']} km</div>
            <div class="metrica-label">Distancia total</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metrica">
            <div class="metrica-valor">{ruta['num_intersecciones']}</div>
            <div class="metrica-label">Intersecciones en ruta</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metrica">
            <div class="metrica-valor">{ruta['total_explorados']}</div>
            <div class="metrica-label">Nodos visitados</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("")


if ruta and ruta.get("pasos"):
    st.divider()
    st.markdown("### ⚙️ Pasos del Algoritmo de Dijkstra")
    st.markdown(
        f"Dijkstra exploró **{ruta['total_explorados']:,} intersecciones** "
        f"de la red **{etiqueta}** antes de encontrar la ruta óptima "
        f"de **{ruta['distancia_km']} km**."
    )

    pasos = ruta["pasos"]
    for i, p in enumerate(pasos[:25]):
        km = round(p["distancia"] / 1000, 2)
        st.markdown(
            f'<div class="paso">'
            f'Paso {i+1:03d} &nbsp;|&nbsp; '
            f'Nodo: <code>{p["nodo_osm"]}</code> &nbsp;|&nbsp; '
            f'Dist. acumulada: <b>{km} km</b> &nbsp;|&nbsp; '
            f'Visitados: {p["visitados"]}'
            f'</div>',
            unsafe_allow_html=True
        )

    if len(pasos) > 25:
        st.markdown(f"*… y **{len(pasos) - 25:,} pasos más** (se muestran solo los primeros 25)*")