# Paper Identifier - Sistema de Identificación Automatizada de Papers Académicos

## Descripción

Este proyecto es un sistema de inteligencia artificial que automatiza la extracción de información clave de papers académicos en formato PDF. Utiliza el modelo Gemini de Google para analizar la primera página de cada paper y extraer automáticamente:

- Autor principal (apellido e inicial del nombre)
- Año de publicación
- Título del paper
- Abstract


## Explicación Técnica

### Arquitectura del Sistema

El sistema sigue una arquitectura modular con separación de responsabilidades:

1. **PDFProcessor**: Maneja la extracción de texto de archivos PDF
2. **GeminiClient**: Gestiona la comunicación con la API de Gemini
3. **ExcelWriter**: Controla la persistencia de datos en formato Excel
4. **Main**: Coordina el flujo principal y la interacción con el usuario

### Flujo de Datos

1. **Entrada**: PDFs organizados en subcarpetas `part_X`
2. **Procesamiento**: 
   - Extracción de texto con `pdfplumber`
   - Análisis con Gemini usando prompts estructurados
   - Validación y parsing de respuestas JSON
3. **Salida**: Archivo Excel con columnas estandarizadas

### Características de Implementación

- **Configuración Externa**: Prompts y configuraciones en YAML para fácil modificación
- **Manejo de Estado**: Persistencia automática y recuperación de progreso
- **Interfaz de Usuario**: Feedback claro en consola con emojis y progreso
- **Robustez**: Múltiples niveles de manejo de errores y fallbacks

Este sistema proporciona una solución completa y profesional para la automatización de la identificación de papers académicos, combinando las mejores prácticas de desarrollo con herramientas modernas de IA.

## Características Principales

- **Procesamiento por lotes**: Organiza los PDFs en subcarpetas (`part_1`, `part_2`, etc.)
- **Control interactivo**: Permite pausar y continuar el procesamiento entre subcarpetas
- **Tolerante a fallos**: Continua el procesamiento incluso cuando encuentra errores
- **Persistencia de datos**: Mantiene un archivo Excel actualizado con todos los resultados
- **Manejo de APIs**: Integración con Gemini API para análisis de texto

## Estructura del Proyecto
```bash
paper_identifier/
├── config/ # Configuraciones YAML para el LLM
├── src/ # Código fuente Python
├── papers_to_identify/ # Carpeta de entrada con subcarpetas
├── output/ # Carpeta de salida con resultados
├── .env # Variables de entorno (no versionado)
└── requirements.txt # Dependencias del proyecto`
```

## Requisitos Previos

- Python 3.8 o superior
- Cuenta en Google AI Studio con API key para Gemini
- Entorno virtual de Python

## Instalación y Configuración

### 1. Clonar y Configurar el Entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Registro de Cambios Recientes

**Noviembre 2025**

- Se implementó rotación automática de claves API Gemini: el sistema alterna entre varias claves configuradas en `.env` para evitar límites de uso y mejorar la robustez.
- Mejoras en el manejo de errores: ahora el sistema detecta y reporta fallos en la extracción de texto, respuestas inválidas de la API y problemas de configuración.
- Configuración avanzada por YAML: los prompts y el formato de respuesta se gestionan desde `config/prompt_config.yaml`, facilitando la personalización sin modificar el código fuente.
- Persistencia y recuperación de progreso: el sistema carga automáticamente los resultados previos del archivo Excel y continúa el procesamiento sin duplicar datos.
- Control interactivo por subcarpeta: el usuario puede pausar y continuar el procesamiento entre lotes de archivos PDF.