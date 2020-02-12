#!/usr/bin/env python
'''Automate the proteomics workflow'''

from src.access_methods.direct_access.Input import Input
from src.access_methods.direct_access.QueryBuilder import QueryBuilder

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



if __name__ == '__main__':

    MetProWorkflowApp().start_workflow()

# Test Input to Pipeline

# datapackage ID
# 3524 @paul NMDC_HESS_prot1_pdp
# 3458 @yuchian Mint-soil
# 3021 @matt

# set of dataset-IDs
# 508538, 509161, 509162, 509163, 509166, 509167, 511721, 511723, 511724, 511726, 511727, 511728, 526183, 526184, 526185, 526387, 526388, 526438, 526439, 526440, 526441, 526481, 526482, 526483, 526539, 526540, 526549, 526586, 526587, 526588

# set of JobNums
# 1553244, 1553245, 1553246, 1553247, 1553248, 1553249, 1553250, 1553251, 1553252, 1553253, 1553254, 1553255, 1553256, 1553257, 1553258, 1553259, 1553260, 1553261, 1553262, 1553263, 1553264, 1553265, 1553266, 1553267, 1553268, 1553269, 1553270, 1553271, 1553272, 1553273