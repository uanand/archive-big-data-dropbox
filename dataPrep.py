import os
import numpy
import pandas
import platform
from tqdm import tqdm

from os.path import isfile,isdir,join,getsize,exists

class dataPrep:
    
    ############################################################
    def __init__(self,excelName,sheetName,fileSizeLimit_GB=100,chunkSizeSplit_MB=1024):
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','dropboxFile']
        self.fileSizeLimit = fileSizeLimit_GB*1024*1024*1024
        self.chunkSizeSplit = chunkSizeSplit_MB*1024*1024
        
        self.chunksInEachSplit = int(numpy.ceil(self.fileSizeLimit/self.chunkSizeSplit))
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
        
        print ('Stage 1 - Data preparation')
        self.getFileList()
        self.checkForLargeFiles()
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
                tempFileNameList,tempFileSizeList = self.getFilesinDir(inputDir)
                for a,b in zip(tempFileNameList,tempFileSizeList):
                    fileNameList.append(a)
                    fileSizeList.append(b)
        self.fileNameList = fileNameList
        self.fileSizeList = fileSizeList
    ############################################################
    
    ############################################################
    def getFilesinDir(self,inputDir):
        fileNameList,fileSizeList = [],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                fileName = os.path.join(root,name)
                fileSize = getsize(fileName)
                fileNameList.append(fileName)
                fileSizeList.append(fileSize)
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
