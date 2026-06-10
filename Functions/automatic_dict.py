#data to automatic analysis

formulas={
    'Repetibility':'C(Rep)',
    'Accuracy':'C(Methodology)',
    'Accuracy_w_rep':'C(Methodology)+C(Sample)+C(Rep)+C(Methodology):C(Sample)',
    'Methods_comp': 'C(Methodology)'
}

variables={
    'Repetibility':['Rep'],
    'Accuracy':['Methodology'],
    'Accuracy_w_rep':['Methodology'],
    'Methods_comp':['Methodology']
}

plot_pair={
    'Repetibility':'Rep',
    'Accuracy':'Sample',
    'Accuracy_w_rep':'Sample',
    'Methods_comp':'Sample'
}

ds_diff_sub_index={
    'Repetibility':'id',
    'Accuracy':'Sample',
    'Accuracy_w_rep':'id',
    'Methods_comp':'Sample'
} # descritive stats colmun for subindex difference

ds_diff_bar_plot={
    'Repetibility':'Rep',
    'Accuracy':'Sample',
    'Accuracy_w_rep':'Sample', 
    'Methods_comp':'Sample'
}# column to use and visualize diferences

rv_limit_analysis = {
    'Accuracy':'R_Method',
    'Accuracy_w_rep':'R_Method',
}

merger_dict={
    'Repetibility':'id',
    'Accuracy':'Sample',
    'Accuracy_w_rep':'id',
    'Methods_comp':'Sample'
}

# selection of method
def rvalue_selector(dataframe, eval):
    if eval not in list(rv_limit_analysis.keys()):
        r_method = dataframe['Methodology'].unique().tolist()[0]
        print('''This evaluation has no method selected as Referenced method, 
                    the first methodology in the data will serve as such''')
        print(f'Method selected as referenced value was: {r_method}')
        return str(r_method)
    else:
        return rv_limit_analysis[eval]