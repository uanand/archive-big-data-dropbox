import dataPrep
import dropbox

excelName = '/home/utkarsh/Projects/archive-big-data-dropbox/inputs.xlsx'
sheetName = 'dropboxUpload_APP'

dp = dataPrep.dataPrep(excelName,sheetName,fileSizeLimit_GB=4,chunkSizeSplit_MB=1024)
dbx = dropbox.dropbox(excelName,sheetName,batchSize_GB=10,sleepTime=120,r_wSpeedCutOff=0.5)
# dbx = utils.dropbox(excelName,sheetName,batchSize_GB=20,fileSizeLimit_GB=10,chunkSizeSplit_MB=1024,chunkSizeAPI_MB=256,sleepTime=120,API=False)
