# A Meta-proteomics data processing pipeline(Workflow) for Mass Spectrometry identifications.

This pipeline purpose if to automate the process of merging results from MSGF+ and MSAIC. It will be further extended by another service that will be running MSGF+ standalone,  will produce files which will be used by this prototype for downstream processing.

### Description of the  structure.
```shell script
.
├── src                             # Contains the pipeline code.
│   ├── MetProWorkflowApp.py        # Run the Meta-proteomics workflow
│   ├── access_methods
│   │   └── direct_access
│   │       ├── DMSDatabase.py      # MSSQL database functions.
│   │       ├── Input.py            # UserInut defined
│   │       ├── Query.py            # Configuration file: set of SQL Queries.
│   │       ├── QueryBuilder.py     # Configure appropriate SQL queries and executes them.
│   │       └── secure.py           # Configuration file: MSSQL database credentials
│   └── processing
│       ├── FileOperations.py
│       ├── Merge.py
├── data                            # Files Dumped & Used while running workflow
│   ├── dpkgs                       # Data for UserInput_1: data data package
│   │   ├── 3458                    
│   │   │   ├── job_query_info.xlsx 
│   │   │   └── start_file_3458.xlsx# 
│   ├── set_of_Dataset_IDs          # Data for UserInput_2: list of dataset_IDs
│   │   ├── job_query_info.xlsx
│   │   └── start_file.xlsx
│   └── set_of_Jobs                 # Data for UserInput_3: list of MSGF_Jobs
│       ├── job_query_info.xlsx
│       └── start_file.xlsx
├── results
├── tests                           # unit test cases 
├── docker                          # Dockerfile to run the complete project as standalone application in a container
│   └── Dockerfile
└── utility
    └── utils.py
├── subscriptionService
├── README.md                       # Overview of the proteomics workflow.
├── Task-2.1.5.md                  
├── requirements.txt
├── setup.py
````

## Installation:
 #### Manual setup
   - [Download and install "Conda"](https://docs.conda.io/en/latest/miniconda.html): package manager and environment management system.
   - In terminal:
        - Download codebase from stash
        
            ```git clone https://stash.pnnl.gov/scm/omcs/nmdc-proteomics-workflow.git```
            
            ```cd nmdc-proteomics-workflow```

        - Create seperate environment to run the workflow.
        
             ```conda create --name <my_proteomics_env> --file requirements.txt```   
             
             ```conda activate my_proteomics_env```
             
             [refer this]((https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf)) for OS specific commands
        - Set the temporary environment variables(Instruction for bash shell)
        
            ```
            $ export DATABASE_USERNAME= 
            $ export DATABASE_PASSWORD=
            $ export DATABASE_SERVER=
            $ export DATABASE_NAME=
            ```
            verify whether env variables have been set or not!(List all the variable currently set in your env)
            
            ``` $ printenv```
        - Install workflow as a package:
           ```pip install -e .```
        - Run the workflow
        
            ```chmod 777 ./StartMetaProteomicsWorkflow.sh```
            
            ```./StartMetaProteomicsWorkflow.sh```
  #### Docker setup
   Using StandAlone app running in Docker container.
   - Install docker([Follow instructions](https://docs.docker.com/docker-for-mac/install/))
   - In terminal:
        - Download codebase from stash
        
            ```git clone https://stash.pnnl.gov/scm/omcs/nmdc-proteomics-workflow.git```
            
            ```cd nmdc-proteomics-workflow```
        - Build an image using the 
        
          ```$ docker build -t my_workflow -f docker/Dockerfile .``` 
        - Run image
        
          ```$ docker run my_workflow```
 
## Workflow details:
 #### User input options([DMS](https://prismwiki.pnl.gov/wiki/Data_Management_System)):
   1. a data_package_id.
   2. a list of Dataset_IDs.
   3. a list of MSGF+ Jobs.
    
 #### Workflow outline:   
   - Given an User-input:
        - Generate 
           - start_file.xlsx
           - job_info_query.xlsx
        - For each dataset:
            **Algorithm for merging MSGF+ and MASIC analysis job results**
            - Combine multiple [MSGFplusJob results](https://prismwiki.pnl.gov/wiki/MSGF%2B_Results_Files):
                 1. Merge "*_msgfplus_syn.txt" files based on scan_id.
                 2. keep the best scoring peptide(minimum MSGFDB_SpecEValue candidate) for each scan.
                 3. Generate `consolidate_syn`( big peptide file). 
                 4. Generate,`recomupted_consolidate_syn` 
                   [improving the "False Discovery Rate" algorithm on `Consolidate_syn`.](###Algorithm-to-Recompute-the-qvalues)
                 5. Obtain protein information from below files & merge it with `recomupted_consolidate_syn`.
                   `*_msgfplus_syn_SeqToProteinMap.txt`(protein file) and 
                   `*_msgfplus_syn_ResultToSeqMap.txt` {mapper file}
                 6. Generate `MSGFjobs_Merged`.
            - Combine `MSGFjobs_Merged` with MASIC results
                 1. Merge on the basis of `Scan_id` in `_SICstats.txt`. 
                 2. Generate `MSGFjobs_MASIC_resultant`.
        - Create a crossTab/ pivot table:
            - Combine `MSGFjobs_MASIC_resultant` of all datasets.
        - Generate Metrics/ Visualisations
            - Using `crossTab` 
        - Report generation.
            `TODO`

    
`TODOs `:
- Untie Workflow from DMS
    - Start directly from `.raw` files.
    - running [MSGF and MASIC tools seperately in docker](https://github.com/MoTrPAC/motrpac-proteomics-pnnl-prototype). 
  - [MzidToTSVConverter](https://github.com/PNNL-Comp-Mass-Spec/Mzid-To-Tsv-Converter)


## Additional Information:

### **Algorithm to Recompute the qvalues**
     In some datasets MSGFplus tool dealing with SPLIT FASTAs due to which the `QValue` and `PepQValue` value aren't
     based on the entire FASTA file for that dataset. Therefore, we're recomputing these 2 columns after we get 
     `Consolidate_syn` (by merging all the MSGFplusjobs ran on multiple FASTAs)

### Necessary information of files generated during workflow execution:

```
├── data                          
│   ├── dpkgs/             
│   ├── set_of_Dataset_IDs/
│   └── set_of_Jobs/ 
```
   1. `start_file.xlsx`
    
   | Dataset_ID | MSGFPlusJob | Data Folder Link | NewestMasicJob | Results Folder Path |
   |------------|-------------|------------------|----------------|---------------------|
    
   2. `job_info_query.xlsx`
    
   | Job | Dataset | Experiment | OrganismDBName | ProteinCollectionList | ParameterFileName |
   |-----|---------|------------|----------------|-----------------------|-------------------|

```
├── results                          
│   ├── dpkgs/Dataset_ID/                  
│   ├── set_of_Dataset_IDs/Dataset_ID/
│   └── set_of_Jobs/Dataset_ID/
```
   1. `*_consolidate_syn.txt`
   
   | ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError |
   |:--------:|------|------------|-----------|--------|-------------|------|----------|----|---------|---------|-----|-------------|-----------|-------------------|------------------------|--------|--------|-----------|--------------|

   2. `*_recomupted_consolidate_syn.txt`
   
   3. `*_MSGFjobs_Merged.txt`
      
   4. `*_MSGFjobs_MASIC_resultant.txt`

```
├── results                          
│   ├── dpkgs/                     
│   ├── set_of_Dataset_IDs/
│   └── set_of_Jobs/
``` 
   - `*_crossTab.txt`
   
   - genrated histogram
   
   - automated report of the analysis