import os
import numpy
import pandas
import psutil
import shutil
import utils
import time
import dropbox
import datetime
from tqdm import tqdm

exclusionList = [
    'desktop.ini',\
    'thumbs.db',\
    'Thumbs.db',\
    '.ds_store',\
    '.DS_Store',\
    '._.DS_Store',\
    '.dropbox',\
    '.dropbox.attr'\
    ]

############################################################
class dropboxApp:
    """ dropboxApp class has the following functions and variables
    
    Parameters:
    ----------
    excelName : str
        name of the excel file which has the names of files and folders
        that need to be uploaded to Dropbox.
    sheetName : str
        name of the excel sheet that has details of files and folders to
        be uploaded to Dropbox.
    dropboxDir : str
        location of the local Dropbox directory.
    batchSize_GB : float
        Size of each upload batch in GB. Default is 200 GB.
    sleepTime : float
        Duration in seconds after which sync check is performed. Default
        is 120 s. If Dropbox is busy then the same batch will continue
        to upload. Otherwise, work on next batch is started.
    r_wSpeedCutOff : float
        Average disk r/w speed cutoff to check Dropbox availability. If
        r/w < 0.5 (Default), Dropbox is free to work on next batch,
        otherwise uploading of same batch continues.
    accessToken : str
        Access token to access Dropbox using API.
        
    Methods:
    -------
    getFileList()
    getFilesInDir(inputDir,outputDir)
    makeBatches()
    uploadFiles()
    checkResource()
    droboxFree()
    storageFree()
    dropboxRunning()
    dropboxStorageFree()
    checkFilesOnWebsite(fileNameList,accessToken)
    
    Attributes:
    ----------
    df : pandas dataframe
        First column has the file name or directory to be uploaded.
        Second column has the corresponding Dropbox folder name.
    dropboxDir : str
        Location of local Dropbox directory.
    batchSize : float
        Maximum size (in bytes) of a batch during upload.
    sleepTime : float
        Time interval in seconds between when the r/w speed of Dropbox
        application is calculated.
    r_wSpeedCutOff : float
        Cutoff speed below which it is assumed Dropbox is available to
        upload the next batch.
    accessToken : str
        For API access for additional check file upload.
    fileNameList : array of string
        List of all the files to be uploaded to Dropbox.
    fileSizeList : array of float
        Corresponding size in bytes of all the files.
    dropboxFileList : array of str
        Corresponsing file name with full path for the Dropbox
        directory.
    dropboxWebFileList : array of str
        Corresponding file name with full path on the Dropbox servers.
    dropboxDirList : array of str
        List of directories in the Dropbox folder that need to be
        created before data upload start.
        
    Usage:
    -----
    import dropboxBatch
    
    # Example 1
    dbx = dropboxBatch.dropboxApp(
            excelName='inputs.xlsx',,
            sheetName='dropboxUpload_APP',
            dropboxDir=r'E:\Dropbox',
            accessToken='***********',
            batchSize_GB=20,
            sleepTime_s=150,
            r_wSpeedCutOff=1)
    The files and directories in excel sheet will be split batches of 20
    GB and uploaded to Dropbox sequentially. The next batch does not
    start until the current batch is fully uploaded.
    
    # Example 2
    dbx = dropboxBatch.dropboxApp(
            excelName='inputs.xlsx',,
            sheetName='dropboxUpload_APP',
            dropboxDir=r'E:\Dropbox',
            accessToken='***********')
    Default values for batchSize_GB, sleepTime_s, and r_wSpeedCutOff
    are used which are 200, 120, and 0.5 respectively.
    """
    
    ############################################################
    def __init__(self,excelName,sheetName,dropboxDir,accessToken,batchSize_GB=500,sleepTime_min=30,batchTimeLimit_hour=12):
        """ Creates attribute variables and makes a log file
        dropboxApp.log in the logs directory.
        
        Uploads files to Dropbox using the desktop APP in batches.
        """
        
        self.excelName = excelName
        self.sheetName = sheetName
        self.dropboxDir = dropboxDir
        self.accessToken = accessToken
        self.batchSize = batchSize_GB*1024*1024*1024
        self.sleepTime_min = sleepTime_min
        self.batchTimeLimit_hour = batchTimeLimit_hour
        self.names = ['inputFile','outputDir']
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
        self.dbx = dropbox.Dropbox(self.accessToken)
        
        print ('Stage 2 - Data upload using APP')
        logFile = open('./logs/upload/dropboxApp.log','w')
        logFile.write('%s\tData upload using APP\n' %(utils.timestamp()))
        logFile.close()
        self.getFileList()
        utils.mkdirs(self.dropboxDirList)
        self.makeBatches()
        self.uploadFiles()
        os.rename('./logs/upload/dropboxApp.log','./logs/upload/'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'.log')
    ############################################################
    
    ############################################################
    def getFileList(self):
        """ Use self.df to generate the list of files that need to be
        uploaded to Dropbox. In addition to this the corresponding
        file size, file on local Dropbox, file on Dropbox website, and
        the new directories on local Dropbox that need to be made are
        created.
        
        Usage:
        -----
        self.getFileList()
        
        Returns:
        -------
            NULL
            
        Creates:
        -------
        self.fileNameList : array of str
            List of all the files uploading to Dropbox.
        self.fileSizeList : array of float
            List of corresponding file size in bytes.
        self.dropboxFileList : array of str
            List of corresponding files with local Dropbox path.
        self.dropboxWebFileList : array of str
            List of corresponding files with cloud Dropbox path.
        self.dropboxDirList : array of str
            List of local Dropbox directories that need to be created.
        """
        
        fileNameList,fileSizeList,dropboxFileList,dropboxWebFileList,dropboxDirList = [],[],[],[],[]
        for inputFile,outputDir in self.df.values:
            if (os.path.isfile(inputFile)):
                fileSize = os.path.getsize(inputFile)
                fileNameList.append(inputFile)
                fileSizeList.append(fileSize)
                dropboxFileList.append(outputDir+'/'+utils.getFileName(inputFile))
                dropboxWebFileList.append(utils.getDropboxWebFileName(outputDir+'/'+utils.getFileName(inputFile),self.dropboxDir))
                dropboxDirList.append(outputDir)
            elif (os.path.isdir(inputFile)):
                inputDir = inputFile
                tempFileNameList,tempFileSizeList,tempDropboxFileList,tempDropboxWebFileList,tempDropboxDirList = self.getFilesInDir(inputDir,outputDir)
                for a,b,c,d,e in zip(tempFileNameList,tempFileSizeList,tempDropboxFileList,tempDropboxWebFileList,tempDropboxDirList):
                    fileNameList.append(a)
                    fileSizeList.append(b)
                    dropboxFileList.append(c)
                    dropboxWebFileList.append(d)
                    dropboxDirList.append(e)
        self.fileNameList = numpy.asarray(fileNameList)
        self.fileSizeList = numpy.asarray(fileSizeList)
        self.dropboxFileList = numpy.asarray(dropboxFileList)
        self.dropboxWebFileList = numpy.asarray(dropboxWebFileList)
        self.dropboxDirList = numpy.unique(dropboxDirList)
    ############################################################
    
    ############################################################
    def getFilesInDir(self,inputDir,outputDir):
        """ Creates a list of files inside a directory and the
        corresponding files in the local Dropbox directory.
        
        Usage:
        -----
        self.getFilesinDir(inputDir,targetDir)
        
        Returns:
        -------
        fileNameList : array of str
            List of all the files uploading to Dropbox.
        fileSizeList : array of float
            List of corresponding file size in bytes.
        dropboxFileList : array of str
            List of corresponding files with local Dropbox path.
        dropboxWebFileList : array of str
            List of corresponding files with cloud Dropbox path.
        dropboxDirList : array of str
            List of local Dropbox directories that need to be created.
        """
        
        fileNameList,fileSizeList,dropboxFileList,dropboxWebFileList,dropboxDirList = [],[],[],[],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                if (name not in exclusionList):
                    fileName = os.path.join(root,name)
                    fileSize = os.path.getsize(fileName)
                    dropboxFile = fileName.replace(inputDir,outputDir)
                    dropboxWebFile = utils.getDropboxWebFileName(dropboxFile,self.dropboxDir)
                    dropboxDir = utils.getDirName(dropboxFile,name)
                    fileNameList.append(fileName)
                    fileSizeList.append(fileSize)
                    dropboxFileList.append(dropboxFile)
                    dropboxWebFileList.append(dropboxWebFile)
                    dropboxDirList.append(dropboxDir)
        return fileNameList,fileSizeList,dropboxFileList,dropboxWebFileList,dropboxDirList
    ############################################################
    
    ############################################################
    def makeBatches(self):
        """ Splits the files to upload into smaller batches of size
        self.batchSize.
        
        Usage:
        -----
        self.makeBatches()
        
        Returns:
        -------
        NULL
        
        Creates:
        -------
        self.fileNameBatch : list of list of str
            List of files split in batches. Each list element contains
            an array of files in a single batch.
        self.fileSizeBatch : list of list of float
            Corresponding file sizes.
        self.dropboxFileBatch : list of list of str
            Corresponding local Dropbox file name with full path.
        self.dropboxWebFileBatch : list of list of str
            Corresponding Dropbox cloud file name with full path.
        self.numBatches : float
            Total number of batches to be uploaded.
        """
        
        fileNameBatch,fileSizeBatch,dropboxFileBatch,dropboxWebFileBatch = [],[],[],[]
        l1,l2,l3,l4,totalSize = [],[],[],[],0
        lastFileIncluded = False
        for fileName,fileSize,dropboxFile,dropboxWebFile in zip(self.fileNameList,self.fileSizeList,self.dropboxFileList,self.dropboxWebFileList):
            totalSize += fileSize
            if (totalSize <= self.batchSize):
                l1.append(fileName)
                l2.append(fileSize)
                l3.append(dropboxFile)
                l4.append(dropboxWebFile)
            elif (totalSize > self.batchSize):
                fileNameBatch.append(l1)
                fileSizeBatch.append(l2)
                dropboxFileBatch.append(l3)
                dropboxWebFileBatch.append(l4)
                l1,l2,l3,l4,totalSize = [],[],[],[],0
                l1.append(fileName)
                l2.append(fileSize)
                l3.append(dropboxFile)
                l4.append(dropboxWebFile)
                totalSize += fileSize
            if (fileName == self.fileNameList[-1]):
                fileNameBatch.append(l1)
                fileSizeBatch.append(l2)
                dropboxFileBatch.append(l3)
                dropboxWebFileBatch.append(l4)
        self.fileNameBatch = fileNameBatch
        self.fileSizeBatch = fileSizeBatch
        self.dropboxFileBatch = dropboxFileBatch
        self.dropboxWebFileBatch = dropboxWebFileBatch
        self.numBatches = len(fileNameBatch)
    ############################################################
    
    ############################################################
    def uploadFiles(self):
        """ Uploads the batches using Dropbox App one by one.
        self.checkResource() is called repeatedly. If resources are
        available it a second verification is done if the files from
        current batch have uploaded successfully using
        self.checkFilesOnWebsite(). Only then, the next batch is
        submitted for upload.
        
        Usage:
        -----
        self.uploadFiles()
        
        Returns:
        -------
        NULL
        """
        
        for i in range(self.numBatches):
            if (self.storageFree()==True):
                print ('Uploading batch %d/%d' %(i+1,self.numBatches))
                logFile = open('./logs/upload/dropboxApp.log','a')
                logFile.write('%s\tUploading batch %d/%d\n' %(utils.timestamp(),i+1,self.numBatches))
                logFile.close()
                tic = time.time()
                for fileName,fileSize,dropboxFile in zip(self.fileNameBatch[i],self.fileSizeBatch[i],self.dropboxFileBatch[i]):
                    print ('%s\tMoving %s\tto\t%s' %(utils.timestamp(),fileName,dropboxFile))
                    logFile = open('./logs/upload/dropboxApp.log','a')
                    logFile.write('%s\t%s\t%s\t%.6f GB\n' %(utils.timestamp(),fileName,dropboxFile,fileSize/1024/1024/1024))
                    logFile.close()
                    shutil.move(fileName,dropboxFile)
                uploadStatus = False
                self.filesRemaining = self.dropboxWebFileBatch[i]
                while (uploadStatus==False):
                    time.sleep(self.sleepTime_min*60)
                    uploadStatus = self.checkFilesOnWebsite()
                    toc = time.time()
                    timeElapsed = (toc-tic)/60/60
                    if (timeElapsed > self.batchTimeLimit_hour):
                        logFile = open('./logs/upload/dropboxApp.log','a')
                        logFile.write('%s\tCurrent batch upload incomplete\n' %(utils.timestamp()))
                        logFile.close()
                        input('Batch not uploaded! Make sure to finish batch sync and press enter to continue ...')
                        uploadStatus = True
    ############################################################
    
    ############################################################
    def storageFree(self):
        """ Checks availability of hard drive space. If there is space
        to proceed with the next batch returns True otherwise False.
        
        Usage:
        -----
        self.storageFree()
        
        Returns:
        -------
        bool (True/False)
        """
        
        free = False
        availableSpace = psutil.disk_usage(self.dropboxDir).free
        if (availableSpace >= 2*self.batchSize):
            free = True
        else:
            logFile = open('./logs/upload/dropboxApp.log','a')
            logFile.write('%s\tDisk full\n' %(utils.timestamp()))
            logFile.close()
            input('Disk is full. Move data to online-only mode. Press enter to continue after more space is available.')
        return free
    ############################################################
    
    ############################################################
    def dropboxStorageFree(self):
        # TODO - Will need Dropbox API access for this
        pass
    ############################################################
    
    ############################################################
    def checkFilesOnWebsite(self):
        """ Checks if all the files in current batch have been properly
        uploaded to cloud. If not, then the program pauses and waits for
        user to make sure Dropbox is running smoothly and batch sync is
        complete. The functions accepts one argument - list of files on
        Dropbox cloud that need to be checked.
        
        Usage:
        -----
        self.checkFilesOnWebsite()
        
        Returns:
        -------
        NULL
        """
        
        filesUploadFlag = True
        uploadedFileList = []
        for fileName in self.filesRemaining:
            try:
                tt = self.dbx.files_get_metadata(fileName)
                print ('%s Upload successful - %s' %(utils.timestamp(),fileName))
                uploadedFileList.append(fileName)
            except:
                filesUploadFlag = False
                print ('%s Upload ongoing - %s' %(utils.timestamp(),fileName))
                break
        for fileName in uploadedFileList:
            self.filesRemaining.remove(fileName)
        return filesUploadFlag
    ############################################################
