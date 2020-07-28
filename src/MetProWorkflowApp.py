from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder
from src.data_access.via_DMS.FileOperations import FileOperations
from src.processing.DatasetsMerger import DatasetsMerger
from src.analysis import internalAnalysis
from utility.utils import str2bool

import os
import fnmatch
from argparse import RawTextHelpFormatter, ArgumentParser


class MetProWorkflowApp:
    '''Automate the Meta-proteomics workflow'''

    def __init__(self, mode=None, InputType = None, path_to_data=None, project_name=None,
                 UserInput=None, CombineDatasets= None, SelectAnalysis=None):
        self.Mode= mode
        self.InputType= InputType
        self.Storage = path_to_data
        self.Project = project_name
        self.UserInput= UserInput
        self.CombineDatasets = CombineDatasets
        self.SelectAnalysis = SelectAnalysis

    def run_Analysis(self, on_file, analysis_type):
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
        merge = DatasetsMerger(folder, self.CombineDatasets)
        result_path = merge.merge_all_jobs_in_UserInput()
        return result_path

    def download_data_from_DMS(self,user_obj):
        '''
        build & execute query to dowload data from DMS

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

if __name__ == '__main__':

    parser= ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument( "-M", "--Mode",
                        help="\nDifferent Modes to run the workflow?\n"
                             "\t  Developer : Automatically generates files at each step!\n"
                             "\t  User      : Generates CrossTab/Metric only!\n",
                        type=str)
    parser.add_argument("-It", "--InputType",
                        help="\n"
                             "1 : a datapackage ID\n"
                             "2 : a list of dataset IDs\n"
                             "3 : a list of MSGFjobs Nums\n",
                        type=int,
                        choices=[1, 2, 3])
    parser.add_argument("-S", "--Storage",
                        help="Give path where you want to store data & results of pipeline ",
                        type=str)
    parser.add_argument("-P", "--ProjectName", nargs="?",
                        help="FICUS project name",
                        type=str)
    parser.add_argument("-I", "--Input",
                        help="\nA valid input\n"
                             "InputType: 1, An Integer\n"
                             "InputType: 2, A comma-seperated list of Integers\n"
                             "InputType: 3, A comma-seperated list of Integers\n",
                        type=str)
    parser.add_argument("-C","--CombineDatasets",
                        type=str2bool,nargs="?",
                        const=True, default=False,
                        help="Combine all dataset's MSGF & MASIC jobs to single file for generating crossTabs.")
    parser.add_argument("-Sa", "--SelectAnalysis",
                        help="\n"
                             "internal : Run internal analysis\n"
                             "ficus    : Run ficus analysis\n"
                             "both     : Run both analysis\n",
                        type=str,
                        choices=["internal", "ficus", "both"] )
    args = parser.parse_args()
    start = MetProWorkflowApp(args.Mode, args.InputType, args.Storage ,args.ProjectName, args.Input, args.CombineDatasets, args.SelectAnalysis )
    start.start_workflow()