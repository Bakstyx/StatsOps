from dataclasses import dataclass
import pandas as pd


@dataclass(slots=True)
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool
    nunique_values: int
    unique: bool
    unique_values: list | None
    value_counts: int | None

@dataclass(slots=True)
class DatasetSchema:
    columns: list[ColumnSchema]


class SchemaDetector:
    def __init__(self):
        pass

    def detect_schema(self, dataframe: pd.DataFrame):
        columns_schema = []
        for col in dataframe.columns:
            column_schema = ColumnSchema(
                name=col,
                dtype=str(dataframe[col].dtype),
                nullable=bool(dataframe[col].isnull().any()),
                nunique_values=dataframe[col].nunique(),
                value_counts=len(dataframe[col]),
                unique=bool(dataframe[col].is_unique),
                unique_values=dataframe[col].unique().tolist()
                if dataframe[col].nunique() < 10
                else None,
            )
            columns_schema.append(column_schema)
        return DatasetSchema(columns=columns_schema)
