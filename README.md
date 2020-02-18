# A Meta-proteomics data processing pipeline(Workflow) for Mass Spectrometry identifications.

This pipeline purpose if to automate the process of merging results from MSGF+ and MSAIC. It will be further extended by another service that will be running MSGF+ standalone,  will produce files which will be used by this prototype for downstream processing.

### Description of the  structure.
```shell script
.
├── src                                
│   ├── MetProWorkflowApp.py           # Run the Meta-proteomics workflow
│   ├── data_access                    
│   │   ├── general                    
│   │   └── via_DMS                                        
│   │       ├── DMSDatabase.py         # MSSQL database functions.
│   │       ├── Input.py               # UserInut defined
│   │       ├── Query.py               # Configuration file: set of SQL Queries.
│   │       ├── QueryBuilder.py        # Configure appropriate SQL queries and executes them.
│   │       └── secure.py              # Configuration file: MSSQL database credentials
│   └── processing
│       ├── DatasetsMerger.py          #
│       ├── FileOperations.py          #
│       ├── MASICmerger.py             #
│       ├── MSGFplusMerger.py          #
├── data                               # Files Dumped & Used while running workflow
│   ├── dpkgs                          # Data for UserInput_1: data data package
│   ├── set_of_Dataset_IDs             # Data for UserInput_2: list of dataset_IDs
│   └── set_of_Jobs                    # Data for UserInput_3: list of MSGF_Jobs
├── results                            
├── tests                              # unit test cases 
├── docker                             # Dockerfile to run the complete project as standalone application in a container
│   └── Dockerfile                     # 
└── utility
    └── utils.py
├── subscriptionService
├── README.md                          # Overview of the proteomics workflow.
├── Task-2.1.5.md                      # 
├── requirements.txt                   # 
├── setup.py                           # 
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
   1) Using the Consolidate_syn object 
   3) For each scan, select the peptide with the lowest Spec EValue
       - If there is more than one peptide with a tied spec evalue, select both of them
   4) Examine the proteins for the selected peptide (or peptides) in the given scan
        - If all of the proteins start with XXX_, this is a Decoy (aka reverse) PSM
        - Otherwise, if any of the proteins does not start with XXX, this is a forward PSM
   5) Remove the prefix and suffix letters from the peptide
       - For example, given peptide K.SPVGKS*PPSTGSTYGSSQKEESAASGGAAYTKR.Y, remove K. and .Y to get SPVGKS*PPSTGSTYGSSQKEESAASGGAAYTKR
       - Call this the base peptide
   6) Look for that base peptide in a new in-memory table called the UniquePeptide table
       - If the table does not have the peptide, add it, storing BasePeptide, SpecEValue, and IsDecoy=True or false
       - If the table does have the peptide, and if the SpecEValue for the base peptide in this scan is lower, update the update the entry for the peptide to have the lower SpecEValue
   7) Once all scans are processed, your new in-memory table will have one row per base peptide
       - If you had encountered these two peptides, you would have two rows; that's OK (and appropriate, since the * symbol is in different locations)
         SPVGKS*PPSTGSTYGSSQKEESAASGGAAYTKR
      SPVGKSPPSTGSTYGSS*QKEESAASGGAAYTKR
   8) Sort this unique peptide table on SpecEValue, then IsDecoy, then peptide (thus, for entries with the same SpecEValue, the IsDecoy=false ones should be first)
   9) Step through that table and count the number of Forward hits and the number of Decoy hits, up to the current row
   10) Compute DecoyCount / ForwardCount; this is the PepQValue
   11) When the DecoyCount value increments by one, assign the DecoyCount / ForwardCount value for the previous row to all previous rows with the same DecoyCount value
   12) Once all rows have been processed, go back to the original table and assign an updated PepQValue by linking the two tables on Peptide (linking on Base Peptide)
   13) Report both the original PepQValue and your re-computed PepQValue in the output table so that we can assure that they're similar.
    
### Necessary information of files generated during workflow execution:

   ```
    ├── data                          
    │   ├── dpkgs/             
    │   ├── set_of_Dataset_IDs/
    │   └── set_of_Jobs/ 
   ```
   1. `start_file.xlsx`
        ```   
           | Dataset_ID | MSGFPlusJob | MSGFplus_loc | NewestMasicJob | MASIC_loc |
           |------------|-------------|--------------|----------------|-----------|
        ```    
   2. `job_info_query.xlsx`
        ```    
           | Job | Dataset | Experiment | OrganismDBName | ProteinCollectionList | ParameterFileName |
           |-----|---------|------------|----------------|-----------------------|-------------------|
        ```

   ```
    ├── results                          
    │   ├── dpkgs/Dataset_ID/                  
    │   ├── set_of_Dataset_IDs/Dataset_ID/
    │   └── set_of_Jobs/Dataset_ID/
   ```
   1. `*_consolidate_syn.xlsx`
        ```      
           | ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset |
           |----------|------|------------|-----------|--------|-------------|------|----------|----|---------|---------|-----|-------------|-----------|-------------------|------------------------|--------|--------|-----------|--------------|--------|---------|
        ```   
   2. `*_recomupted_consolidate_syn.xlsx`
        ```   
           | ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset | recomputedQValue| recomputedPepQValue |
           |----------|------|------------|-----------|--------|-------------|------|----------|----|---------|---------|-----|-------------|-----------|-------------------|------------------------|--------|--------|-----------|--------------|--------|---------|-----------------|---------------------|   
        ```   
   3. `*_MSGFjobs_Merged.xlsx`
        ```
           | ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset | Unique_Seq_ID | Cleavage_State | Terminus_State | Protein_Expectation_Value_Log(e) | Protein_Intensity_Log(I) |
           |----------|------|------------|-----------|--------|-------------|------|----------|----|---------|---------|-----|-------------|-----------|-------------------|------------------------|--------|--------|-----------|--------------|--------|---------|---------------|----------------|----------------|----------------------------------|--------------------------|
        ```
   4. `*_MSGFjobs_MASIC_resultant.xlsx`
        ```   
           | ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset_x | Unique_Seq_ID | Cleavage_State | Terminus_State | Protein_Expectation_Value_Log(e) | Protein_Intensity_Log(I) | Dataset_y | ParentIonIndex | MZ | SurveyScanNumber | OptimalPeakApexScanNumber | PeakApexOverrideParentIonIndex | CustomSICPeak | PeakScanStart | PeakScanEnd | PeakScanMaxIntensity | PeakMaxIntensity | PeakSignalToNoiseRatio | FWHMInScans | PeakArea | ParentIonIntensity | PeakBaselineNoiseLevel | PeakBaselineNoiseStDev | PeakBaselinePointsUsed | StatMomentsArea | CenterOfMassScan | PeakStDev | PeakSkew | PeakKSStat | StatMomentsDataCountUsed |
           |----------|------|------------|-----------|--------|-------------|------|----------|----|---------|---------|-----|-------------|-----------|-------------------|------------------------|--------|--------|-----------|--------------|--------|-----------|---------------|----------------|----------------|----------------------------------|--------------------------|-----------|----------------|----|------------------|---------------------------|--------------------------------|---------------|---------------|-------------|----------------------|------------------|------------------------|-------------|----------|--------------------|------------------------|------------------------|------------------------|-----------------|------------------|-----------|----------|------------|--------------------------|
        ```
   ```
    ├── results                          
    │   ├── dpkgs/                     
    │   ├── set_of_Dataset_IDs/
    │   └── set_of_Jobs/
   ``` 
   - `resultants_df.xlsx`
   
   - `*_crossTab.txt`
   
   - genrated histogram
   
   - automated report of the analysis