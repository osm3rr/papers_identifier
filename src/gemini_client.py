"""
Cliente de Python refactorizado para interactuar con la API de Gemini
utilizando la biblioteca google-genai actualizada.

Este cliente está optimizado para:
1. Usar instrucciones de sistema (system_instruction).
2. Forzar la salida en modo JSON (response_mime_type).
3. Manejar la configuración de seguridad.
"""

import google.generativeai as genai
import os
import yaml
import json

class GeminiClient:
    """
    Cliente para interactuar con la API de Google Gemini (google-genai).
    
    Utiliza un prompt de sistema y solicita respuestas en formato JSON
    para una extracción de información fiable.
    """
    
    def __init__(self):
        """Inicializa el cliente, carga la configuración y el modelo."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            # Es una mejor práctica fallar rápido si la API key no está.
            raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")
            
        # Configura la biblioteca una vez.
        genai.configure(api_key=self.api_key)
        
        self.prompt_config = self._load_prompt_config()
        self.model = self._initialize_model()
        
        # --- MEJORA: Fallar rápido si el modelo no se inicializa ---
        if not self.model:
            raise RuntimeError("Falló la inicialización del modelo Gemini. Revisa los logs de error anteriores (causados por YAML o la API).")
        # --- FIN DE LA MEJORA ---

    def _load_prompt_config(self):
        """
        Carga la configuración del prompt desde un archivo YAML.
        """
        try:
            with open('config/prompt_config.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                if 'system_prompt' not in config:
                    print("Advertencia: 'system_prompt' no se encontró en prompt_config.yaml")
                    config['system_prompt'] = '' # Asegura que la clave exista
                return config
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de configuración en 'config/prompt_config.yaml'")
            raise
        except Exception as e:
            print(f"Error cargando configuración YAML: {e}")
            raise

    def _initialize_model(self):
        """
        Inicializa el GenerativeModel con configuración avanzada.
        
        Configura el modelo para:
        1. Usar el 'system_prompt' de la configuración.
        2. Devolver respuestas estrictamente en "application/json".
        3. Usar configuraciones de seguridad permisivas para la tarea.
        """
        if not self.prompt_config:
            print("Error: Configuración de prompt no cargada. No se puede inicializar el modelo.")
            return None

        try:
            # Configuración para forzar la salida JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            
            # Para tareas de extracción, a veces es útil ser más permisivo
            # con las configuraciones de seguridad, aunque esto depende del caso de uso.
            
            # --- INICIO DE LA MODIFICACIÓN ---
            # El error 'dangerous_content' indica un problema al intentar
            # desactivar los filtros de seguridad.
            # Vamos a eliminar esta sección y usar los filtros seguros por defecto.
            # safety_settings = {
            #     'HATE_SPEECH': 'BLOCK_NONE',
            #     'HARASSMENT': 'BLOCK_NONE',
            #     'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            #     'DANGEROUS_CONTENT': 'BLOCK_NONE',
            # }
            # --- FIN DE LA MODIFICACIÓN ---
            
            system_instruction = self.prompt_config.get('system_prompt', '')

            model = genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=system_instruction,
                generation_config=generation_config
                # Eliminamos la línea de safety_settings
                # safety_settings=safety_settings
            )
            return model
        except Exception as e:
            print(f"Error fatal inicializando el modelo Gemini: {e}")
            return None

    def extract_paper_info(self, text: str) -> dict:
        """
        Extrae información del paper usando Gemini con modo JSON.
        
        Args:
            text (str): Texto de la primera página del paper.
            
        Returns:
            dict: Información extraída del paper.
        """
        if not self.model:
            print("Error: El modelo no está inicializado. Abortando extracción.")
            return self._create_empty_response()

        if not text or not text.strip():
            print("Texto de entrada vacío. Devolviendo respuesta vacía.")
            return self._create_empty_response()
        
        try:
            # El system_prompt ya está configurado en el modelo.
            # Solo necesitamos enviar el texto del usuario.
            # Limitamos el tamaño para evitar errores de contexto.
            user_prompt = f"Texto del paper:\n{text[:15000]}"
            
            response = self.model.generate_content(user_prompt)
            
            # Es buena práctica revisar si el prompt fue bloqueado
            if response.prompt_feedback.block_reason:
                print(f"Prompt bloqueado por: {response.prompt_feedback.block_reason}")
                return self._create_empty_response()

            # El modelo está configurado para devolver JSON,
            # por lo que response.text debería ser un string JSON.
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            # Captura errores de la API (ej. timeouts, errores de autenticación)
            print(f"Error durante la llamada a Gemini API (generate_content): {str(e)}")
            return self._create_empty_response()

    def _parse_gemini_response(self, response_text: str) -> dict:
        """
        Parsea la respuesta JSON de Gemini a un diccionario.
        
        Args:
            response_text (str): El string JSON devuelto por el LLM.
            
        Returns:
            dict: Diccionario con los campos normalizados.
        """
        try:
            # Ya no necesitamos regex, simplemente cargamos el JSON.
            data = json.loads(response_text)
            
            # Validar y limpiar datos
            return {
                'author': str(data.get('author', 'not found')).strip(),
                'year': str(data.get('year', 'not found')).strip(),
                'title': str(data.get('title', 'not found')).strip(),
                'abstract': str(data.get('abstract', 'not found')).strip()
            }
                
        except json.JSONDecodeError as e:
            print(f"Error crítico: Gemini no devolvió un JSON válido.")
            print(f"Error de parseo: {e}")
            print(f"Respuesta recibida: {response_text[:500]}...") # Loguea parte de la respuesta
            return self._create_empty_response()
        except Exception as e:
            print(f"Error inesperado parseando la respuesta: {e}")
            return self._create_empty_response()

    def _create_empty_response(self) -> dict:
        """Crea una respuesta vacía estandarizada para errores."""
        return {
            'author': 'not found',
            'year': 'not found',
            'title': 'not found',
            'abstract': 'not found'
        }

if __name__ == '__main__':
    # Ejemplo de cómo se usaría el cliente
    # (Asegúrate de tener GEMINI_API_KEY en tu entorno y config/prompt_config.yaml)
    
    print("Iniciando prueba de GeminiClient...")
    
    # Crear un mock de config/prompt_config.yaml para la prueba
    if not os.path.exists('config'):
        os.makedirs('config')
    
    mock_config = {
        'system_prompt': """
        Eres un asistente experto en análisis de documentos científicos.
        Tu tarea es extraer la siguiente información del texto proporcionado:
        - author: El primer autor o autores.
        - year: El año de publicación.
        - title: El título completo del paper.
        - abstract: El resumen (abstract) completo del paper.

        Responde únicamente en formato JSON.
        """
    }
    
    try:
        with open('config/prompt_config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(mock_config, f)
            
        mock_paper_text = """
        A Novel Method for AI-Driven Paper Extraction
        
        John Doe, Jane Smith
        
        (2024)
        
        Abstract
        We present a new technique for automatically extracting metadata
        from scientific papers using advanced large language models.
        Our method achieves state-of-the-art results.
        """
        
        client = GeminiClient()
        info = client.extract_paper_info(mock_paper_text)
        
        print("\nInformación extraída:")
        print(json.dumps(info, indent=2))
        
        # Prueba de texto vacío
        print("\nProbando con texto vacío:")
        info_empty = client.extract_paper_info("")
        print(json.dumps(info_empty, indent=2))
        
    except ValueError as e:
        print(f"Error de configuración: {e}")
        print("Asegúrate de exportar tu GEMINI_API_KEY.")
    except Exception as e:
        print(f"Ocurrió un error durante la prueba: {e}")