import heapq #libreria de python --> colas de prioridad (queue)
import osmnx as ox #encapsula red vial de tunja (libreria externa)
from typing import Dict, List, Tuple

class Grafo:

    def __init__(self, modo: str = "drive"):
        self.modo = modo
        tipo = "vehicular" if modo == "drive" else "peatonal"
        print(f"⏳  Descargando red {tipo} de Tunja desde OpenStreetMap…")

        self.G = ox.graph_from_place("Tunja, Boyacá, Colombia", network_type= modo, simplify=True)
        print(f"✅  Red {tipo}cargada con éxito: {len(self.G.nodes):,} nodos · {len(self.G.edges):,} aristas")

        self.lugares: dict = {} #diccionario de lugares de interes


    def cargar_lugares(self, nodos_dict: dict) -> None:
        self.lugares = {k: dict(v) for k, v in nodos_dict.items()}

    #Agregar nodo
    def agregar_lugar(self, nombre: str, info: dict) -> tuple[bool, str]:
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre del lugar no puede estar vacío."
        if nombre in self.lugares:
            return False, f"Ya existe un lugar llamado {nombre}."
        if not info.get("coords") or len(info["coords"]) != 2:
            return False, "Las coordenadas son obligatorias"
        
        info["nuevo"] = True
        self.lugares[nombre] = info
        return True, f"'{nombre}' agregado correctamente al grafo."
    
    #Encontrar nodo mas cercano (OMS)
    def nodo_oms_cercano(self, lat: float, lng:float) -> int: #devuelve ID del nodo
        return ox.nearest_nodes(self.G, X=lng, Y=lat)


    #Algoritmo Dijkstra - MultiDiGraphn de OSMnx
    def dijkstra(self, origen_id: int, destino_id: int) -> tuple[dict, dict, list]:
        dist = {n: float("inf") for n in self.G.nodes()}
        prev = {n: None for n in self.G.nodes()}
        dist[origen_id] = 0.0  #Se inicializa distancias en infinito y sin predecesor

        cola = [(0.0, origen_id)] #cola de prioridad (distancia_acumulada, nodo)
        visitados = set()
        pasos = [] 

        while cola:
            d_actual, u = heapq.heappop(cola) #extrae nodo con menor distancia acumulada
            if u in visitados:
                continue
            visitados.add(u)

            pasos.append({"nodo": u, "distancia": round(d_actual, 1), "visitados": len(visitados)}) #registro de pasos a mostrar

            if u == destino_id:
                break
            for v in self.G.neighbors(u):
                if v in visitados:
                    continue

                aristas = self.G[u][v]
                peso = min(data.get("length", float("inf")) for data in aristas.values())

                nueva_dist = dist[u] + peso
                if nueva_dist < dist[v]:
                    dist[v] = nueva_dist
                    prev[v] = u
                    heapq.heappush(cola, (nueva_dist, v))

        return dist, prev, pasos
    
    #Reconstruir el camino desde prev[]
    def reconstruir_camino(self, prev: dict, origen_id: int, destino_id: int) -> list:
        camino = []
        actual = destino_id
        while actual is not None:
            camino.append(actual)
            actual = prev[actual]
        camino.reverse()

        if not camino or camino[0] != origen_id:
            return [] # No se encontró un camino válido
        return camino  
    

    def coords_nodos(self, nodos_ids: list) -> list:
        return [(self.G.nodes[n]["y"], self.G.nodes[n]["x"]) for n in nodos_ids] #Coordenadas lat, lng
    

    #Calcular ruta entre dos lugares

    def ruta(self, nombre_origen: str, nombre_destino: str) -> dict:
        if nombre_origen not in self.lugares:
            return {"error": f"Lugar '{nombre_origen}' no encontrado"}
        if nombre_destino not in self.lugares:
            return {"error": f"Lugar '{nombre_destino}' no encontrado"}
        if nombre_origen == nombre_destino:
            return {"error": "El origen y el destino son iguales"}
        
        lat_origen, lng_origen = self.lugares[nombre_origen]["coords"]
        lat_destino, lng_destino = self.lugares[nombre_destino]["coords"]

        origen_id = self.nodo_oms_cercano(lat_origen, lng_origen)
        destino_id = self.nodo_oms_cercano(lat_destino, lng_destino)

        dist, prev, pasos = self.dijkstra(origen_id, destino_id)

        if dist[destino_id] == float("inf"):
            return {"error": f"No se pudo encontrar la ruta entre '{nombre_origen}' y '{nombre_destino}'"}
        
        camino = self.reconstruir_camino(prev, origen_id, destino_id)
        coordenadas_ruta = self.coords_nodos(camino)
        distancia = dist[destino_id] #dist. total origen-destino

        return {
            "origen": nombre_origen,
            "destino": nombre_destino,
            "distancia_m": round(distancia, 1),
            "distancia_km": round(distancia / 1000, 2),
            "num_intersecciones": len(camino),
            "coordenadas_ruta": coordenadas_ruta,
            "pasos": pasos,
            "total_visitados": len(pasos),    
            "modo": self.modo,        
        }
        

    def lista_lugares(self) -> list:
        return list(self.lugares.keys())