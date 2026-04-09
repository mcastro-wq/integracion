import requests
from bs4 import BeautifulSoup
import json
import time

def scrapear_mef(cui):
    # Intentamos con la URL directa de consulta
    url = f"https://ofi5.mef.gob.pe/ssi/Home/ArquitecturaCUI?codigo={cui}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        session = requests.Session()
        print(f"Iniciando raspado de CUI: {cui}...")
        
        # Hacemos la petición
        res = session.get(url, headers=headers, timeout=30)
        res.encoding = 'utf-8'
        
        if res.status_code != 200:
            print(f"Error de servidor: {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. Extraer Nombre (ID: td_nominv)
        nombre_element = soup.find(id="td_nominv")
        nombre = nombre_element.get_text(strip=True) if nombre_element else "No encontrado"
        
        # 2. Extraer Estado (ID: td_estcu)
        estado_element = soup.find(id="td_estcu")
        estado = estado_element.get_text(strip=True) if estado_element else "N/A"
        
        # 3. Extraer Situación (ID: td_situinv)
        situacion_element = soup.find(id="td_situinv")
        situacion = situacion_element.get_text(strip=True) if situacion_element else "N/A"
        
        # 4. Extraer Costo Actualizado (ID: val_cta)
        costo_element = soup.find(id="val_cta")
        costo_raw = costo_element.get_text(strip=True) if costo_element else "0"
        
        # Limpiar el número de comas y espacios
        costo_limpio = costo_raw.replace(',', '').replace('S/', '').strip()
        try:
            pim = float(costo_limpio)
        except:
            pim = 0.0

        # Si el nombre sigue vacío, es que el MEF no cargó la data
        if nombre == "No encontrado" or nombre == "":
            print(f"Atención: El CUI {cui} devolvió página vacía. El MEF podría estar bloqueando el bot.")
            return None

        return {
            "cui": cui,
            "nombre": nombre,
            "estado": estado,
            "situacion": situacion,
            "pim": pim,
            "avance": 0,
            "actualizado": time.strftime("%d/%m/%Y %H:%M")
        }

    except Exception as e:
        print(f"Error crítico en {cui}: {str(e)}")
        return None

# --- LISTA DE CUIS ---
mis_cuis = ["2199528"] 

resultados = []
for c in mis_cuis:
    data = scrapear_mef(c)
    if data:
        resultados.append(data)
    # Pausa de 2 segundos para no ser bloqueados
    time.sleep(2)

# GUARDAR SIEMPRE (aunque sea vacío para debug, pero esperamos que tenga data)
with open("data.json", "w", encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print(f"Proceso finalizado. Registros capturados: {len(resultados)}")
