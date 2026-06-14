import pandas as pd
from typing import Literal
from src.datasets.schema import ColumnSchema, DatasetSchema


class SchemaDetector:
    def __init__(self):
        pass

    def detect_schema(self, dataframe: pd.DataFrame):
        columns_schema = []
        for col in dataframe.columns:
            column_schema = ColumnSchema(
                name=col,
                dtype=str(dataframe[col].dtype),
                categorical=(
                    dataframe[col].nunique() / len(dataframe[col])
                )
                < 0.2,
                nullable=bool(dataframe[col].isnull().any()),
                nunique_values=dataframe[col].nunique(),
                value_counts=len(dataframe[col]),
                unique=bool(dataframe[col].is_unique),
                unique_values=(
                    dataframe[col].unique().tolist()
                    if dataframe[col].nunique() < 10
                    else None
                ),
            )
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

        # Update schema for the modified column
        updated_columns = []
        for col_schema in schema.columns:
            if col_schema.name == column:
                updated_col_schema = ColumnSchema(
                    name=col_schema.name,
                    dtype=str(modified_df[column].dtype),
                    categorical=(
                        modified_df[column].nunique()
                        / len(modified_df[column])
                    )
                    < 0.2,
                    nullable=bool(modified_df[column].isnull().any()),
                    nunique_values=modified_df[column].nunique(),
                    value_counts=len(modified_df[column]),
                    unique=bool(modified_df[column].is_unique),
                    unique_values=(
                        modified_df[column].unique().tolist()
                        if modified_df[column].nunique() < 10
                        else None
                    ),
                )
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
        new_schema = self.detect_schema(modified_df)

        return modified_df, new_schema
