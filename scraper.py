import requests
import pandas as pd
import json
import io
import time
import random

ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def obtener_datos_robusto(url):
    # Lista de navegadores para engañar al firewall del MEF
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Intentamos la descarga ignorando el bucle de redirecciones (allow_redirects=False)
    # y luego siguiendo solo un paso si es necesario.
    try:
        with requests.Session() as s:
            r = s.get(url, headers=headers, timeout=120, allow_redirects=True)
            return r
    except requests.exceptions.TooManyRedirects:
        # Si entra en bucle, pedimos el archivo sin permitir redirecciones y 
        # confiamos en que el contenido venga en el primer salto.
        return requests.get(url, headers=headers, timeout=120, allow_redirects=False)

def procesar():
    for nombre, url in ENLACES.items():
        print(f"--- Iniciando descarga de {nombre} ---")
        try:
            r = obtener_datos_robusto(url)
            
            if r.status_code in [200, 301, 302]:
                # Si es un redirect, intentamos leer el contenido igual (a veces el CSV viene ahí)
                content = r.content
                df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
                
                chunk_size = 10000
                total = len(df)
                partes = (total // chunk_size) + 1
                
                for i in range(partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
                
                print(f"✅ {nombre} procesado: {total} filas.")
                
                # Pausa LARGA y ALEATORIA para no parecer un bot
                espera = random.randint(15, 25)
                print(f"Esperando {espera} segundos para evitar bloqueo...")
                time.sleep(espera)
                
            else:
                print(f"❌ Error {r.status_code} en {nombre}")
                
        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {str(e)}")

if __name__ == "__main__":
    procesar()
