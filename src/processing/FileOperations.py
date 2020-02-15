import os
import fnmatch
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utility.utils import timeit

class FileOperations:
    ''' Grab  locations of the MSGF+ & MASIC analysis tools using analysis_jobs object'''

    def __init__(self, analysis_jobs= None, parent_folder= None):
        self.Input = analysis_jobs
        self.parent_folder = parent_folder
        self.url = None
        self.started_from=None
        self.file_pattern_types = ["*msgfplus_syn.txt",
                                   "*SeqToProteinMap.txt",
                                   "*ResultToSeqMap.txt",
                                   "*_SICstats.txt"]

    def parse_fileserverpath_to_web_url(self, file_server_path):
        ''' Converts Windows FileSever path to webURL.
        :param file_server_path: windows server file path.
        :return:
        '''
        folders = file_server_path.split('\\')
        self.url = 'http://' + folders[2] + '.pnl.gov/' + '/'.join(folders[3:])

    def write_to_disk(self, url):
        '''
        :param url: Job's file path on DMS.
        :return:
        '''
        try:
            os.system('wget %s' % url)
            logging.info("Files transferred successfully!")
        except Exception as e:
            logging.info("FAILED to transfer files!")

    def use_df(self,df):
        '''
        Called for each dataset in the dataFrame!
        :param df: reference to analysis_jobs object.
        :return:
        '''
        #FIXME: Need to check whether below approach of creating folder path is OS independent or not?
        new_parent_folder = self.parent_folder + '/' + str(df['Dataset_ID'])+ '/' +  'MSGFjobs'+ '/' + str(df['MSGFPlusJob'])
        if not os.path.exists(new_parent_folder):
            os.makedirs(new_parent_folder)
        os.chdir(new_parent_folder)

        path_or_url = str(df['MSGFplus_loc'])
        if not path_or_url.startswith("http"):
            self.parse_fileserverpath_to_web_url(path_or_url)
            self.download_over_http()
        else:
            self.url= path_or_url
            self.download_over_http()

        os.chdir(self.started_from)  # parent folder resets
        new_parent_folder = self.parent_folder + '/' + str(df['Dataset_ID']) + '/' + 'MASICjob' + '/' + str(df['NewestMasicJob'])
        if not os.path.exists(new_parent_folder):
            os.makedirs(new_parent_folder)
        os.chdir(new_parent_folder)

        path_or_url = str(df['MASIC_loc'])
        if not path_or_url.startswith("http"):
            self.parse_fileserverpath_to_web_url(path_or_url)
            self.download_over_http()
        else:
            self.url= path_or_url
            self.download_over_http()

        os.chdir(self.started_from)  # parent folder resets

    @timeit
    def get_files(self):
        '''Start's any anf File operation.
        :return:
        '''
        self.started_from = os.getcwd()
        self.Input.apply( lambda x: self.use_df(x), axis=1)

    def download_over_http(self):
        '''
        Given a url, copy files from DMS to disk!
        :return:
        '''
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        filenames= [ link.get('href') for link in soup.find_all('a')]
        for file in filenames:
            for p in self.file_pattern_types:
                if fnmatch.fnmatch(file, p):
                    parsed_uri = urlparse(self.url)
                    domain_name = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                    file_url = domain_name + file
                    if not os.path.isfile(file.split('/')[-1]): # needed to avoid duplicating MSAIC files.
                        self.write_to_disk(file_url)

    def download_over_ftp(self):
        '''
        TODO : Directly from Proto-X windows file-server
        Eg. folder_path :"\\proto-6\QExactHF03\2015_2\MinT_Kans_No_Gly_pool_19_Qexactive_22May15_Arwen_14-12-03\SIC201505251246_Auto1197920"
        :return:
        '''

    def download_using_DMS_api(self):
        '''
        TODO: need to explore!
        Source: https://prismwiki.pnl.gov/wiki/DMS_Data_Export#Advanced_DMS_Data_Export
        url= https://dms2.pnl.gov/data/ax/tsv/aux_info_categories/aux_info_def/501
        :return:
        '''