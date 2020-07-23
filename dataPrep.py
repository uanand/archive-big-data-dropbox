import os
import numpy
import pandas
import utils
from tqdm import tqdm

class dataPrep:
    """ dataPrep class has the following functions and variables
    Functions :
        __init__()
        checkForLargeFiles()
        getFileList()
        getFilesinDir()
        spitFile()
        
    Variables :
        excelName (str)- name of the excel file which has the names of
            files and folders that need to be uploaded to Dropbox.
        sheetName (str)- name of the excel sheet that has details of
            files and folders to be uploaded to Dropbox.
        fileSizeLimit (float)- size limit for files. If any file is
            bigger that this it is split into smaller pieces. Default
            is 100 GB.
        chunkSizeSplit (float)- when splitting files size of chunk to
            keep in memory. Default 1024 MB.
        df (pandas dataframe) - First column has the file name or
            directory to be uploaded. Second column has the
            corresponding Dropbox folder name.
            
    Usage:
        import dataPrep
        
        # Example 1
        dp = dataPrep.dataPrep(
            excelName='inputs.xlsx',
            sheetName='dropboxUpload_APP',
            fileSizeLimit_GB=64,
            chunkSizeSplit_MB=256)
        The files and directories in excel sheet will be split into
        smaller pieces if they are larger than 64 GB. During splitting
        256 MB of data will be loaded into the memory at a time.
        
        # Example 2
        dp = dataPrep.dataPrep(
            'inputs.xlsx',
            'dropboxUpload_API')
        Default values for fileSizeLimit_GB and chunkSizeSplit_MB will
        be used which are 100 and 1024 respectively.
    """
    
    ####################################################################
    def __init__(self,excelName,sheetName,fileSizeLimit_GB=100,chunkSizeSplit_MB=1024):
        """ Invoked as soon as an object is initialized. Creates new
        attribute variables and makes a log file dataPrep.log in the
        logs directory.
        
        Call self.self.getFileList() which creates a list of all the
        files that need to be uploaded on Dropbox.
        Call self.checkForLargeFiles() which looks at the size of all
        the files and splits them if required.
        """
        
        self.excelName = excelName
        self.sheetName = sheetName
        self.names = ['inputFile','outputDir']
        self.fileSizeLimit = fileSizeLimit_GB*1024*1024*1024
        self.chunkSizeSplit = chunkSizeSplit_MB*1024*1024
        
        self.chunksInEachSplit = int(numpy.ceil(self.fileSizeLimit/self.chunkSizeSplit))
        self.df = pandas.read_excel(self.excelName,sheet_name=self.sheetName,names=self.names)
        
        print ('Stage 1 - Data preparation')
        self.logFile = open('logs/dataPrep.log','w')
        self.getFileList()
        self.checkForLargeFiles()
        self.logFile.close()
    ####################################################################
    
    ####################################################################
    def getFileList(self):
        """ Use self.df to generate the list of files that need to be
        uploaded to Dropbox.
        
        Usage:
            self.getFileList()
            
        Returns:
            NULL
            Creates two lists
            self.fileNameList - List of all the files uploading to
                Dropbox
            self.fileSizeList - List of corresponding file size in bytes
        """
        
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
    ####################################################################
    
    ####################################################################
    def getFilesinDir(self,inputDir):
        """ Creates a list of files inside a directory
        
        Usage:
            self.getFilesinDir(dir)
            
        Returns:
            fileNameList - List of all the files inside dir
            fileSizeList - List of the corresponding file size in bytes
        """
        
        fileNameList,fileSizeList = [],[]
        for root,dirs,files in os.walk(inputDir):
            for name in files:
                fileName = os.path.join(root,name)
                fileSize = os.path.getsize(fileName)
                fileNameList.append(fileName)
                fileSizeList.append(fileSize)
        return fileNameList,fileSizeList
    ####################################################################
    
    ####################################################################
    def checkForLargeFiles(self):
        """ Scans through all the files in self.fileNameList and splits
        it if the file size is bigger than self.fileSizeLimit
        
        Usage:
            self.checkForLargeFiles()
            
        Returns:
            NULL
            Calls self.splitFile(file) if the file is large
        """
        
        for fileName,fileSize in zip(self.fileNameList,self.fileSizeList):
            if (fileSize>self.fileSizeLimit):
                self.splitFile(fileName)
    ####################################################################
    
    ####################################################################
    def splitFile(self,fileName):
        """ Split a large file into smaller pieces. The size of smaller
        pieces is defined by self.fileSizeLimit
        
        Usage:
            self.splitFile(file)
            
        Returns:
            NULL
            Splits the file into chunks of self.fileSizeLimit and saves
            it in the same directory. fileName_split_0001,
            fileName_split_0002, ... is added at the end of each split.
            The original file is deleted after splitting.
        """
        
        fileSize = os.path.getsize(fileName)
        numFiles = int(fileSize/self.fileSizeLimit)+1
        print ('Splitting %s into %d parts' %(fileName,numFiles))
        self.logFile.write('%s\tSplit %s into %d parts\n' %(utils.timestamp(),fileName,numFiles))
        
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
    ####################################################################
