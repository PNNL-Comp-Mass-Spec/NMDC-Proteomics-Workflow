from src.processing.MSGFplusMerger import MSGFplusMerger
from src.processing.MASICmerger import MASICmerger
import os
import pandas as pd

class DatasetsMerger(MSGFplusMerger):
    '''1. Run for UserInput:
                         a datapackage or
                         a set of datasets or
                         a set of MSGFJobNums
      2. create a crossTab object
    '''

    def __init__(self, folder= None):
        self.resultants = []
        self.parent_folder = folder
        self.resultants_df= None
        self.crossTab = None

    def create_crossTab(self):
        '''read resultants_df objects and create crossTab file
        :return:
        '''
        #
        # pd.pivot_table()


    def merge_all_jobs_in_UserInput(self):
        '''
        1. Run for each dataset.
        2. Merge all MSGFjobs_MASIC_resultant objects.
        :return:
        '''

        # stop =0
        for dataset in next(os.walk(self.parent_folder))[1]:
             # stop+=1
             dataset_loc = self.parent_folder + dataset + '/'
             msfg_obj= MSGFplusMerger(dataset_loc)
             msfg_obj.consolidate_syn_files()

             masic = MASICmerger(dataset_loc)
             masic.merge_msgfplus_msaic(msfg_obj.MSGFjobs_Merged)

             self.resultants.append(masic.MSGFjobs_MASIC_resultant)
             # if stop==1:
             #     break
        # concatenate all datsets

        self.resultants_df = pd.concat(self.resultants)
        # self.create_crossTab()
        self.write_to_disk(self.resultants_df, dataset_loc, "resultants_df.xlsx")



