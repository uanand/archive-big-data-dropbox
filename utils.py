import os
import numpy
import pandas
import platform
from tqdm import tqdm

from os.path import isfile,isdir,join,getsize,exists

class dropbox:
# class dropbox(excelName,sheetName,batchSize_GB=400,fileSizeLimit_GB=100,chunkSizeSplit_MB=1024,chunkSizeAPI_MB=256,sleepTime=120,API=False):
    ############################################################
    def __init__(self,excelName,sheetName,batchSize_GB=400,fileSizeLimit_GB=100,chunkSizeSplit_MB=1024,chunkSizeAPI_MB=256,sleepTime=120,API=False):
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','dropboxFile']
        self.batchSize = batchSize_GB*1024*1024*1024
        self.fileSizeLimit = fileSizeLimit_GB*1024*1024*1024
        self.chunkSizeSplit = chunkSizeSplit_MB*1024*1024
        self.chunkSizeAPI = chunkSizeAPI_MB*1024*1024
        self.sleepTime = sleepTime
        self.API = API
        self.chunksInEachSplit = int(numpy.ceil(self.fileSizeLimit/self.chunkSizeSplit))
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
    ############################################################
    
    ############################################################
    def getFileList(self):
        fileNameList,fileSizeList = [],[]
        for inputFile in self.df.values[:,0]:
            if (os.path.isfile(inputFile)):
                fileSize = os.path.getsize(inputFile)
                fileNameList.append(inputFile)
                fileSizeList.append(fileSize)
            elif (os.path.isdir(inputFile)):
                inputDir = inputFile
                tempFileNameList,tempFileSizeList = self.getFilesinDir(inputDir,sizeFlag=True)
                for a,b in zip(tempFileNameList,tempFileSizeList):
                    fileNameList.append(a)
                    fileSizeList.append(b)
        self.fileNameList = fileNameList
        self.fileSizeList = fileSizeList
    ############################################################
    
    ############################################################
    def getFilesinDir(self,inputDir,outputDir=False,sizeFlag=False,outputFileFlag=False,outputDirFlag=False):
        fileNameList,fileSizeList,outputFileList,outputDirList = [],[],[],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                fileName = os.path.join(root,name)
                if (sizeFlag==True):
                    fileSize = getsize(fileName)
                    fileSizeList.append(fileSize)
                fileNameList.append(fileName)
        return fileNameList,fileSizeList
    ############################################################
    
    ############################################################
    def checkForLargeFiles(self):
        for fileName,fileSize in zip(self.fileNameList,self.fileSizeList):
            if (fileSize>self.fileSizeLimit):
                self.splitFile(fileName)
    ############################################################
    
    ############################################################
    def splitFile(self,fileName):
        fileSize = os.path.getsize(fileName)
        numFiles = int(fileSize/self.fileSizeLimit)+1
        print ('Splitting %s into %d parts' %(fileName,numFiles))
        
        numChunksToRead,splitNum,chunkNum = int(numpy.ceil(fileSize/self.chunkSizeSplit)),1,0
        outputFileName = fileName
        infile = open(fileName,'rb')
        outFile = open(outputFileName+'_split_'+str(splitNum).zfill(4),'wb')
        for i in tqdm(range(numChunksToRead)):
            chunk = infile.read(self.chunkSizeSplit)
            chunkNum += 1
            if (chunkNum<=self.chunksInEachSplit):
                outFile.write(chunk)
            else:
                outFile.close()
                splitNum += 1
                outFile = open(outputFileName+'_split_'+str(splitNum).zfill(4),'wb')
                outFile.write(chunk)
                chunkNum = 1
        outFile.close()
        infile.close()
        os.remove(fileName)
    ############################################################
