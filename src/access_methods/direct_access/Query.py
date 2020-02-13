
class Query:

    #-------------------------------------------------------- Type A
    # Get the MSGF+ Jobs, plus Dataset_IDs
    # sometime MASIC Jobs aren't added in the datapackage by the user, so always safe to get MASIC information from DATASET_MASIC query!
    DATASET_MSFG=""" SELECT A.Dataset_ID,
                                   A.MSGFPlusJob,
                                   B.MasicJob
                            FROM ( SELECT Dataset_ID,
                                          Job AS MSGFPlusJob
                                   FROM DMS_Data_Package.dbo.V_Data_Package_Analysis_Jobs_List_Report
                                   WHERE ID = {} AND
                                         Tool LIKE 'msgf%' ) A
                                 LEFT OUTER JOIN
                                 ( SELECT Dataset_ID,
                                          Job AS MasicJob
                                   FROM DMS_Data_Package.dbo.V_Data_Package_Analysis_Jobs_List_Report
                                   WHERE ID = {} AND
                                         Tool LIKE 'masic%' ) B
                                   ON A.Dataset_ID = B.Dataset_ID
                            """
    # Get the Data Folders for the MSGF+ Jobs (and also the MASIC jobs, if included in tthe data package)
    MSGF_loc = """SELECT JobNum, [Data Folder Link]
                FROM V_Analysis_Job_Detail_Report_2
                WHERE JobNum IN ({})"""

    # Find the newest MASIC job for a list of dataset IDs
    DATASET_MASIC= """  SELECT Dataset_ID, Max(Job) As NewestMasicJob
                        FROM V_Analysis_Job_List_Report_2
                        WHERE Dataset_ID In ({})
                              And Tool Like 'masic%'
                        Group by Dataset_ID"""

    # Get the Data Folders for the MSGF+ Jobs (and also the MASIC jobs, if included in tthe data package)
    MASIC_loc = """SELECT JobNum AS NewestMasicJob , [Results Folder Path]
                        FROM V_Analysis_Job_Detail_Report_2
                        WHERE JobNum IN ({})"""

    #--------------------------------------------------------
    # Type B Given a list of dataset_IDs, determine MSGF
    # DATASET = """   SELECT Dataset_ID, Job, [Results Folder Path]
    #                 FROM V_Analysis_Job_List_Report_2
    #                 WHERE Job IN ( SELECT Max(Job)
    #                                FROM V_Analysis_Job_List_Report_2
    #                                WHERE [Tool] LIKE 'msgf%' AND
    #                                            Dataset_ID IN ({})
    #                                GROUP BY dataset_id )"""
    DATASET = """       SELECT Dataset_ID, Job, [Data Folder Link]
                        FROM V_Analysis_Job_Detail_Report_2 
                        WHERE [JobNum] IN (SELECT Job
                                           FROM V_Data_Package_Analysis_Jobs_List_Report 
                                           WHERE [ID] = 508538 and 
                                          [Tool] LIKE 'msgf%')"""

    # Could use this query to get the MSGF Jobs--> Using MSGF Jobs, find the "Data Folder link" {in view: V_Analysis_Job_Detail_Report_2 as above over JobNum!}
    """ 
    SELECT Dataset_ID, Max(Job) as Job, 
    FROM V_Analysis_Job_List_Report_2
    WHERE Dataset_ID In ({})
          And Tool Like 'msgf%'
    Group by Dataset_ID  
    """
    #-------------------------------------------------------- Type C Given a list of MSGF+ jobs, determine the dataset_IDs
    MSGF = """SELECT Job,[Results Folder Path], Dataset_ID
                FROM V_Analysis_Job_List_Report_2
                WHERE Job IN ({})"""

    # to create Job info file!
    JOB_INFO = """SELECT Job, Dataset, Experiment, OrganismDBName, ProteinCollectionList, ParameterFileName
                        FROM V_Analysis_Job_Export
                        Where Job In  ({}) 
                        Order By Dataset, job"""