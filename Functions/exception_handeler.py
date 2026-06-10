#Libraries
import pandas as pd
import traceback
import logging


class ExceptionLogger():
    
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        logging.basicConfig(filename=log_file_path, level=logging.ERROR, 
                            format='%(asctime)s - %(levelname)s - %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S', filemode='a')
        
    def error_logger(self, error):
        logging.error("An error occurred: %s", error)
        logging.error("Traceback details:\n%s", traceback.format_exc())

class Logger():
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        logging.basicConfig(filename=log_file_path, level=logging.NOTSET, 
                                format='%(asctime)s - %(levelname)s - %(message)s', 
                                filemode='a')
        
    def info_logger(self, error):
        logging.error("An error occurred: %s", error)
        logging.error("Traceback details:\n%s", traceback.format_exc())
        
    
    def actions_logger(self, error):
        logging.error("An error occurred: %s", error)
        logging.error("Traceback details:\n%s", traceback.format_exc())
        
    def debug_logger(self, error):
        logging.error("An error occurred: %s", error)
        logging.error("Traceback details:\n%s", traceback.format_exc())


#Functions

def replace_with (element):
    chars_a = [":", "+", "-", "<", ">", "(", ")", "[", "]"]
    chars_b = ["/", ".", ",", "-", "  ", " "]
def replace_with(element):
    chars_a = [':', '+', '-', '<', '>', '(', ')', '[', ']']
    chars_b = ['/', '.', ',', '-', '  ', ' ']
    #first set of replace
    for char in chars_a:
        if char in element:
            element = element.replace(char, "")
    #second set of replace
    for char in chars_b:
        if char in element:
            element = element.replace(char, "_")
    return element

def standard_name(names):
    if isinstance(names, list):
        lista= []
        for name in names:
            replaced_name = replace_with(name)
            lista.append(replaced_name)
        return lista
    elif isinstance(names, str):
        name = replace_with(names)
        return name
    else:
        element = names.type()
        print(f"{element} type incorrect")

def name(name):
    if "ñ" in name:
        a = name.replace("ñ", "n")
        return str(a)
    else:
        return str(name)

def standard_dataframe(dataframe: pd.DataFrame):
    for column in dataframe.columns.tolist():
        dataframe.rename(columns={column: name(standard_name(column)).lower()}, 
                            inplace=True)
    return dataframe


def anova_categorial_dtypes(dataframe):
    for col in dataframe.columns:
        if (dataframe[col].dtype == str) or (str(dataframe[col].dtype) == "object"):
            dataframe[col] = dataframe[col].astype("category")
    return dataframe

#remove "_" so in the grafics or tables
def remove_under_score(name):
    if type(name) == str:
        name  = name.replace("_", " ")
        return str(name)
    else:
        return name

def check_all_floats(lst:list):
    try:
        for item in lst:
            if not isinstance(item, float):
                raise TypeError(f"Item {item} is not a float. \nAll items must be floats between 0.0 and 1.0")
    except TypeError as e:
        # Log the error with traceback
        ExceptionLogger(r'..\error.log').error_logger(e)
        raise


#check the columns for automatic analysis
def clasification_columns_check(dataframe, data_to_pull):
    check_definition_col = [col for col in dataframe.columns 
                            if col in ["Methodology", "Sample", "id", "Rep"]]
    columns_needed = { 
        "Repetibility":["Methodology","id", "Rep"],
        "Accuracy":["Methodology","Sample"],
        "Accuracy_w_rep":["Methodology","Sample", "Rep", "id"],
        "Methods_comp":["Methodology","Sample"]
    }
    if check_definition_col == columns_needed[data_to_pull]:
        print("Classification columns are OK")
    else:
        not_found_col = [col for col in columns_needed[data_to_pull] if col not in check_definition_col]
        print(f"Classification columns: {not_found_col}. Not found inside the columns of the dataframe.")

#variables columns
def check_variable_columns(dataframe, data_to_pull, variables, 
                            drop=False):
    columns_needed = { 
            "Repetibility":["Methodology","id", "Rep"],
            "Accuracy":["Methodology","Sample"],
            "Accuracy_w_rep":["Methodology","Sample", "Rep", "id"],
            "Methods_comp":["Methodology","Sample"]}

    check_clasiff_col = [col for col in dataframe.columns 
                            if col in columns_needed[data_to_pull]]
    rest_columns = [col for col in dataframe.columns if col not in check_clasiff_col]
    list_variable_missing = [col for col in variables if col not in rest_columns]
    if len(list_variable_missing) > 0:
        print(f"Variable list elements:{list_variable_missing}")
    dataframe_columns_not_used = [col for col in rest_columns if col not in variables]
    if len(dataframe_columns_not_used) > 0:
        print(f"Dataframe columns not used:{dataframe_columns_not_used}")
        if drop==True:
            dataframe.drop(columns=dataframe_columns_not_used, inplace=True)
            return dataframe
    return dataframe
