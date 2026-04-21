import requests
import pandas as pd
import json
import io
import time

# Usamos los enlaces de descarga directa para evitar redirecciones de portal (301)
ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def procesar_mef():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    for nombre, url in ENLACES.items():
        print(f"Descargando {nombre} desde servidor de archivos...")
        try:
            # allow_redirects=True es clave para manejar el 301 automáticamente
            r = requests.get(url, headers=headers, timeout=180, allow_redirects=True)
            
            if r.status_code == 200:
                # El MEF usa punto y coma (;) como separador estándar en sus CSV
                df = pd.read_csv(io.BytesIO(r.content), sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
                
                # Fragmentación de datos para GitHub
                chunk_size = 10000
                total_filas = len(df)
                partes = (total_filas // chunk_size) + 1
                
                for i in range(partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
                
                print(f"✅ {nombre} procesado: {total_filas} filas.")
                time.sleep(10) # Aumentamos la pausa para evitar bloqueos por saturación
            else:
                print(f"❌ Falló {nombre}. Código de error: {r.status_code}")
                
        except Exception as e:
            print(f"❌ Error en {nombre}: {str(e)}")

if __name__ == "__main__":
    procesar_mef()