############################################################


############################################################
class dropboxAPI:
    """ dropboxAPI class has the following functions and variables
    
    Parameters:
    ----------
    excelName : str
        name of the excel file which has the names of files and folders
        that need to be uploaded to Dropbox.
    sheetName : str
        name of the excel sheet that has details of files and folders to
        be uploaded to Dropbox.
    accessToken : str
        Access token to access Dropbox using API.
    chunkSize_MB : float
        A large file will be uploaded in smaller pieces of a size
        defined by this.
        
    Methods:
    -------
    getFileList()
    getFilesInDir(inputDir,outputDir)
    mkdirs()
    uploadFiles()
    dropboxStorageFree()
    
    Attributes:
    ----------
    df : pandas dataframe
        First column has the file name or directory to be uploaded.
        Second column has the corresponding Dropbox folder name.
    accessToken : str
        For API access for additional check file upload.
    fileNameList : array of string
        List of all the files to be uploaded to Dropbox.
    fileSizeList : array of float
        Corresponding size in bytes of all the files.
    dropboxFileList : array of str
        Corresponsing file name with full path for the cloud Dropbox
        directory.
    dropboxDirList : array of str
        List of directories in the Dropbox folder that need to be
        created before data upload start.
        
    Usage:
    -----
    import dropboxBatch
    
    # Example 1
    dbx = dropboxBatch.dropboxAPI(
            excelName='inputs.xlsx',,
            sheetName='dropboxUpload_API',
            accessToken='***********',
            chunkSize_MB=150)
    The files and directories in excel sheet will uploaded directly to
    Dropbox. Large files will be uploaded in multiple smaller pieces of
    size 150 MB.
    
    # Example 2
    dbx = dropboxBatch.dropboxApp(
            excelName='inputs.xlsx',,
            sheetName='dropboxUpload_API',
            accessToken='***********')
    Default values for chunkSize_MB = 128 will be used during upload.
    """
    
    ############################################################
    def __init__(self,excelName,sheetName,accessToken,chunkSize_MB):
        """ Creates attribute variables and makes a log file
        dropboxAPI.log in the logs directory.
        
        Uploads files sequentially to Dropbox using API.
        """
        
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','outputDir']
        self.accessToken = accessToken
        self.chunkSize = chunkSize_MB*1024*1024
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
        
        print ('Stage 2 - Data upload using API')
        logFile = open('logs/dropboxAPI.log','w')
        logFile.write('%s\tStage 2 - Data upload using API\n' %(utils.timestamp()))
        self.dbx = dropbox.Dropbox(accessToken)
        self.getFileList()
        self.mkdirs()
        self.uploadFiles()
        logFile.close()
    ############################################################
    
    ############################################################
    def getFileList(self):
        """ Use self.df to generate the list of files that need to be
        uploaded to Dropbox. In addition to this the corresponding
        file size, file on Dropbox cloud, and the new directories on
        cloud Dropbox that need to be made are created.
        
        Usage:
        -----
        self.getFileList()
        
        Returns:
        -------
        NULL
            
        Creates:
        -------
        self.fileNameList : array of str
            List of all the files uploading to Dropbox.
        self.fileSizeList : array of float
            List of corresponding file size in bytes.
        self.dropboxFileList : array of str
            List of corresponding files with cloud Dropbox path.
        self.dropboxDirList : array of str
            List of cloud Dropbox directories that need to be created.
        """
        
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
        """ Creates a list of files inside a directory and the
        corresponding files in the local Dropbox directory.
        
        Usage:
        -----
        self.getFilesinDir(inputDir,targetDir)
        
        Returns:
        -------
        fileNameList : array of str
            List of all the files uploading to Dropbox.
        fileSizeList : array of float
            List of corresponding file size in bytes.
        dropboxFileList : array of str
            List of corresponding files with cloud Dropbox path.
        dropboxDirList : array of str
            List of cloud Dropbox directories that need to be created.
        """
        
        fileNameList,fileSizeList,dropboxFileList,dropboxDirList = [],[],[],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                if (name not in exclusionList):
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
    def mkdirs(self):
        """ Creates a list of directories on Dropbox cloud.
        
        Usage:
        -----
        self.mkdirs()
        
        Returns:
        -------
        NULL
        """
        
        for dropboxDir in self.dropboxDirList:
            try:
                self.dbx.files_create_folder(dropboxDir,autorename=False)
            except:
                pass
    ############################################################
    
    ############################################################
    def uploadFiles(self):
        """ Uploads files to cloud using Dropbox API. If the upload
        fails, it is attempted again for a maximum of three times
        before moving on to the next file. A large file is read in
        smaller chunks and uploaded.
        
        Usage:
        -----
        self.uploadFiles()
        
        Returns:
        -------
        NULL
        """
        
        for fileName,fileSize,dropboxFile in zip(self.fileNameList,self.fileSizeList,self.dropboxFileList):
            if not(self.dropboxStorageFree(fileSize)):
                input('Dropbox cloud full. Make sure you have enough space and press enter.')
                
            print ('Uploading %s\tto\t%s' %(fileName,dropboxFile))
            numChunks = int(numpy.ceil(fileSize/self.chunkSize))
            attemptCounter,success = 1,False
            while (attemptCounter<=3 and success==False):
                try:
                    f = open(fileName,'rb')
                    if (numChunks==1):
                        self.dbx.files_upload(f.read(),dropboxFile)
                    else:
                        for i in tqdm(range(numChunks)):
                            chunk = f.read(self.chunkSize)
                            if (i==0):
                                upload_session_start_result = self.dbx.files_upload_session_start(chunk)
                                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,offset=f.tell())
                                commit = dropbox.files.CommitInfo(path=dropboxFile)
                            elif (i==numChunks-1):
                                self.dbx.files_upload_session_finish(chunk,cursor,commit)
                            else:
                                self.dbx.files_upload_session_append(chunk,cursor.session_id,cursor.offset)
                                cursor.offset = f.tell()
                    f.close()
                    os.remove(fileName)
                    logFile.write('%s\t%s\t%s\t%.6f GB\tSuccess\n' %(utils.timestamp(),fileName,dropboxFile,fileSize/1024/1024/1024))
                    success=True
                except:
                    logFile.write('%s\t%s\t%s\t%.6f GB\tFailed\n' %(utils.timestamp(),fileName,dropboxFile,fileSize/1024/1024/1024))
                    print ("Error uploading %s. Trying again." %(fileName))
                    attemptCounter += 1
                    f.close()
    ############################################################
    
    ############################################################
    def dropboxStorageFree(self,fileSize):
        # TODO
        return True
    ############################################################
