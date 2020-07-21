import os
import hashlib
import pandas as pd
import fnmatch
from datetime import datetime
from shutil import copyfile

from utility.utils import timeit

PIPELINE_TYPE= "nmdc:MetaProteomicAnalysis"
EXECUTION_RESOURCE = "EMSL"
TYPE= "nmdc:DataObject"
GIT_URL = "https://github.com/microbiomedata/metaPro/releases/tag/1.0.0"
STUDY="hess"
DATA_LOC="/Volumes/MSSHARE/Anubhav/storage/data/set_of_Dataset_IDs"+"/"+STUDY

class GenMetadata:
    '''
    TODO: planning to split calling instances of this class from different components of pipeline.(only Definations will live here!)    '''
    def __init__(self):
        self.activity={}
        self.data_object={}


    def get_md5(self, filepath):
        # print(">>",filepath)
        # if filepath is not None: # if file transfered, it cries!
        md5 = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
        return md5

    def grab_fasta_filename(self, genome_directory):
        nersc_fasta_dump_loc = "/Volumes/MSSHARE/Anubhav/fastas"
        fasta_loc = os.path.join(nersc_fasta_dump_loc, STUDY, genome_directory, "annotation")
        for path,subdirs,files in os.walk(fasta_loc):
            for file in files:
                if fnmatch.fnmatch(file, '.'.join([genome_directory,'faa'])):
                    return os.path.join(path,file)
                # else:
                #     print("{} metagenome doesn't exist".format(genome_directory))
                #     return ""

    def gettime(self):
        return datetime.today().strftime('%Y-%m-%d')

    def gen_id(self, dataset_id, genome_directory, nersc_seq_id ):
        txt = "{}\n{}\n{}\n".format( str(dataset_id), str(genome_directory), str(nersc_seq_id))
        return 'nmdc:{}'.format(hashlib.md5(txt.encode('utf-8')).hexdigest())


    def prepare_data_object(self, file_path , dataset_id, newfilename, description ):
        file_id = 'nmdc:'+self.get_md5(file_path)
        self.data_object['id']= file_id
        self.data_object['name'] = dataset_id+'_'+newfilename
        self.data_object['description'] = description
        self.data_object['file_size_bytes'] =os.stat(file_path).st_size
        self.data_object['type'] =TYPE
        return file_id

    def move_successful(self, old_checksum, new_fasta_file_path):
        #FIXME If the .faa files exist, we don't need to run for them!
        # if os.path.exists(new_fasta_file_path):
        #     print("File already moved!")
        #     return False
        # else:
        return old_checksum == self.get_md5(new_fasta_file_path)

    def move_fasta_to_data_loc(self, old_file_path, new_file_path):
        # This function assumes that the manuel NERSC data dump has happened for a study!
        if not os.path.exists(new_file_path):# and new_file_path is not None:
            copyfile(old_file_path,new_file_path)
            # os.rename(old_file_path, new_file_path)

    def prepare_activity(self, dataset_id, genome_directory, nersc_seq_id):
        self.activity["id"] = self.gen_id(dataset_id, genome_directory, nersc_seq_id)
        self.activity["name"]= ":".join(["Metagenome",genome_directory, nersc_seq_id])
        self.activity["was_informed_by"]= ":".join(["emsl", dataset_id])
        self.activity["started_at_time"]= self.gettime()
        self.activity["ended_at_time"]= self.gettime()
        self.activity["type"]=PIPELINE_TYPE
        self.activity["execution_resource"]=EXECUTION_RESOURCE
        self.activity["git_url"]=GIT_URL

        has_input=[]
        ptr_to_raw_in_bills_json=  "emsl:output_"+dataset_id
        has_input.append(ptr_to_raw_in_bills_json)

        old_fasta_file_path = self.grab_fasta_filename(genome_directory)
        print("old_fasta_file_path >>>> | ", old_fasta_file_path)
        if old_fasta_file_path is not None:
        # print("<<",old_fasta_file_path)
            nersc_fasta_checksum= self.get_md5(old_fasta_file_path)

            new_fasta_file_path = os.path.join(DATA_LOC, dataset_id, "{}.faa".format(dataset_id))
            self.move_fasta_to_data_loc(old_fasta_file_path, new_fasta_file_path )

            if self.move_successful(nersc_fasta_checksum,new_fasta_file_path ):
                print("Move successful {} --> {}".format(genome_directory, dataset_id))
                # if not successfull, you don't have checksum!
                has_input.append('nmdc:'+nersc_fasta_checksum)
                self.activity["has_input"]=has_input


                has_output=[]
                # results must already be generated!
                resultant_file_path= os.path.join(DATA_LOC.replace("data","results"), dataset_id, "MSGFjobs_MASIC_resultant.tsv")
                resultant_file_id=self.prepare_data_object( resultant_file_path,
                                                            dataset_id,
                                                            'resultant.tsv',
                                                            "Aggregation of analysis tools{MSGFplus, MASIC} results"
                                                            )
                has_output.append(resultant_file_id)

                # data_out_table_file_path= os.path.join(DATA_LOC.replace("data","results"), dataset_id, "data_out_table.tsv")
                # data_out_table_file_id=self.prepare_data_object( data_out_table_file_path,
                #                                                  dataset_id,
                #                                                  'data_out_table.tsv',
                #                                                  "QC_analysis"
                #                                                  )
                # has_output.append(data_out_table_file_id)

                self.activity["has_output"] =has_output

    def on_each_row(self, df, root_loc):

        dataset_id = str(df['Dataset ID'])
        nersc_seq_id = str(df['sequencing_project_extid'])
        genome_directory = str(df['genome directory'])
        print(dataset_id,nersc_seq_id,genome_directory)
        self.prepare_activity(dataset_id, genome_directory, nersc_seq_id)


        with open(root_loc + '/' + STUDY + 'MetaProteomicAnalysis_activity.json', 'a+') as f:
            f.write(str(self.activity))
            f.write(',\n')

        with open(root_loc + '/' + STUDY + 'emsl_analysis_data_objects.json', 'a+') as f:
            f.write(str(self.data_object))
            f.write(',\n')

        self.activity.clear()
        self.data_object.clear()

    @timeit
    def start(self):
        # read mapper file
        root_loc = "/Users/anub229/Downloads"
        mapper_file = "EMSL48099_JGI1393_Hess_DatasetToMetagenomeMapping.xlsx"
        # mapper_file = "EMSL48473_JGI1781_Stegen_DatasetToMetagenomeMapping.xlsx"
        # mapper_file = "EMSL49483_JGI503125_Blanchard_DatasetToMetagenomeMapping.xlsx"
        df_xlsx = pd.read_excel(root_loc + '/' + mapper_file)
        print("{} :: {} :: ".format(mapper_file, df_xlsx.shape))
        df_xlsx.apply(lambda x: self.on_each_row(x, root_loc), axis=1)

if __name__ == "__main__":


    meta_file= GenMetadata()
    # meta_file.start()
    print("Hit the bottom!")



