### Libs
import pandas as pd
import numpy as np
import random
from tabulate import tabulate


from src.standard_format import replace_with
from metadata import DatasetMetadata
from schema import DatasetSchema, SchemaDetector


class Dataset():

    def __init__(self,
                data: pd.DataFrame,
                metadata: DatasetMetadata | None = None,
                schema: DatasetSchema | None = None,
                target_column: str | None = None,
                groups_columns: list | None = None
        ):
        # Process data first, then initialize parent with processed data
        self.data = data
        self.__process_data()
        self.schema = (
            schema
            if schema is not None
            else SchemaDetector().detect_schema(data)
        )
        self.metadata = (
            metadata
            if metadata is not None
            else DatasetMetadata.from_dataframe(data)
        )


    @classmethod
    def from_dataframe(cls, df):
        schema = SchemaDetector().detect_schema(df)
        metadata = DatasetMetadata.from_dataframe(df)
        return cls(
            data=df,
            metadata=metadata,
            schema=schema,
        )


    @property
    def _constructor(self):
        """Ensure operations on the DataFrame return Dataset instances"""
        return Dataset

    @property
    def dataframe(self):
        return self.data.copy()

    @property
    def columns(self):
        return self.data.columns

    def __process_data(self):
        # Standardize column names
        self.data.columns = [replace_with(col) for col in self.data.columns]
        return self

    def __repr__(self):
        return self.data.__repr__()

    def get_shape(self):
        return """Columns: {} \nRows: {}""".format(self.data.shape[1], self.data.shape[0])

    def get_columns_types(self):
        dict_type =  {}
        for col in self.data.columns:
            dict_type[col] = str(self.data[col].dtypes).replace("dtype", "")
        return dict_type

    def get_numerical_columns(self):
        return self.data.select_dtypes(
            include=[np.number, np.float64, np.int64]).columns.tolist()

    def get_dataset_info(self, complete=True, to_file=False):
        # WIP - add more info, and add option to export to file
        dataframe = {}
        # Generation of dataset info
        dataframe["Column"] = self.data.columns
        dataframe["Dtypes"] = [self.data[col].dtypes for col in self.data.columns]
        dataframe["Rows"] = [len(self.data[col]) for col in self.data.columns]
        dataframe["Categorized"] = ["Yes"
                                    if (len(self.data[col].unique()) / len(self.data[col])) <= 0.1 and (str(self.data[col].dtypes) == "object" or str(self.data[col].dtypes) == "string" or str(self.data[col].dtypes) == "category")
                                    else "No"
                                    for col in self.data.columns]
        if complete:
            dataframe["Null values"] = [len(self.data[col].isnull().loc[lambda x: x])
                                            for col in self.data.columns]
            dataframe["Inf values"] = [len(self.data[col].loc[lambda x: (x == np.inf) | (x == -np.inf)])
                                        for col in self.data.columns]
            dataframe["NA values"] = [len(self.data[col].loc[lambda x: (x == "NA") | (x == "") | (x == " ")])
                                        for col in self.data.columns]
            dataframe["Duplicates"] = [len(self.data[col].duplicated().loc[lambda x: x])
                                        for col in self.data.columns]

        dataframe = pd.DataFrame(data=dataframe)
        if to_file:
            print(tabulate(dataframe.values, headers=list(dataframe.columns),
                            tablefmt="grid"))
        return dataframe


