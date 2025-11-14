import os
import sys
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from gemini_client import GeminiClient
from excel_writer import ExcelWriter

def setup_environment():
    """Configura el entorno y verifica dependencias"""
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY_1'):
        print("Error: GEMINI_API_KEY_1 no encontrada en .env (se requiere al menos una clave).")
        sys.exit(1)
    
    # Crear carpetas necesarias
    os.makedirs('papers_to_identify', exist_ok=True)
    os.makedirs('output', exist_ok=True)

def get_subfolders(base_path):
    """Obtiene la lista de subcarpetas part_X ordenadas"""
    subfolders = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.startswith('part_'):
            try:
                part_num = int(item.split('_')[1])
                subfolders.append((part_num, item))
            except (IndexError, ValueError):
                continue
    
    return [item[1] for item in sorted(subfolders)]

def process_subfolder(subfolder_path, pdf_processor, gemini_client, excel_writer, start_item):
    """Procesa todos los PDFs en una subcarpeta"""
    pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        try:
            pdf_path = os.path.join(subfolder_path, pdf_file)
            print(f"\nProcesando: {pdf_file}")
            
            # Extraer texto de la primera página
            text = pdf_processor.extract_first_page_text(pdf_path)
            if not text:
                print(f"  ⚠️  No se pudo extraer texto de {pdf_file}")
                data = {"author": "not found", "year": "not found", 
                       "title": "not found", "abstract": "not found"}
            else:
                # Extraer información usando Gemini
                data = gemini_client.extract_paper_info(text)
            
            # Agregar información del archivo
            data['item'] = start_item
            data['file_name'] = pdf_file
            
            # Escribir en Excel
            excel_writer.add_row(data)
            start_item += 1
            
            print(f"  ✅ Completado: {data.get('author', 'N/A')} ({data.get('year', 'N/A')})")
            
        except Exception as e:
            print(f"  ❌ Error procesando {pdf_file}: {str(e)}")
            # Agregar fila con errores
            error_data = {
                'item': start_item,
                'file_name': pdf_file,
                'author': 'not found',
                'year': 'not found',
                'title': 'not found',
                'abstract': 'not found'
            }
            excel_writer.add_row(error_data)
            start_item += 1
    
    return start_item

def main():
    """Función principal"""
    setup_environment()
    
    # Inicializar componentes
    pdf_processor = PDFProcessor()
    gemini_client = GeminiClient()
    excel_writer = ExcelWriter('output/papers_identified.xlsx')
    
    # Obtener subcarpetas
    base_path = 'papers_to_identify'
    subfolders = get_subfolders(base_path)
    
    if not subfolders:
        print("No se encontraron subcarpetas part_X en papers_to_identify/")
        return
    
    print(f"Encontradas {len(subfolders)} subcarpetas: {', '.join(subfolders)}")
    
    # Determinar el siguiente item number
    start_item = excel_writer.get_next_item_number()
    
    # Procesar subcarpetas una por una
    for subfolder in subfolders:
        subfolder_path = os.path.join(base_path, subfolder)
        print(f"\n{'='*50}")
        print(f"Procesando subcarpeta: {subfolder}")
        print(f"{'='*50}")
        
        # Resetea el contador de llamadas y la clave de API al inicio
        # de una nueva carpeta, según tu requerimiento.
        gemini_client.reset_key_rotation()

        start_item = process_subfolder(subfolder_path, pdf_processor, 
                                     gemini_client, excel_writer, start_item)
        
        # Preguntar si continuar
        if subfolder != subfolders[-1]:
            print(f"\nSubcarpeta {subfolder} completada.")
            response = input("¿Continuar con la siguiente subcarpeta? (s/n): ").strip().lower()
            if response != 's':
                print("Ejecución detenida por el usuario.")
                break
        else:
            print("\n¡Todas las subcarpetas han sido procesadas!")
    
    excel_writer.save()
    print(f"\nProceso completado. Resultados guardados en output/papers_identified.xlsx")

if __name__ == "__main__":
    main()