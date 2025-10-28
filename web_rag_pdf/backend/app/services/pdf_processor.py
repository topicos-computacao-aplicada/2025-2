from pypdf import PdfReader
from typing import List
import re

class PDFProcessor:
    def extract_text(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                # Limpar texto - remover múltiplos espaços e quebras de linha excessivas
                page_text = re.sub(r'\s+', ' ', page_text).strip()
                text += page_text + " "
                
            return text.strip()
        except Exception as e:
            print(f"❌ Erro ao extrair texto do PDF: {e}")
            raise

    def chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
        if not text:
            return []
            
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Encontrar um ponto de quebra natural próximo ao chunk_size
            end = start + chunk_size
            
            if end >= text_length:
                # Último chunk
                chunk = text[start:]
                if len(chunk.strip()) > 50:  # Só adicionar se tiver conteúdo significativo
                    chunks.append(chunk.strip())
                break
            
            # Tentar quebrar em ponto final, vírgula ou espaço
            break_points = ['.', '!', '?', ',', ';', ' ']
            for break_point in break_points:
                break_pos = text.rfind(break_point, start, end)
                if break_pos != -1 and break_pos > start + chunk_size // 2:
                    end = break_pos + 1
                    break
            
            chunk = text[start:end].strip()
            if chunk:  # Só adicionar chunks não vazios
                chunks.append(chunk)
            
            start = end - chunk_overlap
            if start < 0:
                start = 0
        
        print(f"📊 Texto dividido em {len(chunks)} chunks")
        return chunks