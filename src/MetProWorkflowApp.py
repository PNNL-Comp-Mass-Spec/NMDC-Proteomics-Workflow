from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder
from src.processing.FileOperations import FileOperations

class MetProWorkflowApp:
    '''Automates the Meta-proteomics workflow'''
    def __init__(self):
        pass

    def start_workflow(self):

        # get the user's input
        user_obj = Input()
        user_obj.user_input()

        # build & execute query
        myQuery= QueryBuilder(user_obj)
        myQuery.execute()
        # pickup the objects
        analysis_jobs, job_info, parent_data_folder= myQuery.analysis_jobs, myQuery.job_info, myQuery.parent_data_folder

        # Download relevant files from DMS
        file_obj= FileOperations(analysis_jobs, parent_data_folder)
        file_obj.get_files()

        # Start merge Process

        # print(crossTab.shape, all_info.columns.values)

        # Generate Metrics and Visualisation
        # Metric = downStreamAnalysis()


if __name__ == '__main__':
    MetProWorkflowApp().start_workflow()
