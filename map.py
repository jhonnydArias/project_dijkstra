import folium #libreria para crear mapas en HTML

class Mapa:

    CENTRO  = [5.5340, -73.3630]   # Centro aproximado de Tunja
    ZOOM    = 14
    TILE    = "CartoDB dark_matter" #fondo del mapa

    COLOR_NORMAL = "blue"
    COLOR_ORIGEN = "green"
    COLOR_DESTINO = "red"
    COLOR_NUEVO = "lightgreen"
    COLOR_RUTA = "ff6944"

    #Generar mapa completo
    def generar_mapa(self, lugares: dict, ruta_data: dict = None) -> folium.Map:
        m = folium.Map(location = self.CENTRO, zoom_start = self.ZOOM, tiles = self.TILE)

