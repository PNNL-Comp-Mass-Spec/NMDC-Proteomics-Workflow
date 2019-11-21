### WorkFlow: A proteomics datapipeline prototype for Mass Spectrometry identifications.

This pipeline purpose if to automate the process of merging results from MSGF+ and MSAIC. It will be further extended by another service that will be running MSGF+ standalone,  will produce files which will be used by this prototype for downstream processing.

##### Description of the main directory structure.
| Folder/Files      | Description           |
| :------------- |:-------------| 
| **src**      | Contains the pipeline code.
| **test** | unit test cases      |
| **results** | Merged files from MSGF+ and MASIC      |
| **docker** | Dockerfile to run the complete project as standalone application in a container      |
| **data** | Contains MSGF+ result files.     |
| **utility** | python implementation of useful decorators. (to assist development)      |
| **README.md** | Overview of the proteomics workflow.       |

##### How to run the pipeline:

1. Set the temporary environment variables(Instruction for bash shell)
   
    ```shell script
    $ export DATABASE_USERNAME= 
    $ export DATABASE_PASSWORD=
    $ export DATABASE_SERVER=
    $ export DATABASE_NAME=
   
    ```
    verify whether env variables have been set or not!(List all the variable currently set in your env)
    ```shell script
   $ printenv
    ```
2. Design you SQL query, and add to `src/access_methods/direct_access/query.py` Query class's instance variable query.
    
3. Now, To run 
    - Directly, 
    ```shell script
    $ python ./src/proteomic_workflow.py
    ```
    - Using StandAlone app running in Docker container.
        - Install docker([Follow instructions](https://docs.docker.com/docker-for-mac/install/))
        - Build an image
          ```shell script
          
          $ docker build -t myapp -f docker/Dockerfile .
          ``` 
        - Run image
          ```shell script
          
          $ docker run myapp 
          ``` 
##### Execution of the pipeline:
Input: 
          *  data_package_id or 
          *  a/list of MSGF+ job_id 
1. Given input a data_package_id
    - get all the dataset_id.
        - For each dataset_id
            1. if you find both MSGF+ and MSAIC jobs, then merge the results
            2. if you find only MSGF+ jobs
                - Search for MSAIC jobs at other location.
    
2. Given input a/list of MSGF+ job_id
    - get corresponding dataset_id
       - For each dataset_id, repeat step 1.
       
Algorithm for merge the MSGF+ and MSAIC results:
    1. Merge MSGF+ results to get `peptideIdentification.txt` 
        - Using mapping from `*ResultToSeqMap.txt file`:
            - Make a look up in `*msgfplus_syn.txt` and `*SeqToProteinMap.txt` file and write to new file called `peptideIdentifications.txt` (./results/)
    2. Merge `peptideIdentification.txt` with `` over `Scan_id` to obtain
       msgfplus_masic_merge.txt
         
Output: msgfplus_masic_merge.txt
    
Note:
> - This pipeline will be further extend for Meta-proteomics!
>- 

