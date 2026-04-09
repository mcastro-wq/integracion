import requests
from bs4 import BeautifulSoup
import json
import time

def extraer_data(cui):
    # URL de la arquitectura del CUI que vimos en tu código fuente
    url = f"https://ofi5.mef.gob.pe/ssi/Home/ArquitecturaCUI?codigo={cui}"
    
    # Cabeceras que imitan a un navegador real para evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://ofi5.mef.gob.pe/ssi/",
        "Connection": "keep-alive"
    }

    try:
        print(f"Intentando conectar con MEF para CUI: {cui}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"Error de conexión: Código {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraemos usando los IDs exactos de tu captura de código fuente
        nombre = soup.find(id="td_nominv").get_text(strip=True) if soup.find(id="td_nominv") else "No encontrado"
        
        # Si el nombre viene vacío o como "No encontrado", el MEF nos bloqueó o la data no cargó
        if not nombre or nombre == "No encontrado":
            print("El MEF devolvió una página vacía (Bloqueo de Bot)")
            return None

        costo_raw = soup.find(id="val_cta").get_text(strip=True) if soup.find(id="val_cta") else "0"
        situacion = soup.find(id="td_situinv").get_text(strip=True) if soup.find(id="td_situinv") else "N/A"
        estado = soup.find(id="td_estcu").get_text(strip=True) if soup.find(id="td_estcu") else "ACTIVO"

        # Limpiar el costo para que sea un número
        costo_limpio = costo_raw.replace(',', '').replace('S/', '').strip()
        pim = float(costo_limpio) if costo_limpio else 0.0

        return {
            "cui": cui,
            "nombre": nombre,
            "pim": pim,
            "situacion": situacion,
            "estado": estado,
            "actualizado": time.strftime("%d/%m/%Y %H:%M")
        }

    except Exception as e:
        print(f"Error procesando CUI {cui}: {str(e)}")
        return None

# --- EJECUCIÓN ---
cuis_a_buscar = ["2199528"] # El CUI de tus imágenes
resultados = []

for c in cuis_a_buscar:
    data = extraer_data(c)
    if data:
        resultados.append(data)
    time.sleep(3) # Pausa para no saturar al servidor

# Guardar el JSON (Esto es lo que lee tu seg_pro.html)
with open("data.json", "w", encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print(f"Proceso terminado. Registros en JSON: {len(resultados)}")
