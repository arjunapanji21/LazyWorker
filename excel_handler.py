import pandas as pd

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def get_data(self):
        try:
            # Read Excel with string conversion for all columns
            df = pd.read_excel(
                self.file_path,
                dtype=str  # Convert all columns to string type
            )
            
            # Clean up any NaN values and strip whitespace
            df = df.fillna('')
            for column in df.columns:
                df[column] = df[column].str.strip()
            
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None
