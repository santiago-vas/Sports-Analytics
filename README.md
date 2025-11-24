# 🏃‍♂️ Strava Club Analytics & Leaderboard

Este proyecto automatiza la extracción, limpieza y consolidación de datos de actividades deportivas desde un **Club de Strava**. 

Diseñado originalmente para el grupo *"Green Waltechies"*, este script transforma la gestión manual de datos en un pipeline robusto de Python, permitiendo mantener un historial persistente y generar métricas para rankings o "podios".

## 🚀 Características Principales

Este código ha sido refactorizado siguiendo las mejores prácticas de desarrollo de software (Clean Code):

* **Seguridad Primero:** Las credenciales (Tokens API) no están expuestas en el código; se gestionan mediante variables de entorno (`.env`).
* **Integridad de Datos:** A diferencia de métodos basados en redondeo de cifras, este sistema utiliza el **ID único de actividad (Activity ID)** de Strava para evitar duplicados exactos y garantizar un historial limpio.
* **Persistencia Incremental:** Descarga nuevas actividades y las fusiona inteligentemente con el historial existente (`CSV`), actualizando registros si es necesario.
* **Limpieza Automática:**
    * Normalización de nombres de atletas.
    * Conversión de unidades (Metros a Km, Segundos a Minutos).
    * Filtrado de "actividades basura" (menores a 1km).
* **Portabilidad:** Uso de rutas relativas (`pathlib`), permitiendo que el código se ejecute en cualquier sistema operativo (Windows/Mac/Linux) sin modificar rutas de archivos.
* **Logging Profesional:** Sistema de trazas para monitorear el estado de la ejecución y detectar errores fácilmente.

## 📋 Requisitos Previos

* **Python 3.8** o superior.
* Una cuenta de **Strava**.
* Credenciales de API de Strava (Access Token).
* ID del Club de Strava que deseas monitorear.

## 🛠️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu entorno local:

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/TU_USUARIO/nombre-del-repo.git](https://github.com/TU_USUARIO/nombre-del-repo.git)
cd nombre-del-repo
