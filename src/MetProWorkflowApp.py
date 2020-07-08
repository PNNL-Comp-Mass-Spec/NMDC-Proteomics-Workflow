from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder
from src.data_access.via_DMS.FileOperations import FileOperations
from src.processing.DatasetsMerger import DatasetsMerger

from argparse import RawTextHelpFormatter, ArgumentParser
from src.analysis.downStreamAnalysis import downStreamAnalysis
from utility.utils import str2bool

class MetProWorkflowApp:
    '''Automates the Meta-proteomics workflow'''

    def __init__(self, mode=None, InputType = None,
                 path_to_data=None, project_name=None, UserInput=None, CombineDatasets= None):
        self.Mode= mode
        self.InputType= InputType
        self.Storage = path_to_data
        self.Project = project_name
        self.UserInput= UserInput
        self.CombineDatasets = CombineDatasets

    def start_merging(self, folder):
        merge = DatasetsMerger(folder, self.CombineDatasets)
        merge.merge_all_jobs_in_UserInput()

        # merge.manual_merge_datasets()
        # merge.create_crossTab()
        # print(crossTab.shape, all_info.columns.values)
        return
    def start_downStreamAnalysis(self, path):

        # Generate Metrics and Visualisation
        # metric = downStreamAnalysis(merge.crossTab)
        # metric.filterdata()
        # metric.
        print("start_downStreamAnalysis >>", path)
        cleaner = downStreamAnalysis(path)
        cleaner.process_data()

        pass

    def download_data_from_DMS(self,user_obj):
        # build & execute query to dowload data from DMS
        myQuery= QueryBuilder(user_obj, self.Storage, self.Project)
        myQuery.execute()
        analysis_jobs, parent_data_folder, job_info= myQuery.analysis_jobs, myQuery.parent_data_folder, myQuery.job_info

        file_obj= FileOperations(analysis_jobs, parent_data_folder, job_info)
        file_obj.get_files()
        return parent_data_folder

    def start_workflow(self):
        # TODO: Use User-mode: to suppress file creations & Developer-mode: to Generate files!

        # prepare user's input
        user_obj = Input()
        if self.InputType is None:
            # user_obj.user_input() # no manual execution
            # Have data from user.
            pass
        else:
            user_obj.other_input(self.InputType, self.UserInput)
            parent_folder= self.download_data_from_DMS(user_obj)
            print("MetProWorkflowApp >> ",parent_folder)

            self.start_merging(parent_folder)
            # self.start_downStreamAnalysis(parent_folder)



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
                        help="Combine all datasets MSGF & MASIC jobs to single file for generating crossTabs")


    args = parser.parse_args()
    start = MetProWorkflowApp(args.Mode, args.InputType, args.Storage ,args.ProjectName, args.Input, args.CombineDatasets )
    start.start_workflow()