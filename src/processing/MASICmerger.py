from src.processing.MSGFplusMerger import MSGFplusMerger
from utility.utils import timeit

import os
import pandas as pd
import fnmatch

class MASICmerger(MSGFplusMerger):
    '''Run for each dataset
    '''
    def __init__(self, folder):
        self.parent_folder = folder
        self.MSGFjobs_MASIC_resultant=None
        self.file_pattern_types = {"masic": "{}SICstats.txt"}
        self.masic=[]

    @timeit
    def merge_msgfplus_msaic(self, MSGF_df ):
        '''
        1. Read in the MASIC job:
            "*_SICstats.txt" in masic_DF with added JobNum column
        2. Inner-join:
                MSGFjobs_Merged   and
                masic_DF.FragScanNumber
             over
                JobNum <--> JobNum
                Scan <-->FragScanNumber
        3. create MSGFjobs_MASIC_resultant  dataframe.
        '''
        masic_folder = os.path.join(self.parent_folder, 'MASICjob')

        for cur_path, directories, files in os.walk(masic_folder):
            for file in files:
                if fnmatch.fnmatch(file, self.file_pattern_types["masic"].format('*')):
                    self.masic.append(os.path.join(cur_path, file))
        try:
            masic_DF= pd.read_csv(self.masic[0], sep='\t')
        except Exception as e:
            print("MASIC has multiple files!")
        masic_DF= masic_DF.rename(columns={'FragScanNumber': 'Scan'})

        self.MSGFjobs_MASIC_resultant = pd.merge(MSGF_df, masic_DF, how='left', left_on=['Scan'], right_on=['Scan'])
        self.write_to_disk(self.MSGFjobs_MASIC_resultant , self.parent_folder, "MSGFjobs_MASIC_resultant.xlsx" )

        # print(masic_DF.shape, masic_DF.columns.values)
        # print('`' * 5)
        # print(self.MSGFjobs_MASIC_resultant.shape, self.MSGFjobs_MASIC_resultant.columns.values)
        # print('`' * 5)

