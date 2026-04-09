import requests
from bs4 import BeautifulSoup
import json
import os

def scrapear_mef(cui):
    url = f"https://ofi5.mef.gob.pe/ssi/Home/ArquitecturaCUI?codigo={cui}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Extraer datos exactos de tus capturas
        nombre = soup.find("span", id="lblNombreProyecto").text.strip() if soup.find("span", id="lblNombreProyecto") else "No encontrado"
        estado = soup.find("span", id="lblEstado").text.strip() if soup.find("span", id="lblEstado") else "N/A"
        costo = soup.find("span", id="lblCostoActualizado").text.strip() if soup.find("span", id="lblCostoActualizado") else "0"
        
        return {
            "cui": cui,
            "nombre": nombre,
            "estado": estado,
            "pim": float(costo.replace(',', '')),
            "devengado": 0, # Requiere scraping adicional
            "actualizado": "09/04/2026"
        }
    except:
        return None

# Lista de CUIs que quieres seguir
lista_cuis = ["2199528", "2456781"] 
resultados = []

for cui in lista_cuis:
    data = scrapear_mef(cui)
    if data:
        resultados.append(data)

# Guardar en archivo que leerá el HTML
with open("data.json", "w", encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)
