import pandas as pd
import requests
import json
import io
import sys

def integrar_data():
    urls = {
        "detalle": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "situacion": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "f12b": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv"
    }
    
    print("Iniciando descarga masiva e integración...")

    try:
        # 1. Cargar Detalle Principal
        res_det = requests.get(urls["detalle"], timeout=180)
        df_det = pd.read_csv(io.BytesIO(res_det.content), sep=';', encoding='latin-1', low_memory=False)
        # Limpieza robusta de cabeceras para evitar el error 'upper'
        df_det.columns = [str(c).strip().upper() for c in df_det.columns]
        df_det = df_det[df_det['DEPARTAMENTO'] == 'LAMBAYEQUE'].copy()

        # 2. Cargar Estado Situacional
        res_sit = requests.get(urls["situacion"], timeout=120)
        df_sit = pd.read_csv(io.BytesIO(res_sit.content), sep=';', encoding='latin-1', low_memory=False)
        df_sit.columns = [str(c).strip().upper() for c in df_sit.columns]

        # 3. Cargar Formato 12B
        res_12b = requests.get(urls["f12b"], timeout=120)
        df_12b = pd.read_csv(io.BytesIO(res_12b.content), sep=';', encoding='latin-1', low_memory=False)
        df_12b.columns = [str(c).strip().upper() for c in df_12b.columns]

        maestro_final = []

        for _, row in df_det.iterrows():
            cui_val = row['CODIGO_UNIC']
            
            # Búsqueda de problemática
            sit_row = df_sit[df_sit['CODIGO_UNIC'] == cui_val].sort_values('FECHA_REGISTRO', ascending=False)
            comentario = sit_row.iloc[0]['DESCRIPCION'] if not sit_row.empty else "Sin reporte reciente"

            # Búsqueda de seguimiento 12B
            f12b_row = df_12b[df_12b['CODIGO_UNIC'] == cui_val]
            avance = float(f12b_row.iloc[0]['AVANCE_FISIC']) if not f12b_row.empty else row.get('AVANCE_FISICO', 0)
            pasos = f12b_row.iloc[0]['ACC_PROBLEMA'] if not f12b_row.empty else "En ejecución"

            maestro_final.append({
                "cui": str(cui_val),
                "nombre": str(row.get('NOMBRE_INVERSION', 'N/A')),
                "costo_actualizado": float(row.get('COSTO_ACTUALIZADO', 0)),
                "pim_2026": float(row.get('PIM_ANIO_ACTUAL', 0)),
                "devengado_acumulado": float(row.get('DEVEN_ACUMUL_ANIO_ANT', 0)) + float(row.get('DEV_ANIO_ACTUAL', 0)),
                "avance_fisico_porc": avance,
                "estado_invierte": row.get('ESTADO', 'N/A'),
                "situacion_invierte": row.get('SITUACION', 'N/A'),
                "estado_situacional_mef": comentario,
                "seguimiento_proximos_pasos": pasos,
                "unidad_ejecutora": row.get('NOMBRE_UEP', 'N/A')
            })

        with open('data_cruzada.json', 'w', encoding='utf-8') as f:
            json.dump(maestro_final, f, indent=4, ensure_ascii=False)
        
        print(f"Éxito: {len(maestro_final)} proyectos procesados.")

    except Exception as e:
        print(f"Error en la integración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    integrar_data()
