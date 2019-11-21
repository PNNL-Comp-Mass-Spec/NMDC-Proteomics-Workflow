'''MS SQl queries needed to extract MSGF+ results and MSAIC results'''

class Query:

    def __init__(self, job_id, dataset_id):
        self.job_id = job_id
        self.dataset_id = dataset_id
        self.datapackage_id = None

        self.table_schema_name = None
        self.view_name = None
        self.query = None

    @classmethod
    def from_input(cls):
        #FIXME : Need to be added execution using data_package_id
        return cls(
                   int(input('job_id:')),
                   int(input('dataset_id:')) )

    def set_query(self):
        '''Design queries here & set it'''

        # self.table_schema_name = 'dbo'
        # self.view_name = "V_Mage_Analysis_Jobs"
        #
        # self.query = "SELECT * FROM {} WHERE Dataset_ID={} and Job={}".format(self.view_name,
        #                                                                         self.dataset_id,
        #                                                                         self.job_id)
        # self.query = """ SELECT COLUMN_NAME, TABLE_SCHEMA
        #                    FROM INFORMATION_SCHEMA.COLUMNS
        #                    WHERE TABLE_SCHEMA= '{}' and TABLE_NAME = '{}';""".format(self.table_schema_name,
        #                                                                              self.view_name)
        #
        # self.query = """SELECT Folder
        #                 FROM {}
        #                 WHERE Dataset_ID={} and Job={}""".format(self.view_name,
        #                                                               self.dataset_id,
        #                                                               self.job_id)
        # self.view_name = "V_Mage_Data_Package_Analysis_Jobs"
        # self.query = """SELECT * FROM {} WHERE Dataset_ID={} and Job={}""".format(self.view_name,
        #                                                                           self.datapackage_id)
        dataset_id_list = self.query = """SELECT [Dataset ID]
                                            FROM V_Data_Package_Analysis_Jobs_List_Report
                                            WHERE [ID] = 3021"""

        for dataset_id in dataset_id_list:
            # search whether it's type A or B
                self.query =
