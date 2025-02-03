import pandas as pd


class ExcelReader:
    def __init__(self, file_path: str):
        """
        Initialize the ExcelReader with the file path.
        :param file_path: Path to the Excel file.
        """
        self.file_path = file_path
        self.data = None

    def read_file(self, sheet_name: str = None) -> pd.DataFrame:
        """
        Reads the Excel file into a DataFrame.
        :param sheet_name: Name of the sheet to read (default is the first sheet).
        :return: DataFrame with the Excel data.
        """
        try:
            self.data = pd.read_excel(self.file_path, sheet_name=sheet_name)
            print(f"Successfully read the file: {self.file_path}")
            return self.data
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
            raise
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
            raise

    def get_columns(self) -> list:
        """
        Get a list of column names from the loaded DataFrame.
        :return: List of column names.
        """
        if self.data is not None:
            return list(self.data.columns)
        else:
            print("Error: No data loaded. Please read the file first.")
            return []

    def filter_data(self, column_name: str, filter_value) -> pd.DataFrame:
        """
        Filter the data based on a column and a filter value.
        :param column_name: Column to filter by.
        :param filter_value: Value to filter for.
        :return: Filtered DataFrame.
        """
        if self.data is not None:
            if column_name in self.data.columns:
                filtered_data = self.data[self.data[column_name] == filter_value]
                return filtered_data
            else:
                print(f"Error: Column '{column_name}' not found in the data.")
                return pd.DataFrame()
        else:
            print("Error: No data loaded. Please read the file first.")
            return pd.DataFrame()