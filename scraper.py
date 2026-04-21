import requests
import pandas as pd
import io
import time

ENLACES = {
    "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
    "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B_INVERSIONES.csv",
    "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL_INVERSIONES.csv"
}

def descargar_estilo_navegador(url):
    # Estos son los headers que envía un Chrome en Incógnito
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Intentamos descargar SIN SEGUIR REDIRECTS primero para romper el bucle
        r = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
        if r.status_code == 200 and "html" not in r.headers.get('Content-Type', ''):
            return r.content
        else:
            print(f"⚠️ El servidor intentó bloquear la petición automática.")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def ejecutar():
    for nombre, url in ENLACES.items():
        print(f"Descargando {nombre}...")
        data = descargar_estilo_navegador(url)
        if data:
            df = pd.read_csv(io.BytesIO(data), sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
            # Guardamos por partes
            chunk_size = 10000
            for i in range((len(df) // chunk_size) + 1):
                chunk = df.iloc[i*chunk_size : (i+1)*chunk_size]
                if not chunk.empty:
                    chunk.to_json(f"data_{nombre}_parte_{i+1}.json", orient='records', force_ascii=False)
            print(f"✅ {nombre} listo.")
            time.sleep(20) # Pausa para "enfriar" la IP entre archivos
        else:
            print(f"⏭️ Falló {nombre}")

if __name__ == "__main__":
    ejecutar()
