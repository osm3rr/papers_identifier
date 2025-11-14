from google import genai
import os
import yaml
import json
import re

class GeminiClient:
    """Cliente para interactuar con la API de Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = self._initialize_model()
        self.prompt_config = self._load_prompt_config()
    
    def _initialize_model(self):
        """Inicializa el modelo de Gemini"""
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    
    def _load_prompt_config(self):
        """Carga la configuración del prompt desde YAML"""
        try:
            with open('config/prompt_config.yaml', 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return None
    
    def extract_paper_info(self, text):
        """
        Extrae información del paper usando Gemini
        
        Args:
            text (str): Texto de la primera página del paper
            
        Returns:
            dict: Información extraída del paper
        """
        try:
            if not text.strip():
                return self._create_empty_response()
            
            # Construir el prompt
            system_prompt = self.prompt_config.get('system_prompt', '')
            full_prompt = f"{system_prompt}\n\nTexto del paper:\n{text[:15000]}"  # Limitar tamaño
            
            # Realizar la solicitud
            response = self.model.generate_content(full_prompt)
            
            # Parsear respuesta
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            print(f"Error en Gemini API: {str(e)}")
            return self._create_empty_response()
    
    def _parse_gemini_response(self, response_text):
        """Parsea la respuesta de Gemini a un diccionario"""
        try:
            # Intentar extraer JSON de la respuesta
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Validar y limpiar datos
                return {
                    'author': data.get('author', 'not found').strip(),
                    'year': str(data.get('year', 'not found')).strip(),
                    'title': data.get('title', 'not found').strip(),
                    'abstract': data.get('abstract', 'not found').strip()
                }
            else:
                print("No se encontró JSON en la respuesta")
                return self._create_empty_response()
                
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            return self._create_empty_response()
    
    def _create_empty_response(self):
        """Crea una respuesta vacía para errores"""
        return {
            'author': 'not found',
            'year': 'not found',
            'title': 'not found',
            'abstract': 'not found'
        }