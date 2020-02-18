from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder
from src.processing.FileOperations import FileOperations
from src.processing.DatasetsMerger import DatasetsMerger
from src.analysis.downStreamAnalysis import downStreamAnalysis

from argparse import RawTextHelpFormatter, ArgumentParser

class MetProWorkflowApp:
    '''Automates the Meta-proteomics workflow'''

    def __init__(self, mode=None, InputType = None, UserInput=None):
        self.Mode= mode
        self.InputType= InputType
        self.UserInput= UserInput

    def start_workflow(self):

        # get the user's input
        user_obj = Input()
        if self.InputType is None:
            user_obj.user_input()
        else:
            user_obj.other_input(self.InputType, self.UserInput)

        # TODO: Use User-mode: to suppress file creations & Developer-mode: to Generate files!
        # build & execute query
        myQuery= QueryBuilder(user_obj)
        myQuery.execute()
        analysis_jobs, job_info, parent_data_folder= myQuery.analysis_jobs, myQuery.job_info, myQuery.parent_data_folder

        # Download relevant files from DMS
        file_obj= FileOperations(analysis_jobs, parent_data_folder)
        file_obj.get_files()

        # Start merge Process
        # parent_data_folder='data/dpkgs/3458/'
        merge = DatasetsMerger(parent_data_folder)
        merge.merge_all_jobs_in_UserInput()
        # merge.create_crossTab()
        # print(crossTab.shape, all_info.columns.values)

        # Generate Metrics and Visualisation

        # metric = downStreamAnalysis(merge.crossTab)
        # metric.filterdata()
        # metric.

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
    parser.add_argument("-I", "--Input",
                        help="\nA valid input\n"
                             "InputType: 1, An Integer\n"
                             "InputType: 2, A comma-seperated list of Integers\n"
                             "InputType: 3, A comma-seperated list of Integers\n",
                        type=str)
    args = parser.parse_args()
    start = MetProWorkflowApp(args.Mode, args.InputType, args.Input)
    start.start_workflow()