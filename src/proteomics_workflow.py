#!/usr/bin/env python
'''Automate the proteomics workflow'''

import os
import fnmatch
import logging
import glob
import csv
import collections

from access_methods.direct_access.DMSDatabase import DMSDatabase
from access_methods.direct_access.query import Query
from access_methods.direct_access.secure import Config
from utility.utils import timeit

from bs4 import BeautifulSoup
import requests


class FileOperations:
    '''DMS to fileSystem file operations'''

    def __init__(self, url=None, disk_loc=None):
        self.url = url
        self.disk_loc = disk_loc
        self.path_to_files= None
        # TODO Tweak file pattern to get only required files.
        self.file_pattern_types = ["*msgfplus_syn.txt",
                                   "*SeqToProteinMap.txt",
                                   "*ResultToSeqMap.txt"]
    @timeit
    def copy_files_from_server(self):
        '''
        Copy files from DMS to Local filesystem.
        :return:
        '''
        response = requests.get(self.url)
        rep_str = response.text

        soup = BeautifulSoup(rep_str, 'html.parser')

        os.chdir('../data/msgfplus/')
        self.path_to_files = '/'.join(self.disk_loc[3:])
        try:
            if not os.path.exists(self.path_to_files):
                os.makedirs(self.path_to_files)
                os.chdir(self.path_to_files)

                filenames= [ link.get('href') for link in soup.find_all('a')]
                for file in filenames:
                    for p in self.file_pattern_types:
                        if fnmatch.fnmatch(file, p):
                            file_url = 'http://'+self.disk_loc[2]+'.pnl.gov/'+file
                            os.system('wget %s'% file_url)
        except:
            print("Files already exists, no need to copy!")

class Merge(FileOperations):
    ''' Merging MSGF+ results and MSAIC results'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_loc = None
        self.destination = os.path.join(os.path.dirname(__file__),'..','results')+'/'
        self.source = None
        self.msgfplus_syn_dict    = collections.defaultdict(list)
        self.SeqToProteinMap_dict = collections.defaultdict(list)
        self.peptide_identification_header= None

    def get_files(self):
        '''Initiate file transfer.
        :return:
        '''
        try:
            # query the database
            db = DMSDatabase(Config)
            user = Query.from_input()
            user.set_query()
            query = user.query

            # get the query output
            folder_name = db.run_query(query)
            folders = folder_name.split('\\')

            # create a webURL
            url = 'http://' + folders[2] + '.pnl.gov/' + '/'.join(folders[3:])
            file_op= FileOperations(url, folders)
            file_op.copy_files_from_server()

            self.data_loc = file_op.path_to_files
            self.source = os.path.join(os.path.dirname(__file__),'..','data/msgfplus/',self.data_loc)+'/'
            logging.info("Files transferred successfully!")
        except Exception as e:
            logging.info("FAILED to transfer files!")

    @timeit
    def make_files_searchable(self):
        '''
        Create dictionary objects for o(1) search in msgfplus_syn & SeqToProteinMap files.
        :return:
        '''

        duplicate, duplicate_1, stop, stoop = {}, {}, 0, 0

        with open(glob.glob(self.source + self.file_pattern_types[0])[0], 'r') as msgfplus_syn, \
                open(glob.glob(self.source + self.file_pattern_types[1])[0], 'r') as SeqToProteinMap :

            peptide = csv.reader(msgfplus_syn, delimiter='\t')
            peptide_header= next(peptide)
            protein = csv.reader(SeqToProteinMap, delimiter='\t')
            protein_header= next(protein)

            self.peptide_identification_header = peptide_header[1:10]+peptide_header[11:]+protein_header[3:]
            self.peptide_identification_header.insert(0,'Unique_Seq_ID')
            self.peptide_identification_header.insert(0, 'Result_ID')
            stop=0
            for result_id in peptide:
                stop+=1
                if result_id[0] not in self.msgfplus_syn_dict:
                    self.msgfplus_syn_dict[ result_id[0] ].append(tuple(result_id[1:10]+result_id[11:]))
                    duplicate_1[result_id[0]] = 0
                else:
                    self.msgfplus_syn_dict[ result_id[0] ].append( tuple(result_id[1:10]+result_id[11:]))
                    duplicate_1[result_id[0]] += 1

            dup_exist_1= {key: val for key, val in duplicate_1.items() if val != 0}
            if dup_exist_1 !={}:
                print("CAUTION: The duplicates found in msgfplus_syn file")
                print(dup_exist_1)
            stop=0
            for unique_seq_id in protein:
                stop+=1
                if unique_seq_id[0] not in self.SeqToProteinMap_dict:
                    self.SeqToProteinMap_dict[ unique_seq_id[0] ].append(tuple(unique_seq_id[3:]))
                    duplicate[unique_seq_id[0]]=0
                else:
                    self.SeqToProteinMap_dict[ unique_seq_id[0] ].append( tuple(unique_seq_id[3:]))
                    duplicate[unique_seq_id[0]]+= 1

            dup_exist = {key: val for key, val in duplicate.items() if val != 0}
            if dup_exist != {}:
                print("{} duplicates found in SeqToProteinMap file".format(len(dup_exist)))

            print('Start searching in files \n msgfplus_syn: {} and SeqToProteinMap: {}'.format(len(self.msgfplus_syn_dict), len(self.SeqToProteinMap_dict)))

    @timeit
    def merge_msgfplus_results(self):
        '''
        Search in msgfplus_syn, SeqToProteinMap files and
        create merged file ./results/peptideIdentification.txt
        :return:
        '''
        #TODO: Load files them in pandas & use it for manipulation.
        with open(glob.glob(self.source+self.file_pattern_types[2])[0], 'r') as ResultToSeqMap,\
                open(self.destination+'peptideIdentification.txt', 'w') as identify_peptide:

                mapper = csv.reader(ResultToSeqMap, delimiter= '\t')
                next(mapper, None)  # skip the header
                writer = csv.writer(identify_peptide, delimiter='\t')

                # save files into dictionary
                self.make_files_searchable()
                writer.writerow(self.peptide_identification_header)

                stop=0
                for line in mapper:
                    stop+=1
                    Result_ID, Unique_Seq_ID = line[0], line[1]
                    pep_val= self.msgfplus_syn_dict[Result_ID]
                    pro_val= self.SeqToProteinMap_dict[Unique_Seq_ID]
                    if len(pro_val)>1:
                        for _ in range(len(pro_val)):
                            writer.writerow( (Result_ID,)+ (Unique_Seq_ID,)+ pep_val[0] + pro_val[_])
                    else:
                        writer.writerow( (Result_ID,)+ (Unique_Seq_ID,)+ pep_val[0]+ pro_val[0])
    @timeit
    def merge_msgfplus_msaic(self):
        # Merge

        pass
if __name__ == '__main__':

    merge_start= Merge()
    merge_start.get_files()
    merge_start.merge_msgfplus_results()
