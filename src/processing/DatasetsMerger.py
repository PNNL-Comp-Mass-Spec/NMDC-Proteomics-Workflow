from src.processing.MSGFplusMerger import MSGFplusMerger
from src.processing.MASICmerger import MASICmerger
import os
import pandas as pd
import fnmatch
from pathlib import Path

class DatasetsMerger(MSGFplusMerger):
    '''1. Run for UserInput:
                         a datapackage or
                         a set of datasets or
                         a set of MSGFJobNums
      2. create a crossTab object

    '''
    def __init__(self, folder= None, combineDatasets=None):
        '''

        :param folder:
        :param combineDatasets:
        '''
        self.resultants = []
        self.parent_folder = folder
        self.resultants_df= None
        self.crossTab = None
        self.dataset_result_folder = folder.replace("data", "results")
        self.combineDatasets= combineDatasets

    def merge_all_jobs_in_UserInput(self):
        '''
        1. Run for each dataset.
        2. Merge all MSGFjobs_MASIC_resultant objects.

        :return:
        '''
        if not os.path.exists(self.dataset_result_folder):
            # stop =0
            for dataset in next(os.walk(self.parent_folder))[1]:
                if dataset != "DMS_fasta_param":

                     dataset_loc = self.parent_folder + dataset + '/'
                     # print("dataset_loc >> ", dataset_loc)
                     msfg_obj= MSGFplusMerger(dataset_loc)
                     msfg_obj.consolidate_syn_files()

                     masic = MASICmerger(dataset_loc)
                     masic.merge_msgfplus_msaic(msfg_obj.MSGFjobs_Merged)
                     if self.combineDatasets:
                        self.resultants.append(masic.MSGFjobs_MASIC_resultant)
                     # if stop==1:
                     #     break

            print("`"*5)
            print("Finished aggregating analysis tools results at loc:{}".format(self.dataset_result_folder))
            print("`"*5)
            if self.combineDatasets:
                # concatenate all datasets
                # print("self.combineDatasets >>", self.combineDatasets)
                self.resultants_df = pd.concat(self.resultants)
                # print("self.dataset_result_folder >> ", self.dataset_result_folder)
                self.write_to_disk(self.resultants_df, self.dataset_result_folder, "resultants_df.tsv")

        print("Already ran Pipeline, Merged jobs exists at @:{}! please delete them & rerun the pipeline!".format(self.dataset_result_folder))
        return self.dataset_result_folder
    # def manual_merge_datasets(self):
    #
    #     group_files=[]
    #     for cur_path, directories, files in os.walk(str(Path(__file__).parents[2])+'/'+self.parent_folder):
    #         # print(cur_path)
    #         for file in files:
    #             if fnmatch.fnmatch(file, "MSGFjobs_MASIC_resultant.xlsx"):
    #                 group_files.append(os.path.join(cur_path, file))
    #     print(group_files)
    #     df = pd.DataFrame()
    #     for f in group_files:
    #         data = pd.read_excel(f, 'Sheet1')
    #         df = df.append(data)
    #     self.write_to_disk(df,str(Path(__file__).parents[2])+'/'+self.parent_folder, "resultants_df_1.csv" )

