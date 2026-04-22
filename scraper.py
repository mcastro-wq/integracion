import requests
import pandas as pd
import io
import time

# Enlaces corregidos según la estructura actual del servidor MEF
ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv"
}

def descargar_estilo_navegador(url):
    # Headers que imitan a un navegador real para evitar el bucle de redirecciones
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Se permite el redireccionamiento pero se valida que el contenido no sea una página HTML de error
        r = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
        content_type = r.headers.get('Content-Type', '').lower()
        
        if r.status_code == 200 and "html" not in content_type:
            return r.content
        else:
            print(f"⚠️ Error en {url}: El servidor devolvió {content_type} en lugar de CSV.")
            return None
    except Exception as e:
        print(f"❌ Error de conexión en {url}: {e}")
        return None

def ejecutar():
    for nombre, url in ENLACES.items():
        print(f"Iniciando descarga de: {nombre}...")
        data = descargar_estilo_navegador(url)
        
        if data:
            try:
                # Lectura flexible para detectar separadores automáticamente
                df = pd.read_csv(io.BytesIO(data), sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
                
                # División en archivos JSON de 10,000 registros para optimizar carga web
                chunk_size = 10000
                total_filas = len(df)
                num_partes = (total_filas // chunk_size) + 1
                
                print(f"Procesando {total_filas} filas en {num_partes} partes para {nombre}...")
                
                for i in range(num_partes):
                    chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                    if not chunk.empty:
                        nombre_archivo = f"data_{nombre}_parte_{i+1}.json"
                        chunk.to_json(nombre_archivo, orient='records', force_ascii=False)
                
                print(f"✅ {nombre} procesado exitosamente.")
                
            except Exception as e:
                print(f"❌ Falló el procesamiento de datos para {nombre}: {e}")
            
            # Pausa de seguridad para evitar bloqueos por IP (Rate Limiting)
            time.sleep(15)
        else:
            print(f"⏭️ Saltando {nombre} por error en descarga.")

if __name__ == "__main__":
    ejecutar()
