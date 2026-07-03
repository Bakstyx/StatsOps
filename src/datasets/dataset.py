### Libs
from typing import Literal
import pandas as pd
import numpy as np
from tabulate import tabulate

from src.standard_format import replace_with
from .metadata import DatasetMetadata
from .schema import DatasetSchema
from .detector import SchemaDetector
from .validator import ValidationReport


class Dataset():

    def __init__(self,
                data: pd.DataFrame,
                metadata: DatasetMetadata | None = None,
                schema: DatasetSchema | None = None,
                automatic_dtype_definition: bool = True
        ):
        """_summary_

        Args:
            data (pd.DataFrame): The input DataFrame containing the dataset.
            metadata (DatasetMetadata | None, optional): The metadata for the dataset. Defaults to None.
            schema (DatasetSchema | None, optional): The schema for the dataset. Defaults to None.
            automatic_dtype_definition (bool, optional): Whether to automatically define data types. Use most applicable dtypes based on the data. Defaults to True.
        """
        # Process data first, then initialize parent with processed data
        self.data = data
        self.__process_data()
        self.metadata = (
            metadata
            if metadata is not None
            else DatasetMetadata.from_dataframe(data)
        )
        self.automatic_dtype_definition = automatic_dtype_definition
        self.schema = (
            schema
            if schema is not None
            else SchemaDetector().create_schema(data)
        )
        if self.automatic_dtype_definition:
            self.data, self.schema = (
                SchemaDetector().apply_automatic_dtype_logic(
                    self.data,
                    schema=self.schema,
                )
            )


    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
    ):
        metadata = DatasetMetadata.from_dataframe(df)
        schema = SchemaDetector().create_schema(df)
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

    def modify_column_schema(
        self,
        column: str,
        new_dtype: Literal["int64", "float64", "category", "string"],
    ):
        """
        Modify the schema of a specific column and update the dataset accordingly.
        Args:
            column: Column name to modify
            new_dtype: Target datatype (e.g., 'int64', 'float64', 'category', 'string')
        """
        modified_df, updated_schema = SchemaDetector().modify_column_dtype(
            self.data,
            column,
            new_dtype,
            self.schema,
        )
        self.data = modified_df
        self.schema = updated_schema
        return self

    def get_validations(self):
        self.validations = ValidationReport().validate_dataset(
            dataframe=self.data, schema=self.schema
        )
        return self

    def generate_report(self):
        if self.validations is None:
            self.get_validations()

        return self.validations.generate_report(self.metadata)

