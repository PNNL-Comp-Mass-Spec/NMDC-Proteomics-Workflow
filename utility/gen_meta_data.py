import os
import hashlib
import fnmatch
import json
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

from utility.utils import timeit

PIPELINE_TYPE= "nmdc:MetaProteomicAnalysis"
EXECUTION_RESOURCE = "EMSL"
TYPE= "nmdc:DataObject"
GIT_URL = "https://github.com/microbiomedata/metaPro/releases/tag/1.0.0"

'''
TODO: planning to split this class calling instances of this class from 
      different components of pipeline.(only Definations will live here!)
      Then we won't require below Global variable.
'''
# "stegen" | "hess" | "blanchard"
STUDY= "stegen"
DATA_LOC="/Volumes/MSSHARE/Anubhav/storage/data/set_of_Dataset_IDs"+"/"+STUDY
# read mapper file
ROOT_LOC = "/Users/anub229/Documents_/Projects/NMDC/dump"
# "EMSL48099_JGI1393_Hess_DatasetToMetagenomeMapping.xlsx"
# "EMSL48473_JGI1781_Stegen_DatasetToMetagenomeMapping.xlsx"
# "EMSL49483_JGI503125_Blanchard_DatasetToMetagenomeMapping.xlsx"
MAPPER_FN= "EMSL48473_JGI1781_Stegen_DatasetToMetagenomeMapping.xlsx"
FASTA_LOC= "/Volumes/MSSHARE/Anubhav/fastas"

