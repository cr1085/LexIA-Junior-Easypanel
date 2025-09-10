import os
import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Eres un asistente legal experto. Tu única fuente de verdad es el contexto que te proporciono. Responde en español basándote exclusivamente en ese contexto. Si la respuesta no se encuentra en el texto, di clara y únicamente: 'La información solicitada no se encuentra en los documentos que he procesado.'"

class AIAssistant:
    def __init__(self):
        self.google_api_key = Config.GOOGLE_API_KEY
        self.cache = {}
        print(f"-> [AIAssistant] Asistente HÍBRIDO inicializado en modo: {Config.AI_PROVIDER}")

    def google_gemini_assistant(self, prompt: str):
        print("   -> Usando motor en la nube: Google Gemini...")
        if not self.google_api_key: return None
        
        API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.google_api_key}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                API_URL, headers=headers,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=90
            )
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Error con la API de Google Gemini: {e}")
            return None

    def ollama_assistant(self, prompt: str):
        print("   -> Usando motor local: Ollama (phi3:mini)...")
        try:
            url = "http://localhost:11434/v1/chat/completions"
            payload = { 
                "model": "phi3:mini", 
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], 
                "stream": False 
            }
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.ConnectionError:
            return "Error: No se pudo conectar con Ollama. Asegúrate de que el programa esté en ejecución."
        except Exception as e:
            logger.error(f"Error con Ollama: {e}")
            return None

    def get_response(self, prompt: str, use_cache: bool = True):
        if use_cache and prompt in self.cache:
            print("-> ¡Respuesta encontrada en la caché!")
            return self.cache[prompt]
        
        response = None
        provider = Config.AI_PROVIDER

        if provider == 'google':
            response = self.google_gemini_assistant(prompt)
        else:
            response = self.ollama_assistant(prompt)
        
        if response and use_cache:
            print("-> Guardando respuesta en la caché.")
            self.cache[prompt] = response
            
        return response if response else "Lo siento, el servicio de IA configurado no está respondiendo."

