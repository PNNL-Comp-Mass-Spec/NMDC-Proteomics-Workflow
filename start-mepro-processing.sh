#!/bin/sh
#---------Run the Mepro processing
path_to_raw=Users/anub229/Documents_/Projects/NMDC/nmdc_sandbox/dummy_code/feb12/nmdc-proteomics-workflow/data/dpkgs/3458/430185/MinT_Kans_No_Gly_pool_10_Qexactive_22May15_Arwen_14-12-03.raw
masic_output=./out/

for dir in ../data/     # list directories in the form "/tmp/dirname/"
do
    dir=${dir%*/}      # remove the trailing "/"
    echo ${dir##*/}    # print everything after the final "/"
done

data=/Users/anub229/Documents_/Projects/NMDC/nmdc_sandbox/dummy_code/feb12/nmdc-proteomics-workflow/data/dpkgs/3458/430175
docker run --name proteomicsContainer \
    -v /da:/data:rw \
    -v /tmp/parameters:/parameters:rw \
    -v /tmp/out:/out:rw \
    -it mepro:1.2 /bin/bash

mono /app/masic/MASIC_Console.exe \
/I:/data/*.raw \
/O:/out/ \
/P:/parameters/TMT10_LTQ-FT_10ppm_ReporterTol0.003Da_2014-08-06.xml \
| tee /out/step00_masic.log


docker run -it --rm \
-e WINEDEBUG=-all \
-v $PWD/data:/data:rw \
chambm/pwiz-skyline-i-agree-to-the-vendor-licenses \
wine msconvert /data/test_global/raw/*.raw \
-o /data/test_global/msgfplus_input/


java -Xmx4000M \
-jar /app/msgf/MSGFPlus.jar \
-s /data/test_global/msgfplus_input/MoTrPAC_Pilot_TMT_W_S1_02_12Oct17_Elm_AQ-17-09-02.mzML \
-o /data/test_global/msgfplus_output/MoTrPAC_Pilot_TMT_W_S1_02_12Oct17_Elm_AQ-17-09-02.mzid \
-d /data/ID_007275_FB1B42E8.fasta \
-conf /parameters/MzRef_StatCysAlk_TMT_6plex.txt | tee -a /data/test_global/step02.log


mono /app/mzid2tsv/net462/MzidToTsvConverter.exe \
-mzid:/data/test_global/msgfplus_output/MoTrPAC_Pilot_TMT_W_S1_02_12Oct17_Elm_AQ-17-09-02_final.mzid \
-tsv:/data/test_global/msgfplus_output/MoTrPAC_Pilot_TMT_W_S1_02_12Oct17_Elm_AQ-17-09-02.tsv \
-unroll -showDecoy | tee -a /data/test_global/step05_mzid2tsv.log

mono /app/phrp/PeptideHitResultsProcRunner.exe \
-I:/data/test_global/msgfplus_output/MoTrPAC_Pilot_TMT_W_S1_02_12Oct17_Elm_AQ-17-09-02.tsv \
-O:/data/test_global/phrp_output/ \
-M:/parameters/MSGFPlus_PartTryp_DynMetOx_Stat_CysAlk_TMT_6Plex_20ppmParTol_ModDefs.txt \
-T:/parameters/Mass_Correction_Tags.txt \
-N:/parameters/MSGFPlus_PartTryp_DynMetOx_Stat_CysAlk_TMT_6Plex_20ppmParTol.txt \
-SynPvalue:0.2 -SynProb:0.05 \
-L:/data/test_global/phrp_output/PHRP_LogFile.txt \
-ProteinMods \
-F:/data/ID_007275_FB1B42E8.revCat.fasta | tee -a /data/test_global/step06_phrp.log