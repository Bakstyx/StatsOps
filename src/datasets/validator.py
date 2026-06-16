from dataclasses import dataclass
from typing import Any, Dict, List, Optional
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
    messages: List[str]


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

        messages = []
        if column_validator.column_empty:
            messages.append(f"Column '{column_name}' is empty.")
        if column_validator.missing_values > 0:
            messages.append(
                f"Column '{column_name}' has {column_validator.missing_values} missing values."
            )
        if column_validator.duplicate_rows > 0:
            messages.append(
                f"Column '{column_name}' has {column_validator.duplicate_rows} duplicate rows."
            )
        if column_validator.constant_column:
            messages.append(f"Column '{column_name}' is constant.")
        if column_validator.invalid_datatypes:
            messages.append(
                f"Column '{column_name}' has invalid data types."
            )
        if column_validator.infinite_values > 0:
            messages.append(
                f"Column '{column_name}' has {column_validator.infinite_values} infinite values."
            )

        return ColumnValidations(
            schema=column_schema,
            validation=column_validator,
            messages=messages,
        )

    def validate_dataset(
        self,
        dataframe: pd.DataFrame,
        schema: DatasetSchema,
    ) -> DatasetValidator:
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

        return self.validations

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
                    messages.append(
                        f"[ERROR] Target column '{metadata.target_column}' not found in dataset."
                    )
                else:
                    if target_col.schema.dtype not in ["int64", "float64"]:
                        messages.append(
                            f"[ERROR] Target column '{metadata.target_column}' must be numeric (int64 or float64)."
                        )
                    if target_col.validation.column_empty:
                        messages.append(
                            f"[CRITICAL] Target column '{metadata.target_column}' is empty."
                        )
                    if target_col.validation.missing_values > 0:
                        messages.append(
                            f"[CRITICAL] Target column '{metadata.target_column}' has {target_col.validation.missing_values} missing values."
                        )
                    if target_col.validation.duplicate_rows > 0:
                        messages.append(
                            f"[WARNING] Target column '{metadata.target_column}' has {target_col.validation.duplicate_rows} duplicate rows."
                        )
                    if target_col.validation.constant_column:
                        messages.append(
                            f"[WARNING] Target column '{metadata.target_column}' is constant."
                        )
                    if target_col.validation.invalid_datatypes:
                        messages.append(
                            f"[ERROR] Target column '{metadata.target_column}' has invalid data types."
                        )
        else:
            messages.append("[CRITICAL] No target column specified in metadata.")
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
                        messages.append(
                            f"[ERROR] Groups column '{group_col}' not found in dataset."
                        )
                    else:
                        if group_col_validation.validation.column_empty:
                            messages.append(
                                f"[CRITICAL] Groups column '{group_col}' is empty."
                            )
                        if group_col_validation.validation.missing_values > 0:
                            messages.append(
                                f"[CRITICAL] Groups column '{group_col}' has {group_col_validation.validation.missing_values} missing values."
                            )
                        #! WIP

        return messages

    def generate_report(
        self,
        metadata: DatasetMetadata,
        #dataframe: pd.DataFrame | None = None,
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
        has_column_issues = False

        for column_validation in self.validations.columns_validations:
            if column_validation.messages:
                has_column_issues = True
                report.append(f"\nColumn: {column_validation.schema.name}")
                report.extend(column_validation.messages)

        if not has_column_issues:
            report.append("✓ All columns passed validation.")

        report.append("")

        # Special columns validation (groups_columns and target_column)
        if self.validations.dataset_empty is False:  # Only validate special columns if dataset is not empty
            report.append("[SPECIAL COLUMNS VALIDATION]")
            special_validation = self.validate_special_columns(
                self.columns_validations.dataset_empty, metadata
            )

            has_special_issues = (
                special_validation["errors"]
                or special_validation["warnings"]
            )

            if special_validation["errors"]:
                report.append("[ERRORS]")
                report.extend(special_validation["errors"])
                report.append("")

            if special_validation["warnings"]:
                report.append("[WARNINGS]")
                report.extend(special_validation["warnings"])
                report.append("")

            if not has_special_issues:
                report.append("✓ All special columns passed validation.")
                report.append("")

            # Groups columns info
            if metadata.groups_columns:
                report.append(f"Groups Columns: {metadata.groups_columns}")
            else:
                report.append("Groups Columns: None")

            # Target column info
            if metadata.target_column:
                report.append(f"Target Column: {metadata.target_column}")
            else:
                report.append("Target Column: None")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
