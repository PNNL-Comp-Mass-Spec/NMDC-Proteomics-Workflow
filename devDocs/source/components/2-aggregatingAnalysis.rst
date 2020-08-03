Aggregating analysis results
==========

Overview of software:
*********************
#. Analyzing component:

   #. Reads in syn.txt files & calculated the best scoring peptides for each scan.
   #. Even though, MSGF+ estimates False discovery rates(FDRs) in some datasets MSGFplus tool when dealing with SPLIT FASTAs(multiple FASTA for the same sample) doesn’t actually account all of them due to which the QValue and PepQValue value aren't based on the entire FASTA file for that dataset. Therefore, we're recomputing QValue and PepQValue to improve the FDR.
   #. merges the outputs from MSGF+ and MASIC, and applies to filter to control the false discovery rate. The output is a crosstab format table with rows containing protein sequence information, and columns with relative abundance measurements for proteins identified in each sample analyzed.


Merging Algorithm:
------------------
.. code-block::
   :linenos:

   - Given an User-input:
        - Generate
           - start_file.xlsx
           - job_info_query.xlsx
        - For each dataset:
            **Algorithm for merging MSGF+ and MASIC analysis job results**
            - Combine multiple `MSGFplusJob results`_:
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

Recompute the qvalues Algorithm:
--------------------------------

.. code-block::
   :linenos:

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

Data flow diagram:
------------------

Input:
------


Output:
-------

* start_file.csv

+------------+-------------+--------------+----------------+-----------+
| Dataset_ID | MSGFPlusJob | MSGFplus_loc | NewestMasicJob | MASIC_loc |
+------------+-------------+--------------+----------------+-----------+

* job_info_query.csv

+-----+---------+------------+----------------+-----------------------+-------------------+
| Job | Dataset | Experiment | OrganismDBName | ProteinCollectionList | ParameterFileName |
+-----+---------+------------+----------------+-----------------------+-------------------+

* consolidate_syn.csv

+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+
| ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset |
+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+

* recomupted_consolidate_syn.csv

+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+------------------+---------------------+
| ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset | recomputedQValue | recomputedPepQValue |
+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+------------------+---------------------+

* MSGFjobs_Merged.csv

+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+---------------+----------------+----------------+----------------------------------+--------------------------+
| ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset | Unique_Seq_ID | Cleavage_State | Terminus_State | Protein_Expectation_Value_Log(e) | Protein_Intensity_Log(I) |
+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+---------+---------------+----------------+----------------+----------------------------------+--------------------------+

* `MSGFjobs_MASIC_resultant.csv` and `resultants_df.csv`

+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+-----------+---------------+----------------+----------------+----------------------------------+--------------------------+-----------+----------------+----+------------------+---------------------------+--------------------------------+---------------+---------------+-------------+----------------------+------------------+------------------------+-------------+----------+--------------------+------------------------+------------------------+------------------------+-----------------+------------------+-----------+----------+------------+--------------------------+
| ResultID | Scan | FragMethod | SpecIndex | Charge | PrecursorMZ | DelM | DelM_PPM | MH | Peptide | Protein | NTT | DeNovoScore | MSGFScore | MSGFDB_SpecEValue | Rank_MSGFDB_SpecEValue | EValue | QValue | PepQValue | IsotopeError | JobNum | Dataset_x | Unique_Seq_ID | Cleavage_State | Terminus_State | Protein_Expectation_Value_Log(e) | Protein_Intensity_Log(I) | Dataset_y | ParentIonIndex | MZ | SurveyScanNumber | OptimalPeakApexScanNumber | PeakApexOverrideParentIonIndex | CustomSICPeak | PeakScanStart | PeakScanEnd | PeakScanMaxIntensity | PeakMaxIntensity | PeakSignalToNoiseRatio | FWHMInScans | PeakArea | ParentIonIntensity | PeakBaselineNoiseLevel | PeakBaselineNoiseStDev | PeakBaselinePointsUsed | StatMomentsArea | CenterOfMassScan | PeakStDev | PeakSkew | PeakKSStat | StatMomentsDataCountUsed |
+----------+------+------------+-----------+--------+-------------+------+----------+----+---------+---------+-----+-------------+-----------+-------------------+------------------------+--------+--------+-----------+--------------+--------+-----------+---------------+----------------+----------------+----------------------------------+--------------------------+-----------+----------------+----+------------------+---------------------------+--------------------------------+---------------+---------------+-------------+----------------------+------------------+------------------------+-------------+----------+--------------------+------------------------+------------------------+------------------------+-----------------+------------------+-----------+----------+------------+--------------------------+

Moving on
---------

Now it is time to move on to :doc:`../components/3-reportgen`.

.. _MSGFplusJob results: https://prismwiki.pnl.gov/wiki/MSGF%2B_Results_Files