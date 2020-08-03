from src.data_access.via_DMS.DMSDatabase import DMSDatabase
from src.data_access.via_DMS.secure import Config
from src.data_access.via_DMS.Query import Query

import pandas as pd
import os
import sys

class QueryBuilder():
    ''' 1. Build MS-SQl Queries.
        2. Execute them
        3. create a dataFrame that holds all Information
            Dataset_ID  | MSGFPlusJob  | Data Folder Link  | NewestMasicJob  |	Results Folder Path |

    '''
    def __init__(self, user_input= None, storage=None, project_name=None):
        '''

        :param user_input:
        :param storage:
        :param project_name:
        '''
        self.db= DMSDatabase(Config)
        self.user_input = user_input
        self.analysis_jobs = None
        self.job_info= None
        self.parent_data_folder = storage
        self.project_name = project_name
        # TODO: NMDC: 18 Create a Summary_Stats.txt to distinguish between proteomics & Meta-proteomics study!
        self.Summary_Stats= None

    def save_to_disk(self, data, data_path, msgf_job_list, id ):
        '''

        :param data:
        :param data_path:
        :param msgf_job_list:
        :param id:
        :return:
        '''
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        data.to_excel(data_path+ "start_file.xlsx")

        query = Query.JOB_INFO.format(','.join(str(job) for job in msgf_job_list))
        result_set = self.db.run_query(query).fetchall()
        df= pd.DataFrame(result_set)
        self.job_info= df

        df.to_excel(data_path+ "job_query_info.xlsx")
        # print('analysis_jobs obj size:', sys.getsizeof(self.analysis_jobs))
        pass

    def start_with_datapackage_id(self, id):
        '''
        Given a ID
        ----Find out the Dataset_ID  , MSGFPlusJob
        --------Using MSGFPlusJob, findout  "Data Folder Link"
        --------Using Dataset_ID,  findout  NewestMasicJob
        ------------Using NewestMasicJob findout "Results Folder Path"
        Merge results to create "analysis_jobs".

        :param id: datapackage_id
        :return:
        '''
        query = Query.DATASET_MSFG.format(id, id)
        result_set = self.db.run_query(query).fetchall()
        MSGFPlusJobs = pd.DataFrame(result_set)['MSGFPlusJob']
        Dataset_ID = pd.DataFrame(result_set)['Dataset_ID']

        query = Query.MSGF_loc.format(','.join(str(job) for job in MSGFPlusJobs.to_list()))
        result_set = self.db.run_query(query).fetchall()
        MSGFPlusJob_loc= pd.DataFrame(result_set)["MSGFplus_loc"]

        query = Query.DATASET_MASIC.format(','.join(str(job) for job in Dataset_ID.to_list()))
        result_set = self.db.run_query(query).fetchall()
        df_dataset_newest_MASIC = pd.DataFrame(result_set)
        NewestMasicJob = pd.DataFrame(result_set)['NewestMasicJob']

        query = Query.MASIC_loc.format(','.join(str(job) for job in NewestMasicJob.to_list()))
        result_set = self.db.run_query(query).fetchall()
        df_MASIC_loc= pd.DataFrame(result_set)

        # Concatenate
        df= pd.concat([Dataset_ID, MSGFPlusJobs, MSGFPlusJob_loc], axis=1)

        # Handles both 1-1   (1dataset-->1MSGF-->1MASIC) and
        #              1-Many(1dataset-->+MSGF-->1MASIC)
        first = df.merge(df_dataset_newest_MASIC, how='left', on= ['Dataset_ID', 'Dataset_ID'])
        second = first.merge(df_MASIC_loc, how="left", on= ['NewestMasicJob', 'NewestMasicJob'])

        self.analysis_jobs= second
        self.parent_data_folder = self.parent_data_folder+ '/' +'data/dpkgs/{}/'.format(id)
        self.save_to_disk(second,
                          self.parent_data_folder,
                          MSGFPlusJobs.to_list(),
                          id
                          )
        pass

    def start_with_dataset_ids(self, id_list):
        '''
        Given set of dataset-IDs
        ----findout MSGFPlusJob, "Results Folder Path"
        --------Using Dataset_ID,  findout  NewestMasicJob
        ------------Using NewestMasicJob findout "Results Folder Path"
        Merge results to create "analysis_jobs".

        :param id_list: set of dataset-IDs
        :return:
        '''
        query = Query.DATASET.format(','.join(str(job) for job in id_list))
        result_set = self.db.run_query(query).fetchall()
        df= pd.DataFrame(result_set)
        MSGFPlusJobs = pd.DataFrame(result_set)['MSGFPlusJob']

        query = Query.DATASET_MASIC.format(','.join(str(job) for job in id_list))
        result_set = self.db.run_query(query).fetchall()
        df_dataset_newest_MASIC = pd.DataFrame(result_set)
        NewestMasicJob = pd.DataFrame(result_set)['NewestMasicJob']

        query = Query.MASIC_loc.format(','.join(str(job) for job in NewestMasicJob.to_list()))
        result_set = self.db.run_query(query).fetchall()
        df_MASIC_loc= pd.DataFrame(result_set)

        # concatenate
        first = df.merge(df_dataset_newest_MASIC, how="left", on= ['Dataset_ID', 'Dataset_ID'])
        second = first.merge(df_MASIC_loc, how="left", on=['NewestMasicJob', 'NewestMasicJob'])

        self.analysis_jobs= second
        self.parent_data_folder = self.parent_data_folder+ '/' + 'data/set_of_Dataset_IDs/{}/'.format(self.project_name)

        self.save_to_disk(second,
                          self.parent_data_folder,
                          MSGFPlusJobs.to_list()
                          )
        pass
    def start_with_job_nums(self, id_list):
        '''
        Given set of MSGFJobs
        ----Find the Dataset_ID, & "Results Folder Path"
        --------Using Dataset_ID, findout MASIC
        ------------Using MASIC, findout "Results Folder Path"
        Merge results to create "analysis_jobs".

        :param id_list:  set of JobNums
        :return:
        '''
        query = Query.MSGF.format(','.join(str(job) for job in id_list))
        result_set = self.db.run_query(query).fetchall()
        msgf_loc_dataset= pd.DataFrame(result_set)
        MSGFPlusJobs= pd.DataFrame(result_set)['MSGFPlusJob']
        Dataset_ID = pd.DataFrame(result_set)['Dataset_ID']

        query = Query.DATASET_MASIC.format(','.join(str(job) for job in Dataset_ID.to_list()))
        result_set = self.db.run_query(query).fetchall()
        df_dataset_newest_MASIC = pd.DataFrame(result_set)
        NewestMasicJob = pd.DataFrame(result_set)['NewestMasicJob']

        query = Query.MASIC_loc.format(','.join(str(job) for job in NewestMasicJob.to_list()))
        result_set = self.db.run_query(query).fetchall()
        df_MASIC_loc= pd.DataFrame(result_set)

        # concatenate
        first = msgf_loc_dataset.merge(df_dataset_newest_MASIC, how='left', on=['Dataset_ID', 'Dataset_ID'])
        second = first.merge(df_MASIC_loc, how="left", on= ['NewestMasicJob', 'NewestMasicJob'])

        self.analysis_jobs= second
        self.parent_data_folder = self.parent_data_folder +'/' + 'data/set_of_Jobs/'
        self.save_to_disk(second,
                          self.parent_data_folder,
                          MSGFPlusJobs.to_list()
                          )
        pass
    def execute(self):
        '''Design queries here & set it'''
        try:
            # TODO: Remove query redundancy!
            dpkg_id= self.user_input.datapackage_id
            if dpkg_id:
                # find me all the jobs for each dataset in this datapackage!
                self.start_with_datapackage_id(dpkg_id)
            dataset_ids= self.user_input.dataset_ids
            if dataset_ids:
                # find me all the jobs for each dataset!
                self.start_with_dataset_ids(dataset_ids)
            msgf_jobs= self.user_input.job_nums
            if msgf_jobs:
                # find me all the datasets and their respective jobs!
                self.start_with_job_nums(msgf_jobs)

        except Exception as error:
            raise error
            # print("Query Builder Failed: User must provide correct input!")

        pass
