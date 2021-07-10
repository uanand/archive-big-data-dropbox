import os
import sys

sys.path.append(os.path.abspath('./lib'))

import dataPrep
import dropboxBatch

# INPUT EXCEL FILE NAME WITH CORRESPONDING SHEET FOR DATA UPLOAD
excelName = 'inputs.xlsx'
sheetName = 'dropboxUpload_APP'

# PARAMETERS FOR DATA PREPARATION AND ARCHIVING
fileSizeLimit_GB = 500
chunkSizeSplit_MB = 1024

# PARAMETERS FOR DATA UPLOAD USING APP
dropboxDir = r'E:\Dropbox (NUSCentreofBioImagin)'   # DIRECTORY WHERE DROPBOX SYNC DIRECTORY IS LOCATED
batchSize_GB = 1000
sleepTime_min = 30
batchTimeLimit_hour=24
accessToken = '##############################' # GET DROPBOX ACCESS TOKEN BY CREATING AN APP HERE - https://www.dropbox.com/developers/apps

# PARAMETERS FOR DATA UPLOAD USING API
chunkSize_MB = 128 # in MB

dp = dataPrep.dataPrep(excelName,sheetName,fileSizeLimit_GB,chunkSizeSplit_MB)
if ('APP' in sheetName):
    dbx = dropboxBatch.dropboxApp(excelName,sheetName,dropboxDir,accessToken,batchSize_GB,sleepTime_min,batchTimeLimit_hour)
elif ('API' in sheetName):
    dbx = dropboxBatch.dropboxAPI(excelName,sheetName,accessToken,chunkSize_MB)
