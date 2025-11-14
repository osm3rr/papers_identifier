import pandas as pd
import os

class ExcelWriter:
    """Manejador de escritura en archivo Excel"""
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.data = []
        self.columns = ['item', 'file_name', 'author', 'year', 'title', 'abstract']
        
        # Cargar datos existentes si el archivo existe
        if os.path.exists(output_path):
            self._load_existing_data()
    
    def _load_existing_data(self):
        """Carga datos existentes del archivo Excel"""
        try:
            existing_df = pd.read_excel(self.output_path)
            # Convertir a lista de diccionarios
            self.data = existing_df.to_dict('records')
        except Exception as e:
            print(f"Error cargando archivo existente: {e}")
            self.data = []
    
    def get_next_item_number(self):
        """Obtiene el siguiente número de item"""
        if not self.data:
            return 1
        return max(item['item'] for item in self.data) + 1
    
    def add_row(self, row_data):
        """Agrega una nueva fila de datos"""
        # Validar que tenga todas las columnas necesarias
        validated_row = {col: row_data.get(col, 'not found') for col in self.columns}
        self.data.append(validated_row)
    
    def save(self):
        """Guarda los datos en el archivo Excel"""
        try:
            df = pd.DataFrame(self.data, columns=self.columns)
            df.to_excel(self.output_path, index=False, sheet_name='Papers')
            print(f"Datos guardados en {self.output_path}")
        except Exception as e:
            print(f"Error guardando archivo Excel: {e}")