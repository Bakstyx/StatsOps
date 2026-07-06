from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass(slots=True)
class DatasetMetadata:
    name: str
    description: str
    source: str
    author: str
    date_collected: str
    groups_columns: list[str] | None = None
    target_column: str | None = None
    time_column: str | None = None
    version: str | None = None
    num_rows: int | None = None
    num_columns: int | None = None
    column_types: dict | None = None

    @classmethod
    def from_dataframe(
        cls,
        data : pd.DataFrame,
        name: str = "Unknown",
        description: str = "No description",
        source: str = "Unknown",
        author: str = "Unknown",
        target_column: str | None = None,
        groups_columns: list | None = None,
        time_column: str | None = None,
        version: str | None = None,
    ):
        """
        Create DatasetMetadata from a DataFrame and additional information.
        Args:
            df (pd.DataFrame): The DataFrame to extract metadata from.
            target_column (str | None): The column name of the target variable. Defaults to None.
            groups_columns (list | None): A list of column names to group by. Defaults to None.
            name (str, optional): The name of the dataset. Defaults to "Unknown".
            description (str, optional): A description of the dataset. Defaults to "No description".
            source (str, optional): The source of the dataset. Defaults to "Unknown".
            time_column (str | None, optional): The column name for the time variable. Defaults to None.
            version (str | None, optional): The version of the dataset. Defaults to None.
        Returns:
            DatasetMetadata: The created DatasetMetadata instance.
        """
        return cls(
            name=name,
            description=description,
            source=source,
            author=author,
            date_collected=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            groups_columns=groups_columns,
            target_column=target_column,
            time_column=time_column,
            version=version,
            num_rows=data.shape[0],
            num_columns=data.shape[1],
            column_types={
                col: str(data[col].dtype) for col in data.columns
            },
        )

    @classmethod
    def update(cls, **kwargs):
        """
        Update metadata attributes.
        Args:
            **kwargs: Attribute names and values to update.
            Valid attributes: name, description, source,
                date_collected, groups_columns, target_column,
                time_column, version, num_rows, num_columns, column_types
        Raises:
            AttributeError: If an invalid attribute is provided.
        """

        valid_attributes = {
            "name",
            "description",
            "source",
            "author",
            "groups_columns",
            "target_column",
            "time_column",
            "version",
        }

        for key, value in kwargs.items():
            if key not in valid_attributes:
                raise AttributeError(f"Invalid attribute: {key}")
            setattr(cls, key, value)


    def asdict(self):
        """
        Convert the DatasetMetadata instance to a dictionary.
        Returns:
            dict: A dictionary representation of the DatasetMetadata instance.
        """
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "date_collected": self.date_collected,
            "groups_columns": self.groups_columns,
            "target_column": self.target_column,
            "time_column": self.time_column,
            "version": self.version,
            "num_rows": self.num_rows,
            "num_columns": self.num_columns,
            "column_types": self.column_types,
        }
