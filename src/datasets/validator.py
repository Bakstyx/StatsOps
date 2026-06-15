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
        self.columns_validations: DatasetValidator | None = None

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

        self.columns_validations = DatasetValidator(
            columns_validations=columns_validations,
            dataset_empty=dataset_empty,
        )

        return self.columns_validations

#######################################
#       SPECIAL COLUMNS VALIDATION    #
#######################################


    def _is_valid_categorical_type(self, column_data: pd.Series) -> bool:
        """Check if column is str or categorical type."""
        col_dtype = column_data.dtype
        return (
            col_dtype == "object"
            or col_dtype == "category"
            or pd.api.types.is_string_dtype(column_data)
        )

    def _is_valid_numeric_or_categorical_type(
        self, column_data: pd.Series
    ) -> bool:
        """Check if column is numeric or categorical type."""
        is_numeric = pd.api.types.is_numeric_dtype(column_data)
        is_valid_categorical = self._is_valid_categorical_type(
            column_data
        )
        return is_numeric or is_valid_categorical

    def _check_empty_values(
        self,
        column_data: pd.Series,
        column_name: str,
        context: str = "Column",
    ) -> tuple[list, list]:
        """
        Check for null/empty values in a column.

        Args:
            column_data: The column data to check.
            column_name: Name of the column for error messages.
            context: Context prefix for messages (e.g., 'groups_columns', 'target_column').

        Returns:
            Tuple of (errors, warnings) lists.
        """
        errors = []
        warnings = []

        if column_data.isna().all():
            errors.append(
                f"{context}: {column_name} contains all empty/null values"
            )
        elif column_data.isna().sum() > 0:
            warnings.append(
                f"{context}: {column_name} has {column_data.isna().sum()} null values"
            )

        return errors, warnings

    def _check_categorical_empty_strings(
        self, column_data: pd.Series, column_name: str, context: str = "Column"
    ) -> list:
        """
        Check for empty strings in categorical columns.

        Args:
            column_data: The column data to check.
            column_name: Name of the column for error messages.
            context: Context prefix for messages.

        Returns:
            List of warning messages.
        """
        warnings = []

        if column_data.dtype == "object":
            empty_strings = (column_data == "").sum()
            if empty_strings > 0:
                warnings.append(
                    f"{context}: {column_name} contains {empty_strings} empty strings"
                )

        return warnings

    def _check_numeric_inf_values(
        self, column_data: pd.Series, column_name: str, context: str = "Column"
    ) -> list:
        """
        Check for infinite values in numeric columns.

        Args:
            column_data: The column data to check.
            column_name: Name of the column for error messages.
            context: Context prefix for messages.

        Returns:
            List of error messages.
        """
        errors = []

        if pd.api.types.is_numeric_dtype(column_data):
            inf_count = (column_data == float("inf")).sum() + (
                column_data == float("-inf")
            ).sum()
            if inf_count > 0:
                errors.append(
                    f"{context}: {column_name} contains {inf_count} inf/-inf values"
                )

        return errors

    def _validate_groups_columns(
        self, dataframe: pd.DataFrame, groups_columns: list | None
    ) -> tuple[list, list]:
        """
        Validate groups_columns specification.

        Args:
            dataframe: DataFrame to validate against.
            groups_columns: List of column names to validate.

        Returns:
            Tuple of (errors, warnings) lists.
        """
        errors = []
        warnings = []

        if groups_columns is None:
            return errors, warnings

        if not isinstance(groups_columns, list):
            errors.append(
                f"groups_columns must be a list, got {type(groups_columns)}"
            )
            return errors, warnings

        for col in groups_columns:
            # Check column exists
            if col not in dataframe.columns:
                errors.append(
                    f"groups_columns: Column '{col}' not found in DataFrame"
                )
                continue

            col_data = dataframe[col]
            col_dtype = col_data.dtype

            # Check data type
            if not self._is_valid_categorical_type(col_data):
                errors.append(
                    f"groups_columns: Column '{col}' has dtype {col_dtype}, must be str or categorical"
                )

            # Check for empty values
            col_errors, col_warnings = self._check_empty_values(
                col_data, f"'{col}'", context="groups_columns"
            )
            errors.extend(col_errors)
            warnings.extend(col_warnings)

            # Check for empty strings
            col_warnings = self._check_categorical_empty_strings(
                col_data, f"'{col}'", context="groups_columns"
            )
            warnings.extend(col_warnings)

        return errors, warnings

    def _validate_target_column(
        self, dataframe: pd.DataFrame, target_column: str | None
    ) -> tuple[list, list]:
        """
        Validate target_column specification.

        Args:
            dataframe: DataFrame to validate against.
            target_column: Column name to validate.

        Returns:
            Tuple of (errors, warnings) lists.
        """
        errors = []
        warnings = []

        if target_column is None:
            return errors, warnings

        if not isinstance(target_column, str):
            errors.append(
                f"target_column must be a string, got {type(target_column)}"
            )
            return errors, warnings

        # Check column exists
        if target_column not in dataframe.columns:
            errors.append(
                f"target_column: Column '{target_column}' not found in DataFrame"
            )
            return errors, warnings

        col_data = dataframe[target_column]
        col_dtype = col_data.dtype

        # Check data type
        if not self._is_valid_numeric_or_categorical_type(col_data):
            errors.append(
                f"target_column: Column '{target_column}' has dtype {col_dtype}, must be numeric or categorical"
            )

        # Check for empty values
        col_errors, col_warnings = self._check_empty_values(
            col_data, f"'{target_column}'", context="target_column"
        )
        errors.extend(col_errors)
        warnings.extend(col_warnings)

        # Check for inf values
        col_errors = self._check_numeric_inf_values(
            col_data, f"'{target_column}'", context="target_column"
        )
        errors.extend(col_errors)

        # Check for empty strings
        col_warnings = self._check_categorical_empty_strings(
            col_data, f"'{target_column}'", context="target_column"
        )
        warnings.extend(col_warnings)

        return errors, warnings

    def validate_special_columns(
        self, dataframe: pd.DataFrame, metadata: DatasetMetadata
    ) -> Dict[str, List[str]]:
        """
        Validate groups_columns and target_column against DataFrame requirements.

        Validation rules:
        - groups_columns: Must be str or categorical (object/category dtype) with non-empty values
        - target_column: Must be numeric or categorical with non-empty values and no inf values

        Args:
            dataframe (pd.DataFrame): The DataFrame to validate against.
            metadata (DatasetMetadata): The metadata containing column specifications.

        Returns:
            Dict with 'errors' and 'warnings' lists.
        """
        errors = []
        warnings = []

        # Validate groups_columns
        col_errors, col_warnings = self._validate_groups_columns(
            dataframe, metadata.groups_columns
        )
        errors.extend(col_errors)
        warnings.extend(col_warnings)

        # Validate target_column
        col_errors, col_warnings = self._validate_target_column(
            dataframe, metadata.target_column
        )
        errors.extend(col_errors)
        warnings.extend(col_warnings)

        return {"errors": errors, "warnings": warnings}

    def generate_report(
        self,
        metadata: DatasetMetadata,
        dataframe: pd.DataFrame | None = None,
    ) -> str:
        if self.columns_validations is None:
            return "No validation performed yet."

        report = []

        # Metadata header
        report.append("=" * 60)
        report.append("DATASET VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Dataset metadata information
        report.append("[DATASET INFORMATION]")
        report.append(f"Name: {metadata.name}")
        report.append(f"Description: {metadata.description}")
        report.append(f"Source: {metadata.source}")
        report.append(f"Author: {metadata.author}")
        report.append(f"Date Collected: {metadata.date_collected}")
        report.append(f"Version: {metadata.version}")
        report.append(f"Rows: {metadata.num_rows}, Columns: {metadata.num_columns}")
        report.append("")

        # Dataset level validations
        if self.columns_validations.dataset_empty:
            report.append("[CRITICAL] The dataset is empty.")
            report.append("")

        # Column validations
        report.append("[COLUMN VALIDATIONS]")
        has_column_issues = False

        for column_validation in self.columns_validations.columns_validations:
            if column_validation.messages:
                has_column_issues = True
                report.append(f"\nColumn: {column_validation.schema.name}")
                report.extend(column_validation.messages)

        if not has_column_issues:
            report.append("✓ All columns passed validation.")

        report.append("")

        # Special columns validation (groups_columns and target_column)
        if dataframe is not None:
            report.append("[SPECIAL COLUMNS VALIDATION]")
            special_validation = self.validate_special_columns(
                dataframe, metadata
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
