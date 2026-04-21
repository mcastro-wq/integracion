import pandas as pd
import requests
import json
import io
import sys

def extraer():
    url = "https://ofi5.mef.gob.pe/invierteWS/Ssi/expRepSSIDet"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://ofi5.mef.gob.pe",
        "Referer": "https://ofi5.mef.gob.pe/ssi/"
    }
    payload = {"nivel": "R", "region": "14", "tipo": "0"}

    try:
        print("Enviando petición al MEF...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"Error del servidor: {response.status_code}")
            sys.exit(1) # Forzar error en GitHub Actions

        # Leer Excel
        df = pd.read_excel(io.BytesIO(response.content))
        df.columns = df.columns.str.strip()
        
        # Mapeo super simple para asegurar que no falle por nombres de columnas
        # Si estas columnas no existen, el script fallará aquí y sabremos por qué
        df_final = df.rename(columns={
            'CUI': 'cui',
            'NOMBRE DE LA INVERSION': 'nombre',
            'COSTO ACTUALIZADO': 'monto_actualizado',
            'PIM 2023': 'pim',
            'DEVENGADO ACUMULADO': 'devengado'
        })

        # Convertir a JSON
        data = df_final.to_dict(orient='records')
        
        with open('data_cruzada.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print("¡Archivo data_cruzada.json creado exitosamente en la raíz!")

    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    extraer()
