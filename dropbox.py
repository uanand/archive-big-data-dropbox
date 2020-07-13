import os
import numpy
import pandas
import platform
import psutil
import shutil
import utils
import time

class dropboxApp:
    
    ############################################################
    def __init__(self,excelName,sheetName,batchSize_GB=400,sleepTime=120,r_wSpeedCutOff=0.5):
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','outputDir']
        self.batchSize = batchSize_GB*1024*1024*1024
        self.sleepTime = sleepTime
        self.r_wSpeedCutOff = r_wSpeedCutOff
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
        
        print ('Stage 2 - Data upload')
        self.logFile = open('logs/dropboxApp.log','w')
        self.getFileList()
        utils.mkdirs(self.dropboxDirList)
        self.makeBatches()
        self.uploadFiles()
        self.logFile.close()
    ############################################################
    
    ############################################################
    def getFileList(self):
        fileNameList,fileSizeList,dropboxFileList,dropboxDirList = [],[],[],[]
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
                fileSize = os.path.getsize(fileName)
                dropboxFile = fileName.replace(inputDir,outputDir)
                dropboxDir = utils.getDirName(dropboxFile,name)
                fileNameList.append(fileName)
                fileSizeList.append(fileSize)
                dropboxFileList.append(dropboxFile)
                dropboxDirList.append(dropboxDir)
        return fileNameList,fileSizeList,dropboxFileList,dropboxDirList
    ############################################################
    
    ############################################################
    def makeBatches(self):
        fileNameBatch,fileSizeBatch,dropboxFileBatch = [],[],[]
        l1,l2,l3,totalSize = [],[],0
        lastFileIncluded = False
        for fileName,fileSize,dropboxFile in zip(self.fileNameList,self.fileSizeList,self.dropboxFileList):
            totalSize += fileSize
            if (totalSize <= self.batchSize):
                l1.append(fileName)
                l2.append(fileSize)
                l3.append(dropboxFile)
            elif (totalSize > self.batchSize):
                fileNameBatch.append(l1)
                fileSizeBatch.append(l2)
                dropboxFileBatch.append(l3)
                l1,l2,l3,totalSize = [],[],[],0
                l1.append(fileName)
                l2.append(fileSize)
                l3.append(dropboxFile)
                totalSize += fileSize
            if (fileName == self.fileNameList[-1]):
                fileNameBatch.append(l1)
                fileSizeBatch.append(l2)
                dropboxFileBatch.append(l3)
        self.fileNameBatch = fileNameBatch
        self.fileSizeBatch = fileSizeBatch
        self.dropboxFileBatch = dropboxFileBatch
        self.numBatches = len(fileNameBatch)
    ############################################################
    
    ############################################################
    def uploadFiles(self):
        for i in range(self.numBatches):
            resourceAvailable = False
            while (resourceAvailable == False):
                resourceAvailable = self.checkResource()
            print ('Uploading batch %d/%d' %(i+1,self.numBatches))
            self.logFile.write('%s\tUploading batch %d/%d\n' %(utils.timestamp(),i+1,self.numBatches))
            for fileName,fileSize,dropboxFile in zip(self.fileNameBatch[i],self.fileSizeBatch[i],self.dropboxFileBatch[i]):
                print ('Moving %s\tto\t%s' %(fileName,dropboxFile))
                self.logFile.write('%s\t%s\t%s\t%.6f GB\n' %(utils.timestamp(),fileName,dropboxFile,fileSize/1024/1024/1024))
                shutil.move(fileName,dropboxFile)
    ############################################################
    
    ############################################################
    def checkResource(self):
        resourceAvailable = False
        if (self.droboxFree() and self.storageFree() and self.dropboxRunning()): # and self.dropboxStorageFree()
            resourceAvailable = True
        return resourceAvailable
    ############################################################
    
    ############################################################
    def droboxFree(self):
        free,failed = False,False
        read_speed,write_speed = 0,0
        try:
            for process in psutil.process_iter():
                if (platform.system() == 'Windows'):
                    processName = 'Dropbox.exe'
                elif (platform.system() == 'Linux'):
                    processName = 'dropbox'
                if (process.name() == processName):
                    read_bytes_0 = process.io_counters().read_bytes
                    write_bytes_0 = process.io_counters().write_bytes
                    time.sleep(self.sleepTime)
                    read_bytes_1 = process.io_counters().read_bytes
                    write_bytes_1 = process.io_counters().write_bytes
                    read_speed = max(read_speed,(read_bytes_1-read_bytes_0)/1024/1024/self.sleepTime)
                    write_speed = max(write_speed,(write_bytes_1-write_bytes_0)/1024/1024/self.sleepTime)
        except:
            failed = True
        if (failed==True):
            free = False
        elif (read_speed < self.r_wSpeedCutOff and write_speed < self.r_wSpeedCutOff):
            free = True
        return free
    ############################################################
    
    ############################################################
    def storageFree(self):
        free = False
        availableSpace = psutil.disk_usage(self.dropboxDirList[0]).free
        if (availableSpace >= 2*self.batchSize):
            free = True
        else:
            self.logFile.write('%s\tDisk full\n' %(utils.timestamp()))
            input('Disk is full. Move data to online-only mode. Press enter to continue after more space is available.')
        return free
    ############################################################
    
    ############################################################
    def dropboxRunning(self):
        running = False
        counter = 0
        for process in psutil.process_iter():
            if (platform.system()=='Windows'):
                if (process.name() == 'Dropbox.exe'):
                    counter += 1
            elif (platform.system()=='Linux'):
                if (process.name() == 'dropbox'):
                    counter += 1
        if (counter>=1):
            running = True
        else:
            self.logFile.write('%s\tDropbox not running\n' %(utils.timestamp()))
            input('Dropbox not running. Make sure to start application. Press enter to continue after application starts.')
        return running
    ############################################################
    
    ############################################################
    def dropboxStorageFree(self):
        # TODO
        pass
    ############################################################
    
