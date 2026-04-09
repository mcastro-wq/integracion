import requests
from bs4 import BeautifulSoup
import json
import time

def scrapear_mef(cui):
    # Esta es la URL que devuelve el contenido que me pasaste
    url = f"https://ofi5.mef.gob.pe/ssi/Home/ArquitecturaCUI?codigo={cui}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://ofi5.mef.gob.pe/ssi/"
    }
    
    try:
        print(f"Consultando CUI: {cui}...")
        res = requests.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8' # Forzamos codificación para tildes
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # EXTRACCIÓN BASADA EN TU CÓDIGO FUENTE:
        # Nota: Usamos .text.strip() para limpiar espacios
        
        nombre = soup.find(id="td_nominv").get_text(strip=True) if soup.find(id="td_nominv") else "No encontrado"
        estado = soup.find(id="td_estcu").get_text(strip=True) if soup.find(id="td_estcu") else "N/A"
        situacion = soup.find(id="td_situinv").get_text(strip=True) if soup.find(id="td_situinv") else "N/A"
        
        # El costo actualizado según tu código fuente está en el ID 'val_cta'
        costo_raw = soup.find(id="val_cta").get_text(strip=True) if soup.find(id="val_cta") else "0"
        costo_num = float(costo_raw.replace(',', '')) if costo_raw != "" else 0.0

        return {
            "cui": cui,
            "nombre": nombre,
            "estado": estado,
            "situacion": situacion,
            "pim": costo_num,
            "avance": 0, # Dato que suele cargar por JS aparte
            "actualizado": time.strftime("%d/%m/%Y")
        }
    except Exception as e:
        print(f"Error procesando {cui}: {e}")
        return None

# Lista de tus proyectos (Añade aquí todos los que necesites)
mis_cuis = ["2199528"] 

resultados = []
for c in mis_cuis:
    data = scrapear_mef(c)
    if data:
        resultados.append(data)

# Guardamos el JSON
with open("data.json", "w", encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print("¡Archivo data.json generado con éxito!")
