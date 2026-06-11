from dataclasses import dataclass




@dataclass(slots=True)
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool
    nunique_values: int
    unique: bool


@dataclass(slots=True)
class DatasetSchema:
    columns: list[ColumnSchema]



