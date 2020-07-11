import utils

excelName = '/home/utkarsh/Projects/archive-big-data-dropbox/inputs.xlsx'
sheetName = 'dropboxUpload_APP'

dbx = utils.dropbox(excelName,sheetName,batchSize_GB=20,fileSizeLimit_GB=10,chunkSizeSplit_MB=1024,chunkSizeAPI_MB=256,sleepTime=120,API=False)
dbx.getFileList()
dbx.checkForLargeFiles()
dbx.
