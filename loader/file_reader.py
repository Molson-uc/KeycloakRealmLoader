import pandas as pd


class FileHandler:

    def __init__(self, path: str, sheet: str = "Roles") -> None:
        self.__path = path
        self.__sheet = sheet
        self.__setup_df()

    def path(self) -> str:
        return self.__path

    @property
    def sheet(self) -> str:
        return self.__sheet

    @sheet.setter
    def sheet(self, value: str) -> None:
        self.__sheet = value
        self.__setup_df()

    def get_headers(self) -> list[str]:
        if self._dataframe is None:
            raise ValueError(
                "Dataframe is not initialized. Ensure the file and sheet are correctly loaded."
            )
        return self._dataframe.columns.tolist()

    def __setup_df(self):
        try:
            if not self.__path:
                raise ValueError("File path cannot be empty.")
            self._dataframe = pd.read_excel(self.__path, self.sheet)
            if self._dataframe.empty:
                raise ValueError(
                    f"The sheet '{self.sheet}' in file '{self.__path}' is empty."
                )
            self._dataframe = self._dataframe.ffill(axis=0)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at path '{self.__path}' was not found.")
        except ValueError as ve:
            raise ValueError(f"Error reading sheet '{self.sheet}': {ve}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

    def dataFrame_to_dict(self):
        return self._dataframe.to_dict(orient="index").values()

    def dataframe_merge(self, dataframe: pd.DataFrame, key: str = ""):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("The provided argument is not a valid pandas DataFrame.")
        if key not in self._dataframe.columns or key not in dataframe.columns:
            raise KeyError(
                f"The key '{key}' must be present in both DataFrames for merging."
            )
        self._dataframe = pd.merge(self._dataframe, dataframe, on=key)

    def data_frame_group(self, key: str, column_name: str):
        if key not in self._dataframe.columns:
            raise KeyError(f"The key '{key}' is not in the DataFrame columns.")
        if column_name not in self._dataframe.columns:
            raise KeyError(
                f"The column '{column_name}' is not in the DataFrame columns."
            )
        self._dataframe = self._dataframe.groupby(key).agg(
            {
                col: "first" if col != column_name else list
                for col in self._dataframe.columns
            }
        )

    def get_fields(self, *args: str) -> list[dict]:
        if not all(arg in self._dataframe.columns for arg in args):
            missing = [arg for arg in args if arg not in self._dataframe.columns]
            raise KeyError(
                f"The following fields are missing from the DataFrame: {missing}"
            )
        datas = self.dataFrame_to_dict()
        response = []
        for data in datas:
            small_dict = {arg: data.get(arg, None) for arg in args}
            response.append(small_dict)
        return response

    def get_dataframe(self):
        return self._dataframe
