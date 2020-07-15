import dataPrep
import dropboxBatch
import utils

excelName = '/home/utkarsh/Projects/archive-big-data-dropbox/inputs.xlsx'
sheetName = 'dropboxUpload_APP'

# PARAMETERS FOR DATA PREPARATION AND ARCHIVING
fileSizeLimit_GB = 100
chunkSizeSplit_MB = 1024

# PARAMETERS FOR DATA UPLOAD USING APP
batchSize_GB = 200
sleepTime_s = 120
r_wSpeedCutOff = 0.2

# PARAMETERS FOR DATA UPLOAD USING API
accessToken = '**************' # GET DROPBOX ACCESS TOKEN BY CREATING AN APP HERE - https://www.dropbox.com/developers/apps
chunkSize_MB = 256 # in MB

dp = dataPrep.dataPrep(excelName,sheetName,fileSizeLimit_GB,chunkSizeSplit_MB)
if ('APP' in sheetName):
    dbx = dropboxBatch.dropboxApp(excelName,sheetName,batchSize_GB,sleepTime_s,r_wSpeedCutOff)
elif ('API' in sheetName):
    dbx = dropboxBatch.dropboxAPI(excelName,sheetName,accessToken,chunkSize_MB)
utils.combineLogs()
