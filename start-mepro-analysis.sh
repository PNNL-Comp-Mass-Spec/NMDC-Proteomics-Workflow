#!/bin/sh
export DATABASE_USERNAME=dmsreader DATABASE_PASSWORD=dms4fun DATABASE_SERVER=gigasax DATABASE_NAME=DMS5


#storage="/mnt/msshare/Anubhav/storage"
storage="/Volumes/MSSHARE/Anubhav/storage"

# Hess datasets (EMSL48099_JGI1393_Hess_DatasetToMetagenomeMapping.xlsx) @Samuel-purvine
#projectName="Hess"
#datasets="404590, 404522 ,404510 ,404577 ,404531 ,404518 ,404433 ,404445 ,404514 ,404535 ,404418 ,404422 ,404352 ,404365 ,404390 ,367262 ,367259 ,367505 ,367504 ,404637 ,404602 ,405162 ,404646 ,404769 ,404669 ,404757 ,405192 ,404616 ,404799 ,404816 ,404789 ,404779 ,404321 ,404359 ,404386 ,367506 ,367260 ,404241 ,404254 ,404305 ,404227 ,404248 ,404311 ,404232 ,404266 ,404276 ,404237 ,404259 ,404270 ,405262 ,405278 ,405200 ,405204 ,405274 ,405255 ,405266 ,405251 ,405259 ,405270 ,405196 ,405228 ,404347 ,404372 ,404379 ,405287 ,405299 ,405307 ,405330 ,405285 ,405342 ,405311 ,405313 ,405309 ,405346 ,405282 ,405315 ,367261 ,367258"

#projectName="Stegen"
#datasets="500097,500094 ,500162 ,500837 ,500166 ,500093 ,500835 ,500829 ,500160 ,500095 ,501132 ,500088 ,500101 ,500836 ,500164 ,501128 ,500102 ,500098 ,500096 ,500831 ,500163 ,500830 ,500165 ,500099 ,500090 ,500103 ,501138 ,500832 ,500091 ,500833 ,500834 ,500100 ,500161 ,500167"

#projectName="DMS_random"
#datasets="508538, 509161, 509162, 509163, 509166, 509167, 511721, 511723, 511724, 511726, 511727, 511728, 526183, 526184, 526185, 526387, 526388, 526438, 526439, 526440, 526441, 526481, 526482, 526483, 526539, 526540, 526549, 526586, 526587, 526588"

#projectName="DMS_test"
#datasets="430135"

#msgfJobs="1553244, 1553245, 1553246, 1553247, 1553248, 1553249, 1553250, 1553251, 1553252, 1553253, 1553254, 1553255, 1553256, 1553257, 1553258, 1553259, 1553260, 1553261, 1553262, 1553263, 1553264, 1553265, 1553266, 1553267, 1553268, 1553269, 1553270, 1553271, 1553272, 1553273"

#msgfJobs="1712198,1719436,1733175,1733774"
# TODO: Pickup configuration from WorkfkowOptions.xml file

####  Run Mepro : When data is on DMS/EMSL!

# based on datapackage IDs | DMS
#    3021 # @Matt
#    3458 # @yuchian Mint-soil
#    3524 # @paul
dataPackageNum="3524"
python src/MetProWorkflowApp.py  \
      -M developer  \
      -It 1  \
      -S $storage \
      -I $dataPackageNum \
      -C 1
## Based on job numbers | DMS
#python src/MetProWorkflowApp.py  \
#      -M developer  \
#      -It 3  \
#      -S $storage  \
#      -I "$msgfJobs" \
#      -C 1

# Based on dataset_ids | DMS or NMDC-FICUS
#python src/MetProWorkflowApp.py \
#      -M developer \
#      -It 2 \
#      -S $storage \
#      -P $projectName \
#      -I "$datasets"

#### Run Mepro : When data is provided by user directly!
## Front-end drops RAW, FASTA, PARAMETER files in the "Storage"
#python src/MetProWorkflowApp.py \
#      -S $storage