class GenMetadata:
    def __init__(self):
        self.activity={}
        self.data_object={}
        self.uri = 'mongodb://localhost:27017/'
        self.activity_coll= None
        self.data_obj_coll= None
        self.emsl_to_jgi={}

    def write_to_json_file(self, filenames):
        with open(filenames[0], 'w') as fptr1 ,\
            open(filenames[1], 'w') as fptr2:
            fptr1.write('[\n')
            fptr2.write('[\n')
            activity_count= self.activity_coll.count()
            data_obj_count= self.activity_coll.count()
            for index, (doc1, doc2) in enumerate(zip(self.activity_coll.find(),self.data_obj_coll.find()) ):
                doc1["id"] = doc1.pop("_id")
                doc2["id"] = doc2.pop("_id")
                fptr1.write(json.dumps(doc1, indent=4))
                fptr2.write(json.dumps(doc2, indent=4))
                if index != activity_count-1: # skip for last document.
                    fptr1.write(",\n")
                    fptr2.write(',\n')
            fptr1.write('\n]')
            fptr2.write('\n]')

        print("Finished parsing {}=={}".format(activity_count,data_obj_count))

    def make_connection(self, db_name, coll_names):
        '''
        - Make connection to mongodb database
        - Make cursors available.
        :param db_name: database name
        :param coll_names: list of collection names: _activity then _data_obj
        :return:
        '''
        client = MongoClient(self.uri)
        # makes db.coll if not exists.
        self.activity_coll = client[db_name][coll_names[0]]
        self.data_obj_coll = client[db_name][coll_names[1]]

    def get_md5(self, file):
        '''
        generates MD5 checksum of a file.
        :param file: filename with absolute path.
        :return: chechsum or ""
        '''
        if not file in (None, ""):
            md5 = hashlib.md5(open(file, 'rb').read()).hexdigest()
            return md5
        else:
            return ""

    def grab_fasta_file(self, genome_directory):
        '''
        Search for desired fasta file
        :param genome_directory: absolute path to fasta file.
        :return: absolute path to a fasta.
        '''
        faa_file_loc = os.path.join(FASTA_LOC, STUDY, genome_directory, "annotation")
        for path,subdirs,files in os.walk(faa_file_loc):
            for file in files:
                # looking for exact match!
                if fnmatch.fnmatch(file, '.'.join([genome_directory,'faa'])):
                    return os.path.join(path, file)
                else:
                    print("{}.faa doesn't exist at {}".format(genome_directory, os.path.join(path)))

    def gettime(self):
        '''
        Start and end time of running the pipeline.
        :return:
        '''
        return datetime.today().strftime('%Y-%m-%d')

    def gen_id(self, dataset_id, genome_directory, nersc_seq_id ):
        '''
        - Generate unique ID foreach dataset in the _activity.json
        :param dataset_id: EMSL dataset ID
        :param genome_directory: JGI fasta location
        :param nersc_seq_id:
        :return:
        '''
        txt = "{}\n{}\n{}\n".format( str(dataset_id), str(genome_directory), str(nersc_seq_id))
        return 'nmdc:{}'.format(hashlib.md5(txt.encode('utf-8')).hexdigest())


    def prepare_data_object(self, file , dataset_id, newfilename, description ):
        '''
        - Makes entry in _emsl_analysis_data_objects.json
        - Contains information about Pipeline's analysis results E.g.
            1. resultant.tsv
            2. data_out_table.tsv

        :param file: internal absolute path to analysis result file.
        :param dataset_id: EMSL datasetID
        :param newfilename: renamed "file" if needed!
        :param description: user's comment about the analysis result file.
        :return:
        '''
        checksum= self.get_md5(file)
        if checksum:
            file_id = 'nmdc:'+ checksum
            print("{} : {}".format(checksum, file))
            self.data_object['_id']= file_id
            self.data_object['name'] = dataset_id+'_'+newfilename
            self.data_object['description'] = description
            self.data_object['file_size_bytes'] =os.stat(file).st_size
            self.data_object['type'] =TYPE
            return file_id
        else:
            print("Found HASH empty for {}".format(file))

    def prepare_activity(self, dataset_id, genome_directory, nersc_seq_id):
        '''
        - Makes entry in _MetaProteomicAnalysis_activity.json
        - Foreach dataset, a pointer:
            from : _MetaProteomicAnalysis_activity.json.has_output.[*_file_id]
            to   : _emsl_analysis_data_objects.json."id"
        :param dataset_id: EMSL datasetID
        :param genome_directory:
        :param nersc_seq_id:
        :return:
        '''
        self.activity["_id"] = self.gen_id(dataset_id, genome_directory, nersc_seq_id)
        self.activity["name"]= ":".join(["Metaproteome",dataset_id, genome_directory])
        self.activity["was_informed_by"]= ":".join(["emsl", dataset_id])
        self.activity["started_at_time"]= self.gettime()
        self.activity["ended_at_time"]= self.gettime()
        self.activity["type"]=PIPELINE_TYPE
        self.activity["execution_resource"]=EXECUTION_RESOURCE
        self.activity["git_url"]=GIT_URL

        has_input=[]
        ptr_to_raw_in_bills_json=  "emsl:output_"+dataset_id
        has_input.append(ptr_to_raw_in_bills_json)
        fasta = self.grab_fasta_file(genome_directory)
        self.emsl_to_jgi[dataset_id]= fasta
        fasta_checksum= self.get_md5(fasta)
        if fasta_checksum:
            print("{} : {}".format(fasta_checksum, fasta))
            has_input.append('nmdc:' + fasta_checksum)
            self.activity["has_input"] = has_input
        else:
            print("Found HASH empty for {}".format(fasta))

        has_output=[]
        # results must exist!
        resultant_file= os.path.join(DATA_LOC.replace("data","results"), dataset_id, "MSGFjobs_MASIC_resultant.tsv")
        resultant_file_id=self.prepare_data_object( resultant_file,
                                                    dataset_id,
                                                    'resultant.tsv',
                                                    "Aggregation of analysis tools{MSGFplus, MASIC} results"
                                                    )
        has_output.append(resultant_file_id)

        data_out_table_file= os.path.join(DATA_LOC.replace("data","results"), dataset_id, "data_out_table.tsv")
        data_out_table_file_id=self.prepare_data_object( data_out_table_file,
                                                         dataset_id,
                                                         'data_out_table.tsv',
                                                         "QC_analysis"
                                                         )
        has_output.append(data_out_table_file_id)
        self.activity["has_output"] =has_output

    def on_each_row(self, row):
        '''
        Runs foreach dataset and make entry in a collection.
        :param row: each row in the EMSL-JGI mapper file.
        :return:
        '''
        dataset_id = str(row['Dataset ID'])
        nersc_seq_id = str(row['sequencing_project_extid'])
        genome_directory = str(row['genome directory'])
        print(">>Prepare activity for datasetID:{} genome_directory:{}".format(dataset_id,genome_directory))
        if not genome_directory in ( "", "missing"):
            # skip empty or missing genome_directory
            self.prepare_activity(dataset_id, genome_directory, nersc_seq_id)

            self.activity_coll.insert_one(self.activity)
            self.data_obj_coll.insert_one(self.data_object)
            self.activity.clear()
            self.data_object.clear()
        else:
            print("genome_directory:{} can't be empty/missing!".format(genome_directory))

    @timeit
    def start(self):
        '''
        Beging parsing EMSL-JGI mapper file.
        :return:
        '''
        df_xlsx = pd.read_excel(ROOT_LOC + '/' + MAPPER_FN)
        print("Parsing file {} :: {}".format(MAPPER_FN, df_xlsx.shape))
        df_xlsx.apply(lambda row: self.on_each_row(row), axis=1)

if __name__ == "__main__":

    meta_file= GenMetadata()
    db_name= "mp_metadata"
    coll_names= ["{}_MetaProteomicAnalysis_activity".format(STUDY),
                 "{}_emsl_analysis_data_objects".format(STUDY)]
    #setup the cursors
    meta_file.make_connection(db_name, coll_names)

    # meta_file.start()

    # database to json dump
    activity= os.path.join(ROOT_LOC , STUDY+'_MetaProteomicAnalysis_activity.json')
    data_obj= os.path.join(ROOT_LOC , STUDY+'_emsl_analysis_data_objects.json')
    meta_file.write_to_json_file([activity, data_obj])

    # Pipeline uses this file to process datasets.
    emsl_to_jgi_file= os.path.join(DATA_LOC, "emsl_to_jgi.json")
    if not os.path.exists(emsl_to_jgi_file):
        with open(emsl_to_jgi_file , 'w' ) as fptr:
            fptr.write(json.dumps(meta_file.emsl_to_jgi, indent=2))

    print("Hit the bottom!")