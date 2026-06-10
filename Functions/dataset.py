### Libs
import pandas as pd
import numpy as np
import random
from tabulate import tabulate

### Scripts
from Functions.exception_handeler import standard_dataframe


class Dataset(pd.DataFrame):
    
    def __init__(self, data):
        super().__init__(data)
        self.data = standard_dataframe(data)
    
    def get_shape(self):
        return self.shape
    
    def get_columns_types(self):
        dict_type =  {}
        for col in self.get_columns_names():
            dict_type[col] = str(self[col].dtypes).replace('dtype', '')
        return dict_type
    
    def get_info_resume(self):
        return self.info(verbose=False)
    
    def get_dataset_info(self, complete=True, to_file=False):
        dataframe = {}
        #Generation of dataset info
        dataframe['Column'] = self.columns
        dataframe['Rows'] = [len(self[col]) for col in self.columns]
        dataframe['Null values'] = [len(self[col].isnull().loc[lambda x : x==True]) 
                                        for col in self.columns]
        dataframe['Dtypes'] = [self[col].dtypes for col in self.columns]
        if complete:
            dataframe['Inf values'] = [len(self[col].loc[lambda x : (x==np.inf) | (x==-np.inf)])   
                                        for col in self.columns]
            dataframe['NA values'] = [len(self[col].loc[lambda x : (x=='NA') | (x=='') | (x==' ')]) 
                                        for col in self.columns]
            dataframe['Duplicates'] = [len(self[col].duplicated().loc[lambda x : x==True]) 
                                    for col in self.columns]
            dataframe['Categorized'] = ['Yes'
                                        if (len(self[col].unique())/len(self[col]))<=0.1 
                                        else 'No'  
                                        for col in self.columns]
        
        dataframe = pd.DataFrame(data=dataframe)
        if to_file:
            print(tabulate(dataframe, headers=dataframe.columns, 
                            tablefmt = 'grid'))
        return dataframe
    
    def __check_balanced_dataset__(self, classifier, verbose=False):
        data_count = self.groupby(by=classifier, group_keys=False, as_index=False).size()
        if (True in list(self.duplicated())) or (len(data_count['size'].unique())>1):
            if verbose:
                print("There is duplicated rows in the dataset or is unbalanced. \nPlease check the data")
            return data_count, "Fix"
        else:
            if verbose:
                print('No duplicated rows, and dataset is balanced. \nData is OK')
            return data_count, "No"
    
    def get_balanced_dataset(self, classifier, verbose=False):
        check = self.__check_balanced_dataset__(classifier, verbose)
        if check[1] == "Fix":
            return self.random_sampling(sampling_column=classifier, 
                                        sample_size=check[0]['size'].min(), verbose=verbose )
        else:
            return self
    
    def random_sampling(self:pd.DataFrame, sampling_column:str, 
                        sample_size:int, verbose=False):
        df = pd.DataFrame()
        for sampler in list(self[sampling_column].unique()):
            if len(self[self[sampling_column]==sampler])>=sample_size:
                df = pd.concat([df, self[self.index.isin(random.sample(
                        list(self[self[sampling_column]==sampler].index.values), 
                        k=sample_size))]])
            else:
                df = pd.concat([df, self[self.index.isin(random.sample(
                        list(self[self[sampling_column]==sampler].index.values), 
                        k=len(self[self[sampling_column]==sampler])))]])
                if verbose:
                    print(f"""Warning: Sample size for {sampler} is less than {sample_size}.
                        \nSample size is set to {len(self[self[sampling_column]==sampler])}.""")
        return df
    
    def random_class_sampling(self:pd.DataFrame, class_sampling:str,
                        sampling_column:str, sample_size:int, verbose=False):
        df = pd.DataFrame()
        samples = list(self[sampling_column].unique())
        if len(samples)>=sample_size:
            sample_list = random.sample(samples, k=sample_size)
        else:
            sample_list = samples
            if verbose:
                print(f"""Warning: Sample size for {sampling_column} is less than {sample_size}.
                    \nSample size is set to {len(samples)}.""")
        for sampler in list(self[class_sampling].unique()):
            df = pd.concat([df, self[(self[class_sampling]==sampler)&(self[sampling_column].isin(sample_list))]])
        return df

