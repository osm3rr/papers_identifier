import pdfplumber
import os

class PDFProcessor:
    """Manejador de procesamiento de archivos PDF"""
    
    def extract_first_page_text(self, pdf_path):
        """
        Extrae texto de la primera página de un PDF
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            str: Texto extraído o cadena vacía si hay error
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return ""
                
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                return text if text else ""
                
        except Exception as e:
            print(f"Error al procesar PDF {pdf_path}: {str(e)}")
            return ""