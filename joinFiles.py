import pandas
import os
from tqdm import tqdm
import utils

############################################################
# READ THE INPUT EXCEL FILE AND COMBINE THE SPLIT FILES.
############################################################

'''
NOTE THAT THE NAME OF THE FIRST SPLIT OF EVERY FILE SHOULD
BE ENTERED IN THE EXCEL SHEET. FOR EXAMPLE, A LARGE FILE
IS SPLIT INTO 3 PARTS:
    largeFile.zip_split_0001
    largeFile.zip_split_0002
    largeFile.zip_split_0003.
THEN path_to_file\largeFile.zip_split_0001 WITH COMPLETE
PATH SHOULD BE ENTERED IN THE EXCEL FILE.
'''

df = pandas.read_excel('inputs.xlsx',sheet_name='joinFiles',names=['inputFile','deleteFlag'])

chunkSizeMB = 1024 # in MB
chunkSize = chunkSizeMB*1024*1024

for inputFile,deleteFlag in df.values:
    fileName = inputFile.split('_split_0001')[0]
    splitFileList = utils.findSplitFiles(inputFile)
    print ('Combining split files for %s' %(fileName))
    outFile = open(fileName,'wb')
    for splitFile in tqdm(splitFileList):
        inFile = open(splitFile,'rb')
        while (1):
            chunk = inFile.read(chunkSize)
            if not chunk:
                break
            outFile.write(chunk)
        inFile.close()
        if (deleteFlag==1):
            os.remove(splitFile)
    outFile.close()
############################################################
