import pandas as pd
from typing import Literal
from src.datasets.schema import ColumnSchema, DatasetSchema


class SchemaDetector:
    """Class responsible for detecting and modifying the schema of a dataset, including automatic dtype definition based on categorical attributes.
    This class provides methods to create a schema from a DataFrame, modify column data types, and apply automatic dtype logic based on the categorical attribute of columns in the schema.
    Methods:
        create_schema(dataframe: pd.DataFrame) -> DatasetSchema:
            Creates a DatasetSchema from a given DataFrame by analyzing each column's properties.
        modify_column_dtype(dataframe: pd.DataFrame, column: str, new_dtype: Literal["int64", "float64", "category", "string"], schema: DatasetSchema) -> tuple[pd.DataFrame, DatasetSchema]:
            Modifies the data type of a specific column in the DataFrame and updates the corresponding schema.
        apply_automatic_dtype_logic(dataframe: pd.DataFrame, schema: DatasetSchema) -> tuple[pd.DataFrame, DatasetSchema]:
            Applies automatic dtype conversion logic based on the categorical attribute in the schema, converting columns marked as categorical to 'category' dtype and regenerating the schema accordingly.
    """
    def __init__(self):
        pass

    def __set_column_schema__(self, dataframe: pd.DataFrame, column: str) -> ColumnSchema:
        return ColumnSchema(
            name=column,
            dtype=str(dataframe[column].dtype),
            categorical=(
                dataframe[column].nunique() / len(dataframe[column])
            )
            < 0.2,
            nullable=bool(dataframe[column].isnull().any()),
            nunique_values=dataframe[column].nunique(),
            value_counts=len(dataframe[column]),
            unique=bool(dataframe[column].is_unique),
            unique_values=(
                dataframe[column].unique().tolist()
                if dataframe[column].nunique() < 10
                else None
            ),
        )

    def create_schema(self, dataframe: pd.DataFrame):
        columns_schema = []
        for col in dataframe.columns:
            column_schema = self.__set_column_schema__(dataframe, col)
            columns_schema.append(column_schema)
        return DatasetSchema(columns=columns_schema)



    def modify_column_dtype(
        self,
        dataframe: pd.DataFrame,
        column: str,
        new_dtype: Literal["int64", "float64", "category", "string"],
        schema: DatasetSchema,
    ) -> tuple[pd.DataFrame, DatasetSchema]:
        """
        Modify the datatype of a specific column and update the schema.
        Args:
            dataframe: The input dataframe
            column: Column name to modify
            new_dtype: Target datatype (e.g., 'int64', 'float64', 'category', 'string')
            schema: Current DatasetSchema
        Returns:
            Tuple of (modified_dataframe, updated_schema)
        """
        if column not in dataframe.columns:
            raise ValueError(
                f"Column '{column}' not found in dataframe"
            )

        # Convert dataframe column to new dtype
        try:
            modified_df = dataframe.copy()
            modified_df[column] = modified_df[column].astype(
                new_dtype
            )
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert column '{column}' to dtype '{new_dtype}': {str(e)}"
            ) from e

        # Update schema
        updated_columns = []
        for col_schema in schema.columns:
            if col_schema.name == column:
                updated_col_schema = self.__set_column_schema__(modified_df, column)
                updated_columns.append(updated_col_schema)
            else:
                updated_columns.append(col_schema)

        updated_schema = DatasetSchema(columns=updated_columns)
        return modified_df, updated_schema

    def apply_automatic_dtype_logic(
        self, dataframe: pd.DataFrame, schema: DatasetSchema
    ) -> tuple[pd.DataFrame, DatasetSchema]:
        """
        Apply dtype conversion logic based on schema's categorical attribute.
        Converts columns marked as categorical to 'category' dtype and regenerates schema.

        Args:
            dataframe: The input dataframe
            schema: The DatasetSchema to use for determining which columns should be categorical

        Returns:
            Tuple of (modified_dataframe, updated_schema)
        """
        modified_df = dataframe.copy()

        # Apply dtype conversions based on schema's categorical attribute
        for col_schema in schema.columns:
            if col_schema.categorical:
                try:
                    modified_df[col_schema.name] = modified_df[
                        col_schema.name
                    ].astype("category")
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"Cannot convert column '{col_schema.name}' to categorical dtype: {str(e)}"
                    ) from e

        # Regenerate schema for the modified dataframe
        new_schema = self.create_schema(modified_df)

        return modified_df, new_schema
