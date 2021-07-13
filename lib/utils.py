import os
import platform
import datetime

############################################################
def getFileName(inputFile):
    """ Get the name of file from full file path.
    
    Parameters:
    ----------
    inputFile : str
        name of the file with file path
        
    Returns:
    -------
    fileName : str
        name of the file
        
    Usage:
    -----
    fileName = splitFile(inputFile)
    """
    
    if (platform.system()=='Linux'):
        fileName = inputFile.split('/')[-1]
    elif (platform.system()=='Windows'):
        fileName = inputFile.split('\\')[-1]
    return fileName
############################################################

############################################################
def getDirName(inputFile,name):
    """ Get the directory where a file is located.
    
    Parameters:
    ----------
    inputFile : str
        name of the file with full file path.
    name : str
        name of the file.
        
    Returns:
    -------
    outputDir : str
        directory where the file is located.
        
    Usage:
    -----
    dirName = getDirName(inputFile,name)
    """
    
    if (platform.system()=='Linux'):
        outputDir = inputFile.replace('/'+name,'')
    elif (platform.system()=='Windows'):
        outputDir = inputFile.replace('\\'+name,'')
    return outputDir
############################################################

############################################################
def mkdirs(dirNameList):
    """ Make directories based on the liat of input directories. If the
    directory exists, nothing is done.
    
    Parameters:
    ----------
    dirNameList : list
        List of directories that need to be created.
        
    Returns:
    -------
    NULL
    
    Usage:
    -----
    mkdirs(dirNameList)
    """
    
    for dirName in dirNameList:
        if (os.path.exists(dirName)==False):
            os.makedirs(dirName)
############################################################

############################################################
def timestamp():
    """ Return the current date time as a string in format
    'YYYYMMDD HH:MM:SS'.
    
    Parameters:
    ----------
    NULL
        
    Returns:
    -------
    Current date  and time.
    
    Usage:
    -----
    dt = timestamp()
    """
    
    return datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
############################################################


############################################################
def getDropboxWebFileName(localDropboxFile,localDropboxDir):
    """ Get the path of the file on Dropbox cloud. If the path of the
    local file is D:\Dropbox\Data\test\image_0001.png, then the
    corresponding file name on Dropbox cloud is
    /Data/test/image_0001.png 
    
    Parameters:
    ----------
    localDropboxFile : str
        File name with path of the local Dropbox file. 
    localDropboxDir : str
        Location of Dropbox directory on the local machine. 
        
    Returns:
    -------
    fileName : str
        File name with path on Dropbox cloud.
    
    Usage:
    -----
    getDropboxWebFileName(localDropboxFile,localDropboxDir)
    """
    
    fileName = localDropboxFile.replace(localDropboxDir,'')
    if (platform.system()=='Windows'):
        fileName = fileName.replace('\\','/')
    return fileName
############################################################


############################################################
def deleteFiles(fileNameList):
    """ Delete a list of files. The file names with complete path
    are accepted as a list and they are deleted. If the file does
    not exist then the function moves on to the next file for
    deletion.
    """
    for fileName in fileNameList:
        if os.path.exists(fileName):
            os.remove(fileName)
        else:
            pass
############################################################


############################################################
def findSplitFiles(inputFile):
    """ Get all the brother split files in the directory.
    
    Parameters:
    ----------
    inputFile : str
        name of the first split file with file path
        
    Returns:
    -------
    splitFileList : list of str
        list of all the other split files
        
    Usage:
    -----
    splitFileList = findSplitFiles(inputFile)
    """
    if (platform.system()=='Linux'):
        tempList = inputFile.split('/')
        path = ''
        for temp in tempList[:-1]:
            path = path+temp+'/'
    elif (platform.system()=='Windows'):
        tempList = inputFile.split('\\')
        path = ''
        for temp in tempList[:-1]:
            path = path+temp+'\\'
    fileName = inputFile.split('_split_0001')[0]+'_split_'
    dirFileList = listdir(path)
    splitFileList = []
    for dirFile in dirFileList:
        if (fileName in path+dirFile):
            splitFileList.append(path+dirFile)
    splitFileList = list(numpy.sort(splitFileList,kind='mergesort'))
    return splitFileList
############################################################