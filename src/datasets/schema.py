from dataclasses import dataclass
from tabulate import tabulate

@dataclass(slots=True)
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool
    nunique_values: int
    unique: bool
    categorical: bool
    unique_values: list | None
    value_counts: int | None

@dataclass(slots=True)
class DatasetSchema:
    columns: list[ColumnSchema]

    def __repr__(self):
        return tabulate(
            [[col.name, col.dtype, col.nullable, col.nunique_values, col.unique, col.categorical, col.unique_values, col.value_counts] for col in self.columns],
            headers=["Column Name", "Data Type", "Nullable", "Unique Values Count", "Is Unique", "Is Categorical", "Unique Values (if <10)", "Total Values"],
            tablefmt="grid"
        )



