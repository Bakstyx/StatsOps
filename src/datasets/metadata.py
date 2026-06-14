from dataclasses import dataclass
from datetime import datetime

import pandas as pd



@dataclass(slots=True)
class DatasetMetadata:
    name: str
    description: str
    source: str
    date_collected: str
    groups_columns: list
    target_column: str
    time_column: str | None = None
    version: str | None = None
    num_rows: int | None = None
    num_columns: int | None = None
    column_types: dict | None = None

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        target_column: str,
        groups_columns: list,
        name: str = "Unknown",
        description: str = "No description",
        source: str = "Unknown",
        time_column: str | None = None,
        version: str | None = None,
    ):
        """Create DatasetMetadata from a DataFrame and additional information.

        Args:
            df (pd.DataFrame): _description_
            target_column (str): _description_
            groups_columns (list): _description_
            name (str, optional): _description_. Defaults to "Unknown".
            description (str, optional): _description_. Defaults to "No description".
            source (str, optional): _description_. Defaults to "Unknown".
            time_column (str | None, optional): _description_. Defaults to None.
            version (str | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        return cls(
            name=name,
            description=description,
            source=source,
            date_collected=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            groups_columns=groups_columns,
            target_column=target_column,
            time_column=time_column,
            version=version,
            num_rows=df.shape[0],
            num_columns=df.shape[1],
            column_types={
                col: str(df[col].dtype) for col in df.columns
            },
        )

    @classmethod
    def update(cls, **kwargs):
        """ Update metadata attributes.
        Args:
            **kwargs: Attribute names and values to update.
            Valid attributes: name, description, source,
                date_collected, groups_columns, target_column,
                time_column, version, num_rows, num_columns, column_types
        Raises:
            AttributeError: If an invalid attribute is provided.
        """
        valid_attributes = {
            "name", "description", "source",
            "groups_columns", "target_column",
            "time_column", "version"
        }

        for key, value in kwargs.items():
            if key not in valid_attributes:
                raise AttributeError(f"Invalid attribute: {key}")
            setattr(cls, key, value)


