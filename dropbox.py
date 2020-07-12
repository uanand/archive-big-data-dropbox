import os
import numpy
import pandas
import platform
from tqdm import tqdm

import utils

class dropbox:
    
    ############################################################
    def __init__(self,excelName,sheetName,batchSize_GB=400,sleepTime=120):
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','outputDir']
        self.batchSize = batchSize_GB*1024*1024*1024
        self.sleepTime = sleepTime
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
    ############################################################
    
    ############################################################
    def getAllFiles(self):
        fileNameList,fileSizeList,dropBoxFileList,dropBoxDirList = [],[],[],[]
        for inputFile,outputDir in self.df.values:
            if (os.path.isfile(inputFile)):
                fileSize = os.path.getsize(inputFile)
                fileNameList.append(inputFile)
                fileSizeList.append(fileSize)
                dropboxFileList.append(outputDir+'/'+utils.getFileName(inputFile))
                dropboxDirList.append(outputDir)
            elif (os.path.isdir(inputFile)):
                inputDir = inputFile
                tempFileNameList,tempFileSizeList,tempDropboxFileList,tempDropboxDirList = self.getFilesInDir(inputDir,outputDir)
                for a,b,c,d in zip(tempFileNameList,tempFileSizeList,tempDropboxFileList,tempDropboxDirList):
                    fileNameList.append(a)
                    fileSizeList.append(b)
                    dropboxFileList.append(c)
                    dropboxDirList.append(d)
        self.fileNameList = numpy.asarray(fileNameList)
        self.fileSizeList = numpy.asarray(fileSizeList)
        self.dropboxFileList = numpy.asarray(dropboxFileList)
        self.dropboxDirList = numpy.unique(dropboxDirList)
    ############################################################
    
    ############################################################
    def getFilesInDir(self,inputDir,outputDir):
        fileNameList,fileSizeList,dropboxFileList,dropboxDirList = [],[],[],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                fileName = os.path.join(root,name)
                fileSize = getsize(fileName)
                dropboxFile = inputFile.replace(inputDir,outputDir)
                dropboxDir = utils.getDirName(inputFile,name)
                fileNameList.append(fileName)
                fileSizeList.append(fileSize)
                dropboxFileList.append(dropboxFile)
                dropboxDirList.append(dropboxDir)
        return fileNameList,fileSizeList,dropboxFileList,dropboxDirList
    ############################################################
    
    # ############################################################
    # def getFileList(self,dropboxDirFlag=True):
        # fullFileNameList,fileSizeList,dropBoxDirList, = [],[]
        # for inputFile,dropboxDir in self.df.values:
            # if (os.path.isfile(inputFile)):
                # fileSize = os.path.getsize(inputFile)
                # fullFileNameList.append(inputFile)
                # fileSizeList.append(fileSize)
                # if (dropboxDirFlag==True):
                    # if (platform.system()=='Linux'):
                        # fileName = inputFile.split('/')[-1]
                    # elif (platform.system()=='Windows'):
                        # fileName = inputFile.split('\\')[-1]
                    # dropBoxDirList.append(dropboxDir)
                    # dropboxFileList.append(dropboxDir+'/'+fileName)
            # elif (os.path.isdir(inputFile)):
                # inputDir = inputFile
                # tempFileNameList,tempFileSizeList, = self.getFilesinDir(inputDir,dropboxDir,dropboxDirFlag)
                # for a,b in zip(tempFileNameList,tempFileSizeList):
                    # fullFileNameList.append(a)
                    # fileSizeList.append(b)
        # self.fullFileNameList = fullFileNameList
        # self.fileSizeList = fileSizeList
    # ############################################################
    
    # ############################################################
    # def getFilesinDir(self,inputDir,outputDir=None):
        # if (outputDir==None):
            # fileNameList,fileSizeList = [],[]
            # for root,dirs,files in os.walk(inputDir):
                # for name in files:
                    # fileName = os.path.join(root,name)
                    # fileSize = getsize(fileName)
                    # fileNameList.append(fileName)
                    # fileSizeList.append(fileSize)
            # return fileNameList,fileSizeList
        # else:
            # fileNameList,fileSizeList,outputFileList,outputDirList = [],[],[],[]
            # for root,dirs,files in os.walk(inputDir):
                # for name in files:
                    # fileName = os.path.join(root,name)
                    # fileSize = getsize(fileName)
                    # uploadFileName = fileName.replace(inputDir,)
                    # fileNameList.append(fileName)
                    # fileSizeList.append(fileSize)
            # return fileNameList,fileSizeList
    # ############################################################
