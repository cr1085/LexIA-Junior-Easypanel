import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import logging

class LegalScraper:
    def __init__(self):
        self.sources = {
            'boe': {
                'url': 'https://www.boe.es/buscar/',
                'params': {'q': '', 'sort_field': 'fecha', 'sort_order': 'desc'}
            },
            'europa': {
                'url': 'https://eur-lex.europa.eu/search.html',
                'params': {'text': '', 'type': 'advanced', 'lang': 'es'}
            },
            'congreso': {
                'url': 'https://www.congreso.es/busqueda-de-iniciativas',
                'params': {'texto': '', 'tipo': 'all'}
            }
        }
    
    def search_legislation(self, query: str, source: str = 'boe') -> list:
        """Busca legislación en fuentes oficiales"""
        if source not in self.sources:
            return []
        
        try:
            if source == 'boe':
                return self._search_boe(query)
            elif source == 'europa':
                return self._search_europa(query)
            elif source == 'congreso':
                return self._search_congreso(query)
        except Exception as e:
            logging.error(f"Error en scraper {source}: {e}")
            return []
    
    def _search_boe(self, query: str) -> list:
        """Busca en el Boletín Oficial del Estado"""
        results = []
        params = self.sources['boe']['params'].copy()
        params['q'] = query
        
        try:
            response = requests.get(
                self.sources['boe']['url'], 
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.resultado-busqueda')
            
            for item in items[:5]:  # Limitar a 5 resultados
                title_elem = item.select_one('.titulo a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = title_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.boe.es' + link
                
                date_elem = item.select_one('.fecha')
                date = date_elem.get_text(strip=True) if date_elem else 'Fecha no disponible'
                
                summary_elem = item.select_one('.texto')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'summary': summary,
                    'source': 'BOE'
                })
                
        except Exception as e:
            logging.error(f"Error scraping BOE: {e}")
        
        return results
    
    def _search_europa(self, query: str) -> list:
        """Busca en la legislación europea"""
        # Implementación similar para EUR-Lex
        # (Código simplificado por brevedad)
        return []
    
    def _search_congreso(self, query: str) -> list:
        """Busca iniciativas parlamentarias"""
        # Implementación similar para Congreso de los Diputados
        # (Código simplificado por brevedad)
        return []
    
    def get_law_text(self, url: str) -> str:
        """Obtiene el texto completo de una ley"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar elementos no deseados
            for elem in soup.select('.skip, .anuncio, .publicidad'):
                elem.decompose()
            
            # Extraer el texto principal
            text = ''
            content_selectors = [
                '#textoxslt', 
                '.articulado', 
                '.disposicion',
                'main article',
                '.contenido'
            ]
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    text = content.get_text(separator='\n', strip=True)
                    break
            
            if not text:
                text = soup.get_text(separator='\n', strip=True)
            
            # Limitar tamaño y limpiar texto
            text = text[:50000]  # Límite de caracteres
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Eliminar líneas vacías múltiples
            
            return text
            
        except Exception as e:
            logging.error(f"Error obteniendo texto de ley: {e}")
            return f"Error al obtener el texto: {str(e)}"