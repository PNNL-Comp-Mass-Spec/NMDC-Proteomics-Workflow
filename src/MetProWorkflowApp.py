#!/usr/bin/env python
'''Automate the proteomics workflow'''

from src.data_access.via_DMS.Input import Input
from src.data_access.via_DMS.QueryBuilder import QueryBuilder

class MetProWorkflowApp:
    def __init__(self):
        pass

    def start_workflow(self):

        # get the user's input
        user_obj = Input()
        user_obj.user_input()

        # build & execute query
        myQuery= QueryBuilder(user_obj)
        myQuery.execute()
        all_info, job_info=myQuery.analysis_jobs, myQuery.job_info
        print(all_info.shape, all_info.columns.values,'\n' ,job_info.shape, job_info.columns.values)

        # Start merge Process

        # print(crossTab.shape, all_info.columns.values)

        # Generate Metrics and Visualisation
        # Metric = downStreamAnalysis()


if __name__ == '__main__':

    MetProWorkflowApp().start_workflow()
