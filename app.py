import dataPrep
import dropbox

excelName = '/home/utkarsh/Projects/archive-big-data-dropbox/inputs.xlsx'
sheetName = 'dropboxUpload_APP'

dp = dataPrep.dataPrep(excelName,sheetName,fileSizeLimit_GB=4,chunkSizeSplit_MB=1024)
dbx = dropbox.dropboxApp(excelName,sheetName,batchSize_GB=10,sleepTime=120,r_wSpeedCutOff=0.5)
