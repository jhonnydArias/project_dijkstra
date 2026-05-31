import folium #libreria para crear mapas en HTML

class Mapa:

    CENTRO  = [5.5340, -73.3630]   # Centro aproximado de Tunja
    ZOOM    = 14 #nivel ciudad
    TILE    = "CartoDB dark_matter" #fondo del mapa

    COLOR_NORMAL = "blue"
    COLOR_ORIGEN = "green"
    COLOR_DESTINO = "red"
    COLOR_NUEVO = "lightgreen"
    COLOR_RUTA = "ff6944"

    #Generar mapa completo
    def generar_mapa(self, lugares: dict, ruta_data: dict = None) -> folium.Map:
        m = folium.Map(location = self.CENTRO, zoom_start = self.ZOOM, tiles = self.TILE)  #mapa vacio

        nombre_origen = ruta_data.get("origen") if ruta_data else None
        nombre_destino = ruta_data.get("destino") if ruta_data else None

        for nombre, info in lugares.items():
            color = self.color_marcador(nombre, nombre_origen, nombre_destino, info)
            nombre_icono = self.icono_marcador(nombre, nombre_origen, nombre_destino)

            popup_html = f"""  
                <div style="font-family:Arial,sans-serif;min-width:170px;padding:4px">
                    <b style="font-size:14px">{info.get('icono','')} {nombre}</b><br>
                    <span style="color:#555;font-size:12px">{info.get('info','')}</span>
                    {"<br><span style='color:green;font-size:11px'>✨ Lugar nuevo</span>" if info.get('nuevo') else ""}
                </div>
            """
            ##Ventana emergente para cada marcador

            folium.Marker(
                location = info["coords"],
                popup = folium.Popup(popup_html, max_width = 230), #al hacer click
                tooltip = f"{info.get('icono','')} {nombre}", #al pasar el mouse
                icon = folium.Icon(color = color, icon = nombre_icono, prefix = "glyphicon"),
            ).add_to(m)


        if ruta_data and ruta_data.get("coordenadas_ruta"):
            coords = ruta_data["coordenadas_ruta"]

            # Línea de la ruta
            folium.PolyLine(
                locations = coords,
                color = f"#{self.COLOR_RUTA}",
                weight = 6,
                opacity = 0.95,
                tooltip = f"📏 Ruta: {ruta_data.get('distancia_km','?')} km"
            ).add_to(m)

            # Nodos intermedios del camino
            pasos = ruta_data.get("pasos", [])
            for i, coord in enumerate(coords[1:-1], start=1):
                dist_km = round(pasos[i]["distancia"] / 1000, 2) if i < len(pasos) else "?"
                folium.CircleMarker(
                    location = coord,
                    radius = 4,
                    color = f"#{self.COLOR_RUTA}",
                    fill = True,
                    fill_color = "#ffffff",
                    fill_opacity = 0.8,
                    weight = 2,
                    tooltip = f"Intersección {i} · {dist_km} km",
                ).add_to(m)

            if len(coords) >= 2:
                m.fit_bounds(
                    [[min(c[0] for c in coords), min(c[1] for c in coords)],
                     [max(c[0] for c in coords), max(c[1] for c in coords)]],
                     padding = (40, 40)
                )
        return m
    
    #Convertir mapa a HTML para streamlit
    def a_html(self, m: folium.Map) -> str:
        return m._repr_html_()
    
    def color_marcador(self, nombre, origen, destino, info) -> str:
        if nombre == origen:
            return self.COLOR_ORIGEN
        if nombre == destino:
            return self.COLOR_DESTINO
        if info.get("nuevo"):
            return self.COLOR_NUEVO
        return self.COLOR_NORMAL
    
    def icono_marcador(self, nombre, origen, destino) -> str:
        if nombre == origen:
            return "play"
        if nombre == destino:
            return "map-marker"
        return "info-sign"