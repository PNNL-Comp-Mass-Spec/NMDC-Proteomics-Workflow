from utility.utils import timeit

import  os
import pandas as pd
import fnmatch

class MSGFplusMerger:
    '''1. Runs for each dataset.
       2. Collate "*msgfplus_syn.txt" &  --> consolidate_syn object
       3. Recompute the QValue and PepQValue -->recomupted_consolidate_syn object
       4. Look for protein information into
            *msgfplus_syn_SeqToProteinMap.txt : protein Info.
            *msgfplus_syn_ResultToSeqMap.txt  : Mapper
          --> MSGFjobs_Merged object
    '''
    def __init__(self, data_source=None):

        self.parent_folder = data_source
        self.consolidate_syn_DF= None #
        self.recomupted_consolidate_syn = None #
        self.MSGFjobs_Merged= None
        self.syn=[]
        self.protein=[]
        self.mapper=[]
        self.file_pattern_types = { "syn"     :   "{}syn.txt",
                                    # "syn"     :   [ "{}msgfplus_syn.txt", "{}msgfdb_syn.txt"],
                                    "protein" :   "{}SeqToProteinMap.txt",
                                    "mapper"  :   "{}ResultToSeqMap.txt"}

    def group_files(self, folder):

        # new_syn_type = self.file_pattern_types["syn"][0].format('*')
        # old_syn_type = self.file_pattern_types["syn"][1].format('*')

        for cur_path, directories, files in os.walk(folder):
            for file in files:
                if fnmatch.fnmatch(file, self.file_pattern_types["syn"].format('*')):#new_syn_type) or fnmatch.fnmatch(file, old_syn_type ):
                    self.syn.append(os.path.join(cur_path, file))
                elif fnmatch.fnmatch(file, self.file_pattern_types["protein"].format('*')):
                    self.protein.append(os.path.join(cur_path, file))
                elif fnmatch.fnmatch(file, self.file_pattern_types["mapper"].format('*')):
                    self.mapper.append(os.path.join(cur_path, file))

    def stack_files(self, grouped_files, file_pattern):
        stacked_frames=[]
        for fp in grouped_files:
            JobNum_name = fp.split('/')[-2]
            Dataset_name = os.path.basename(fp).replace(file_pattern.format('_'), '')
            temp = pd.read_csv(fp, sep='\t').assign(JobNum=JobNum_name, Dataset= Dataset_name )
            # print('<<',temp.shape)
            stacked_frames.append(temp)
        df = pd.concat(stacked_frames)
        print(">>> {} shape{}".format(file_pattern, df.shape))
        return df

    def write_to_disk(self, df, folder, file):
        # write to results:
        dataset_result_folder = os.path.join('results', '/'.join(folder.split('/')[1:])  )
        if not os.path.exists(dataset_result_folder):
            os.makedirs(dataset_result_folder)

        if not os.path.exists(dataset_result_folder + file):
            try:
                # to_excel() has Max sheet size is: 1048576, 16384 limit!
                # if it crossed that limit, it fails with : ValueError: This sheet is too large!
                df.to_excel(dataset_result_folder + file)
            except Exception as e:
                print(e)
            try:
                df.to_csv(dataset_result_folder + file, sep='\t')
            except Exception as e:
                print(e)

    @timeit
    def get_protein_info(self):
        '''
        1. For all jobs Read in(Stack):
            "*ResultToSeqMap.txt"  in ResultToSeqMap_DF with added JobNum column
            "*SeqToProteinMap.txt" in SeqToProteinMap_DF with added JobNum column
        2. Inner-join:
                consolidate_syn   and
                ResultToSeqMap_DF and \
                SeqToProteinMap_DF
            over
             1. JobNum   <--> JobNum
                ResultID <--> ResultID
             2. JobNum          <--> JobNum
                Unique_Seq_ID   <--> Unique_Seq_ID
                Protein         <--> Protein_Name
        3. create MSGFjobs_Merged dataframe.
        :return:
        '''
        #FIXME: Confirm with @matt: Could ResultID col in _syn file be duplicate?

        protein_df = self.stack_files(self.protein, self.file_pattern_types["protein"])
        del protein_df['Dataset']
        protein_df= protein_df.rename(columns={'Protein_Name': 'Protein'})

        mapper_df = self.stack_files(self.mapper, self.file_pattern_types["mapper"])
        del mapper_df['Dataset']
        mapper_df= mapper_df.rename(columns={'Result_ID': 'ResultID'})


        # TODO: Change  self.consolidate_syn_DF --> self.recomupted_consolidate_syn
        merge1= pd.merge(self.consolidate_syn_DF, mapper_df,  how='left', left_on=['JobNum','ResultID'], right_on = ['JobNum','ResultID'])
        self.MSGFjobs_Merged= pd.merge(merge1, protein_df,  how='left', left_on=['JobNum','Unique_Seq_ID','Protein'], right_on = ['JobNum','Unique_Seq_ID','Protein'])

        self.write_to_disk(self.MSGFjobs_Merged , self.parent_folder, "MSGFjobs_Merged.xlsx" )

        # print(self.consolidate_syn_DF.shape, self.consolidate_syn_DF.columns.values)
        # print('`'*5)
        # print(protein_df.shape, protein_df.columns.values)
        # print('`' * 5)
        # print(mapper_df.shape, mapper_df.columns.values)

    def consolidate_syn_files(self):
        '''
        1. For all jobs Read in(Stack):
            "*msgfplus_syn.txt" in _syn_DF with added JobNum & dataset column
        Note: _syn_DF have duplicate rows for each Scan with MSGFDB_SpecEValue
        :return:
        '''
        msgf_folder = os.path.join(self.parent_folder, 'MSGFjobs')
        self.group_files(msgf_folder)

        syn_df = self.stack_files(self.syn, self.file_pattern_types["syn"])
        self.keep_best_scoring_peptide(syn_df)

        self.get_protein_info()
        self.write_to_disk(syn_df , self.parent_folder, "syn_DF.xlsx" )
        self.write_to_disk(self.consolidate_syn_DF, self.parent_folder, "consolidate_syn_DF.xlsx")

    @timeit
    def keep_best_scoring_peptide(self, df):
        '''keeping the best scoring pepetide
        1. Using _syn_DF
        2. group by Scan
        3. For each unique Scan,
              Keep row with MSGFDB_SpecEValues
        4. create consolidate_syn_DF
        Note: consolidate_syn_DF
              have unique row for each ResultID, but
              has duplicate Scan due to multiple min MSGFDB_SpecEValue!
        :return:
        '''
        # Slow
        # df1 = df.groupby(['Scan'])['MSGFDB_SpecEValue'].min()
        # df1 = pd.DataFrame(df1, columns = ['MSGFDB_SpecEValue'])
        # df1['Scan'] = df1.index
        # df1.index = range(df1.shape[0])
        # self.consolidate_syn_DF = pd.merge(df,df1, on = ['Scan','MSGFDB_SpecEValue'])
        # print(">>> consolidate_syn_DF shape{}".format(self.consolidate_syn_DF.shape))

        # or # Fast
        self.consolidate_syn_DF = df[df.groupby("Scan")["MSGFDB_SpecEValue"].transform('min') == df['MSGFDB_SpecEValue']]
        print(">>> consolidate_syn_DF shape{}".format(self.consolidate_syn_DF.shape))

class Recompute_PepQValue:
    '''Recompute QValue` and PepQValue
    1. Use consolidate_syn_DF
    2.
    '''
    # FIXME: Once Recomputing Algo. works remove
    #  self.consolidate_syn_DF and
    #  self.consolidate_syn_DF from class & make it local!<-- save m/m.!


