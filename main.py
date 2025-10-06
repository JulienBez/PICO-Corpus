# taken from https://github.com/cuevascarlos/ClinicalTrials/blob/main/Preprocessing.ipynb

import sys, os
import pandas as pd
import numpy as np
from utils import *

sys.path.append("brat/tools")
sys.path.append("brat/server/src")
from brat.tools.anntoconll import main

#Read the text roots from the data folder
txt_files = ['data/'+file for file in os.listdir('data/') if file.endswith(".txt")]
#Run the brat tools on the text files to generate the conll files
main(['-']+txt_files) #The - is a dummy argument to make the brat tools work

data = {'File_ID': [], 'Entity': [], 'Start': [], 'End': [], 'Words': []}

#Read the root of .conll files
conll_files = sorted([file for file in os.listdir('./data/') if file.endswith(".conll")])

for file in conll_files:
    #Read the files
    file_path = os.path.join('./data/', file)
    with open(file_path,"r",encoding='utf-8') as f:
        lines = f.readlines()

        #Add the info of each line of 'file' to the data dict
        for line in lines:
            data['File_ID'].append(file.split('.')[0])
            line = line.split()
            if len(line)>0:
                data['Entity'].append(line[0])
                data['Start'].append(line[1])
                data['End'].append(line[2])
                data['Words'].append(line[3])
            else: #For blank lines
                data['Entity'].append(np.nan)
                data['Start'].append(np.nan)
                data['End'].append(np.nan)
                data['Words'].append(np.nan)

#Transform data dict into DataFrame
data_df = pd.DataFrame(data)

# Create list of sentences and counter
ls = []
counter = 1

for i in range(len(data_df)):
    # If the current line is not a sentence separator, we add the current counter to the list
    if ((pd.isna(data_df.Words[i]) == False) | (pd.isna(data_df.Entity[i]) == False)):
        ls.append(counter)
    # If the current line is a sentence separator, we add 0 to the list and increase the counter by 1
    if ((pd.isna(data_df.Words[i]) == True) & (pd.isna(data_df.Entity[i]) == True)):
        ls.append(0)
        counter += 1 
        
# We add the list to the dataframe        
data_df['Sentence_ID'] = ls

# Drop rows with data['Sentence_ID'] == 0 (blank lines)
data_df = data_df[data_df['Sentence_ID'] != 0]

#Confirm if there still exist any NaN values
data_df.isnull().sum()

#Confirm the type of each column
data_df.dtypes

#Change the type of the column 'Start' and 'End' to int
data_df['Start'] = data_df['Start'].astype(int)
data_df['End'] = data_df['End'].astype(int)

data_df.dtypes

#Save into csv file
data_df.to_csv('./DataProcessed/dataBIO_v3.csv', index=False)

#Create a copy of the dataframe
data2_df = data_df.copy()

#Drop the rows where the Entity is O because it is not an entity of interest
data2_df = data2_df[data2_df['Entity'] != 'O']

#Count values of the column 'Entity' that start with 'B-' because it determines the number of elements per entity
Freq = pd.DataFrame(data2_df['Entity'].value_counts())
#Drop the rows where the index starts with 'I-'
Freq = Freq[Freq.index.str.startswith('I-') == False]
Freq

#Add the number of fileID uniques where each label appears
Freq['n_files'] = data2_df.groupby('Entity')['File_ID'].nunique()

#Re-order the labels to be in the same order as in the paper mentioned
Freq = Freq.reindex(['B-total-participants', 'B-intervention-participants','B-control-participants', 'B-age', 'B-eligibility', 'B-ethinicity', 'B-condition', 'B-location', 'B-intervention', 'B-control', 'B-outcome', 'B-outcome-Measure', 'B-iv-bin-abs', 'B-cv-bin-abs', 'B-iv-bin-percent', 'B-cv-bin-percent', 'B-iv-cont-mean', 'B-cv-cont-mean', 'B-iv-cont-median', 'B-cv-cont-median', 'B-iv-cont-sd', 'B-cv-cont-sd', 'B-iv-cont-q1', 'B-cv-cont-q1', 'B-iv-cont-q3', 'B-cv-cont-q3'])

#Sum the values of the column 'count'
print(f'Total number of entities: {Freq["count"].sum()}') #Article: 17739
#-1 because i didn't fix the overlapping annotation mentionned by the authors