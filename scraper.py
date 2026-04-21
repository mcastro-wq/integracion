import requests
import pandas as pd
import json
import io
import time

ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def descargar_con_reintentos(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://datosabiertos.mef.gob.pe/'
    }
    
    # Intentamos obtener la URL real siguiendo saltos manualmente si es necesario
    try:
        response = requests.get(url, headers=headers, timeout=120, stream=True)
        # Si el servidor intenta marearnos con redirects, esto ayuda a estabilizar
        return response
    except requests.exceptions.TooManyRedirects:
        # Si falla por redirecciones, intentamos una vez más sin seguir redirects automáticamente
        return requests.get(url, headers=headers, timeout=120, allow_redirects=False)

def procesar_mef():
    for nombre, url in ENLACES.items():
        print(f"Iniciando descarga de {nombre}...")
        try:
            r = descargar_con_reintentos(url)
            
            if r.status_code == 200:
                # Usamos stream para leer el contenido y evitar picos de memoria
                df = pd.read_csv(io.BytesIO(r.content), sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
                
                chunk_size = 10000
                total_filas = len(df)
                partes = (total_filas // chunk_size) + 1
                
                for i in range(partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
                
                print(f"✅ {nombre} procesado con éxito ({total_filas} registros).")
                time.sleep(5) # Pausa de cortesía para que el MEF no nos bloquee por velocidad
            else:
                print(f"❌ Error {r.status_code} en {nombre}. El servidor rechazó la conexión.")
                
        except Exception as e:
            print(f"❌ Fallo en {nombre}: {str(e)}")

if __name__ == "__main__":
    procesar_mef()
