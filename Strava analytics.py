import os
import logging
import pandas as pd
from stravalib.client import Client
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Any

# Configuración de Logging (Mejor que print)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno (.env)
load_dotenv()

class StravaAnalytics:
    def __init__(self):
        """Inicializa el cliente y las configuraciones."""
        self.access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        self.club_id = int(os.getenv('STRAVA_CLUB_ID', '0'))
        self.csv_path = Path('data/historial_valtechies.csv')
        
        if not self.access_token or not self.club_id:
            raise ValueError("Faltan credenciales en el archivo .env")

        self.client = Client(access_token=self.access_token)

    def fetch_activities(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Descarga las actividades del club."""
        logger.info(f"Descargando últimas {limit} actividades del club {self.club_id}...")
        
        try:
            activities = self.client.get_club_activities(self.club_id, limit=limit)
            data = []
            for act in activities:
                # Usamos getattr para evitar errores si falta algún atributo
                data.append({
                    'id_actividad': act.id,  # CRUCIAL para evitar duplicados reales
                    'atleta': f"{act.athlete.firstname} {act.athlete.lastname or ''}".strip().title(),
                    'distancia_km': round(float(act.distance) / 1000, 2),
                    'tiempo_movimiento_min': round(float(act.moving_time) / 60, 2),
                    'elevacion': float(act.total_elevation_gain),
                    'actividad': str(act.sport_type), # Stravalib ya maneja esto mejor que "root="
                    'fecha': act.start_date_local
                })
            logger.info(f"Se obtuvieron {len(data)} actividades nuevas.")
            return data
        except Exception as e:
            logger.error(f"Error conectando con Strava: {e}")
            return []

    def load_history(self) -> pd.DataFrame:
        """Carga el historial existente o crea uno vacío."""
        if self.csv_path.exists():
            logger.info("Cargando historial existente...")
            return pd.read_csv(self.csv_path, sep=';')
        else:
            logger.warning("No se encontró historial. Creando nuevo DataFrame.")
            return pd.DataFrame(columns=[
                'id_actividad', 'atleta', 'distancia_km', 
                'tiempo_movimiento_min', 'elevacion', 'actividad', 'fecha'
            ])

    def process_and_merge(self, new_data: List[Dict[str, Any]], history_df: pd.DataFrame) -> pd.DataFrame:
        """Fusiona datos nuevos con historial y limpia duplicados usando ID."""
        if not new_data:
            return history_df

        new_df = pd.DataFrame(new_data)
        
        # Limpieza específica solicitada (aunque sport_type suele venir limpio, aseguramos)
        new_df['actividad'] = new_df['actividad'].astype(str).str.replace("root=", "").str.replace("'", "")

        # Filtrar actividades cortas (< 1km)
        new_df = new_df[new_df['distancia_km'] >= 1]

        # Concatenar
        combined_df = pd.concat([new_df, history_df], axis=0)

        # Deduplicación ROBUSTA: Usar el ID único de Strava
        # keep='first' prioriza la data más reciente si acabamos de descargarla
        if 'id_actividad' in combined_df.columns:
            before_dedupe = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=['id_actividad'], keep='first')
            logger.info(f"Duplicados eliminados: {before_dedupe - len(combined_df)}")
        else:
            # Fallback a la lógica original si no hay IDs en el historial viejo
            combined_df = combined_df.drop_duplicates()

        # Ordenar
        combined_df = combined_df.sort_values(by=['fecha', 'atleta'], ascending=[False, True])
        
        return combined_df

    def save_data(self, df: pd.DataFrame):
        """Guarda el DataFrame actualizado."""
        # Asegurar que el directorio existe
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(self.csv_path, sep=';', index=False)
        logger.info(f"Archivo guardado exitosamente en: {self.csv_path}")

def main():
    analytics = StravaAnalytics()
    
    # 1. Obtener datos
    new_data = analytics.fetch_activities()
    
    # 2. Cargar historial
    history_df = analytics.load_history()
    
    # 3. Procesar
    final_df = analytics.process_and_merge(new_data, history_df)
    
    # 4. Guardar
    analytics.save_data(final_df)
    
    # Vista previa
    print("\n--- Resumen de Datos Actualizados ---")
    print(final_df.head())

if __name__ == "__main__":
    main()
