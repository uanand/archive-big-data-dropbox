import dataPrep
import dropbox
import utils

excelName = '/home/utkarsh/Projects/archive-big-data-dropbox/inputs.xlsx'
sheetName = 'dropboxUpload_APP'
fileSizeLimit_GB = 4
chunkSizeSplit_MB = 1024
batchSize_GB = 10
sleepTime = 120
r_wSpeedCutOff = 0.2

dp = dataPrep.dataPrep(excelName,sheetName,fileSizeLimit_GB,chunkSizeSplit_MB)
dbx = dropbox.dropboxApp(excelName,sheetName,batchSize_GB,sleepTime,r_wSpeedCutOff)
utils.combineLogs()
