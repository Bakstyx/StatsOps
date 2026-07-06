from dataclasses import dataclass
from typing import List
import pandas as pd

from .schema import ColumnSchema, DatasetSchema
from .metadata import DatasetMetadata


@dataclass(slots=True)
class ColumnValidator:
    column_name: str
    column_empty: bool
    missing_values: int
    duplicate_rows: int
    constant_column: bool
    invalid_datatypes: bool
    infinite_values: int


@dataclass(slots=True)
class ColumnValidations:
    schema: ColumnSchema
    validation: ColumnValidator


@dataclass(slots=True)
class DatasetValidator:
    columns_validations: List[ColumnValidations]
    dataset_empty: bool


class ValidationReport:
    def __init__(self):
        pass

    def validate_column(
        self,
        column_name: str,
        column_data: pd.Series,
        column_schema: ColumnSchema,
    ) -> ColumnValidations:
        # Implement validation logic for the column based on the schema
        # Check for missing values, duplicates, constant columns, invalid datatypes, infinite values, etc.
        # Return a ColumnValidations object with the results and any messages
        column_validator = ColumnValidator(
            column_name=column_name,
            column_empty=column_data.empty,
            missing_values=column_data.isnull().sum(),
            duplicate_rows=column_data.duplicated().sum(),
            constant_column=column_data.nunique() == 1,
            invalid_datatypes=not pd.api.types.is_dtype_equal(
                column_data.dtype, column_schema.dtype
            ),
            infinite_values=(column_data == float("inf")).sum()
            + (column_data == float("-inf")).sum(),
        )

        return ColumnValidations(
            schema=column_schema,
            validation=column_validator
        )

    def validate_dataset(
        self,
        dataframe: pd.DataFrame,
        schema: DatasetSchema,
    ):
        columns_validations = []
        for column_schema in schema.columns:
            column_data = dataframe[column_schema.name]
            column_validation = self.validate_column(
                column_schema.name, column_data, column_schema
            )
            columns_validations.append(column_validation)

        dataset_empty = dataframe.empty

        self.validations = DatasetValidator(
            columns_validations=columns_validations,
            dataset_empty=dataset_empty,
        )
        #return self.validations
        return self

#######################################
#       REPORT COLUMNS VALIDATION    #
#######################################

    def report_metadata(self, metadata: DatasetMetadata) :
        report = []

        report.append("DATASET METADATA")
        report.append(f"Name: {metadata.name}")
        report.append(f"Description: {metadata.description}")
        report.append(f"Source: {metadata.source}")
        report.append(f"Author: {metadata.author}")
        report.append(f"Date Collected: {metadata.date_collected}")
        report.append(f"Version: {metadata.version}")
        report.append(f"Rows: {metadata.num_rows}, Columns: {metadata.num_columns}")
        report.append(f"Target Column: {metadata.target_column}")
        report.append(f"Groups Columns: {metadata.groups_columns}")

        return report


    def report_on_column(self, column_validation: ColumnValidations, is_target: bool=False, is_group: bool=False) -> List[str]:
        messages = []
        validation = column_validation.validation

        is_important_column = is_target or is_group
        code = "[CRITICAL]" if is_important_column else "[WARNING]"

        if validation.column_empty:
            messages.append(f"{code} Column '{validation.column_name}' is empty.")

        if validation.missing_values > 0:
            messages.append(
                f"{code} Column '{validation.column_name}' has {validation.missing_values} missing values."
            )
        if validation.duplicate_rows > 0:
            messages.append(
                f"[WARNING] Column '{validation.column_name}' has {validation.duplicate_rows} duplicate rows."
            )
        if validation.constant_column:
            messages.append(
                f"[WARNING] Column '{validation.column_name}' is constant."
            )
        if validation.invalid_datatypes:
            messages.append(
                f"{code} Column '{validation.column_name}' has invalid data types."
            )
        if validation.infinite_values > 0:
            messages.append(
                f"{code} Column '{validation.column_name}' has {validation.infinite_values} infinite values."
            )

        return messages


    def validate_target_column(self, dataset_empty: bool, metadata: DatasetMetadata) -> List[str]:
        messages = []
        if metadata.target_column:
            if dataset_empty is False:  # Only validate target column if dataset is not empty
                target_col = next(
                    (
                        col
                        for col in self.validations.columns_validations
                        if col.schema.name == metadata.target_column
                    ),
                    None,
                )
                messages.append(f"Validating target column '{metadata.target_column}'...")
                if target_col is None:
                    messages.append("[ERROR] Column return empty")
                    return messages
                else:
                    if target_col.schema.dtype not in ["int64", "float64"]:
                        messages.append(
                            f"[ERROR] Target column '{metadata.target_column}' must be numeric (int64 or float64)."
                        )
                    columns_report = self.report_on_column(
                        target_col, is_target=True, is_group=False)
                    messages.extend(columns_report)
        else:
            messages.append("[ERROR] No target column specified in metadata.")
        return messages


    def validate_groups_columns(self, dataset_empty: bool, metadata: DatasetMetadata) -> List[str]:
        messages = []
        if metadata.groups_columns:
            if dataset_empty is False:  # Only validate groups columns if dataset is not empty
                for group_col in metadata.groups_columns:
                    group_col_validation = next(
                        (
                            col
                            for col in self.validations.columns_validations
                            if col.schema.name == group_col
                        ),
                        None,
                    )
                    messages.append(f"Validating groups column '{group_col}'...")
                    if group_col_validation is None:
                        continue
                    else:
                        if group_col_validation.schema.dtype not in [
                            "category",
                            "string",
                        ]:
                            messages.append(
                                f"[WARNING] Target column '{metadata.target_column}' should be numeric ('category', 'string')."
                            )
                        columns_report = self.report_on_column(
                            group_col_validation, is_target=False, is_group=True)
                        messages.extend(columns_report)
        else:
            messages.append(
                "[ERROR] No target column specified in metadata."
            )
        return messages

    def generate_report(
        self,
        metadata: DatasetMetadata,
    ) -> str:
        if self.validations is None:
            return "No validation performed yet."

        report = []

        # Metadata header
        report.append("=" * 60)
        report.append("DATASET VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Dataset metadata information
        report.extend(self.report_metadata(metadata))
        report.append("")

        # Dataset level validations
        if self.validations.dataset_empty:
            report.append("[CRITICAL] The dataset is empty.")
            report.append("")

        # Column validations
        report.append("[COLUMN VALIDATIONS]")

        for column_validation in self.validations.columns_validations:
            if column_validation.schema.name == metadata.target_column:
                self.validate_target_column(dataset_empty=self.validations.dataset_empty, metadata=metadata)
            else:
                groups = metadata.groups_columns
                if groups is None:
                    raise TypeError("metadata.groups_columns is None")
                if column_validation.schema.name in groups:
                    self.validate_groups_columns(
                        dataset_empty=self.validations.dataset_empty,
                        metadata=metadata,
                    )
                else:
                    self.report_on_column(column_validation)
        report.append("")


        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

