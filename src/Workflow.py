from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder
from src.data_access.via_DMS.FileOperations import FileOperations
from src.processing.DatasetsMerger import DatasetsMerger
from src.analysis import internalAnalysis

import os
import fnmatch

class Workflow:
    '''Automate the Meta-proteomics workflow'''

    def __init__(self, mode=None, InputType = None, path_to_data=None, project_name=None,
                 UserInput=None, CombineDatasets= None, SelectAnalysis=None):
        '''
        Intiate values from command line.
        :param mode:
        :param InputType:
        :param path_to_data:
        :param project_name:
        :param UserInput:
        :param CombineDatasets:
        :param SelectAnalysis:
        '''
        self.Mode= mode
        self.InputType= InputType
        self.Storage = path_to_data
        self.Project = project_name
        self.UserInput= UserInput
        self.CombineDatasets = CombineDatasets
        self.SelectAnalysis = SelectAnalysis

    def run_Analysis(self, on_file, analysis_type):
        '''
        Run desired analysis on a file.
        :meta public:
        :param analysis_type:
        :return:
        '''
        if analysis_type == "internal" :
            print("Run Internal analysis on {}".format(on_file))
            #internalAnalysis(on_file)
        elif analysis_type == "ficus":
            print("Run Ficus analysis on {}".format(on_file))
            #ficusAnalysis(on_file)
        else: #"both"
            print("Run Internal & Ficus analysis on {}".format(on_file))
            # internalAnalysis(on_file)
            # ficusAnalysis(on_file)

    def start_downStreamAnalysis(self, result_path):
        '''
        Decides to run analysis on combined results vs single dataset.
        :meta public:
        :param result_path:
        :return:
        '''

        if self.CombineDatasets:
            # generate report on single file.
            self.run_Analysis(result_path + "resultants_df.tsv", self.SelectAnalysis)
        else:
            # generate report on multiple files.
            for path, subdirs, files in os.walk(result_path):
                for file in files:
                    if fnmatch.fnmatch(file, "MSGFjobs_MASIC_resultant.tsv"):
                        self.run_Analysis( os.path.join(path, file), self.SelectAnalysis)

    def start_merging(self, folder):
        '''
        Start merging MSGF and MASIC jobs
        :meta public:
        :param folder:
        :return:
        '''
        merge = DatasetsMerger(folder, self.CombineDatasets)
        result_path = merge.merge_all_jobs_in_UserInput()
        return result_path

    def download_data_from_DMS(self,user_obj):
        '''
        build & execute query to dowload data from DMS
        :meta public:
        :param user_obj: input from shell script.
        :return: path to !!
        '''
        myQuery= QueryBuilder(user_obj, self.Storage, self.Project)
        myQuery.execute()
        analysis_jobs, parent_data_folder, job_info= myQuery.analysis_jobs, myQuery.parent_data_folder, myQuery.job_info

        file_obj= FileOperations(analysis_jobs, parent_data_folder, job_info)
        file_obj.get_files()
        return parent_data_folder

    def start_workflow(self):
        '''
        Runs the workflow in 3 stages
        1. Download relevant datasets from specified source.
        2. Aggregation of analysis tools{MSGF+, MASIC} results: to extract useful data from datasets.
        3. Generation of experimental report.
        :meta public:
        :return:
        '''

        # TODO: Use User-mode: to suppress file creations & Developer-mode: to Generate files!
        ## prepare user's input
        user_obj = Input()
        if self.InputType is None:
            # user_obj.user_input() # nomore manual execution
            pass
        else:
            user_obj.other_input(self.InputType, self.UserInput)
            ## 1.
            data_parent_folder= self.download_data_from_DMS(user_obj)
            print("Input Data located at  @:{}".format(data_parent_folder))
            ## 2.
            result_path= self.start_merging(data_parent_folder)
            print("Merged jobs located at @:{}".format(result_path))
            ## 3.
            self.start_downStreamAnalysis(result_path)
            print("Generated reports      @:{}".format(result_path))

        print('`'*5)
        print("Finished running Meta-proteomics pipeline!")
