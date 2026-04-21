import pandas as pd
import requests
import json
import io

def descargar_data_real():
    # 1. Configuración de la extracción de Invierte.pe
    url_invierte = "https://ofi5.mef.gob.pe/invierteWS/Ssi/expRepSSIDet"
    cui_objetivo = 2199528  # CUI de Chiclayo
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8"
    }

    # Payload para Gobierno Regional de Lambayeque (basado en tu captura)
    # Nota: Si quieres un CUI específico de forma global, a veces el WS permite filtrar por CUI directo
    payload = {
        "nivel": "R", 
        "region": "14", # Lambayeque
        "tipo": "0" 
    }

    try:
        print(f"Consultando Invierte.pe para el CUI {cui_objetivo}...")
        response = requests.post(url_invierte, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # El WS devuelve un Excel. Lo leemos con pandas
            df = pd.read_excel(io.BytesIO(response.content))
            
            # Limpiamos nombres de columnas (quitar espacios)
            df.columns = df.columns.str.strip()
            
            # Buscamos la fila del CUI (Asegúrate que el nombre de columna sea exacto, ej: 'CODIGO_UNICO')
            # Si no conoces el nombre exacto de la columna, imprimimos df.columns
            col_cui = [c for c in df.columns if 'CODIGO' in c.upper() or 'CUI' in c.upper()][0]
            fila = df[df[col_cui].astype(str) == str(cui_objetivo)]

            if not fila.empty:
                data_final = {
                    "cui": str(cui_objetivo),
                    "nombre": fila.iloc[0].get('NOMBRE_INVERSION', 'Nombre no encontrado'),
                    "monto_actualizado": float(fila.iloc[0].get('COSTO_ACTUALIZADO', 0)),
                    # Datos de ejemplo que podrías sacar de otras columnas del Excel:
                    "pim": float(fila.iloc[0].get('PIM', 0)), 
                    "devengado": float(fila.iloc[0].get('DEVENGADO_ACUMULADO', 0)),
                    "objetivo_estrategico": "Reducir el índice de victimización - Lambayeque",
                    "brecha": "Seguridad Ciudadana"
                }
                
                # Guardar el cruce en el JSON que lee tu index.html
                with open('data_cruzada.json', 'w', encoding='utf-8') as f:
                    json.dump([data_final], f, indent=4, ensure_ascii=False)
                
                print("¡Archivo data_cruzada.json actualizado exitosamente!")
            else:
                print(f"No se encontró el CUI {cui_objetivo} en la descarga.")
        else:
            print(f"Error de conexión: {response.status_code}")

    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    descargar_data_real()
