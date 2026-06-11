from dataclasses import dataclass
from datetime import datetime



@dataclass(slots=True)
class DatasetMetadata:
    name: str
    description: str
    source: str
    date_collected: datetime
    groups_columns: list
    target_column: str
    time_column: str | None = None
    version: str | None = None
    num_rows: int | None = None
    num_columns: int | None = None
    column_types: dict | None = None



    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, 
                       name: str = "Unknown",
                       description: str = "No description", source: str = "Unknown", date_collected: datetime = datetime.now(), groups_columns: list = [], target_column: str = "", time_column: str | None = None, version: str | None = None):
        return cls(
            name=name,
            description=description,
            source=source,
            date_collected=date_collected,
            groups_columns=groups_columns,
            target_column=target_column,
            time_column=time_column,
            version=version,
            num_rows=df.shape[0],
            num_columns=df.shape[1],
            column_types={col: str(df[col].dtype) for col in df.columns}
        )