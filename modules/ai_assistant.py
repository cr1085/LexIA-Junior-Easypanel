import os
import requests
import json
import logging
from typing import Optional
import re

class LegalAIAssistant:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
    def get_response(self, prompt: str, user_id: int) -> str:
        """Obtiene respuesta de la IA"""
        if not self.is_legal_related(prompt):
            return "⚠️ Solo puedo responder preguntas relacionadas con derecho y asuntos jurídicos."
        
        response = self.groq_assistant(prompt)
        if response:
            return response
            
        response = self.openrouter_assistant(prompt)
        if response:
            return response
            
        return "⚠️ Los servicios de IA no están disponibles temporalmente."
    
    def groq_assistant(self, prompt: str) -> Optional[str]:
        """Usa Groq API"""
        if not self.groq_api_key:
            return None
            
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"Error con Groq API: {e}")
            return None
    
    def openrouter_assistant(self, prompt: str) -> Optional[str]:
        """Usa OpenRouter como alternativa"""
        if not self.openrouter_api_key:
            return None
            
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "google/gemma-7b-it:free",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            logging.error(f"Error con OpenRouter: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        return """Eres un abogado junior que trabaja en un bufete de abogados. 
Eres profesional pero accesible, entusiasta por aprender y ayudar.

Responde de manera natural y conversacional, sin formato de discord.
Sé analítico pero reconociendo limitaciones.
Nunca des garantías de éxito en casos.
Siempre recomienda consultar con abogados senior para casos complejos.
"""
    
    def is_legal_related(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        legal_terms = [
            'derecho', 'ley', 'legal', 'jurídico', 'abogado', 'proceso', 'juicio', 
            'demanda', 'contrato', 'testamento', 'herencia', 'penal', 'civil', 
            'mercantil', 'laboral', 'fiscal', 'notario', 'documento', 'escritura',
            'poder', 'arrendamiento', 'compraventa', 'sociedad', 'empresa', 'patente',
            'marca', 'propiedad intelectual', 'familia', 'divorcio', 'hipoteca',
            'despido', 'contrato laboral', 'delito', 'prisión', 'detención', 'prueba',
            'testigo', 'mediación', 'arbitraje', 'responsabilidad civil', 'daños',
            'indemnización', 'competencia', 'protección de datos', 'usufructo'
        ]
        
        for term in legal_terms:
            if term in prompt_lower:
                return True
                
        patterns = [
            r'(cómo|como)\s+(demandar|reclamar).*',
            r'(qué|que)\s+(debo|debería).*(hacer|proceder)',
            r'(necesito|quiero)\s+(hacer|redactar).*(contrato|testamento|poder)',
            r'(cuánto|cuanto)\s+(tiempo|dura|tarda).*(proceso|juicio|demanda)',
            r'(qué|que)\s+(derechos|obligaciones).*(tengo|tiene)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, prompt_lower):
                return True
                
        return False