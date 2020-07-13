import os
import platform
import datetime

############################################################
def getFileName(inputFile):
    if (platform.system()=='Linux'):
        fileName = inputFile.split('/')[-1]
    elif (platform.system()=='Windows'):
        fileName = inputFile.split('\\')[-1]
    return fileName
############################################################

############################################################
def getDirName(inputFile,name):
    if (platform.system()=='Linux'):
        outputDir = inputFile.replace('/'+name,'')
    elif (platform.system()=='Windows'):
        outputDir = inputFile.replace('\\'+name,'')
    return outputDir
############################################################

############################################################
def mkdirs(dirNameList):
    for dirName in dirNameList:
        if (os.path.exists(dirName)==False):
            os.makedirs(dirName)
############################################################

############################################################
def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
############################################################

############################################################
def combineLogs():
    logList = []
    if os.path.exists('logs/archive.log'):
        logList.append('logs/archive.log')
    if os.path.exists('logs/dataPrep.log'):
        logList.append('logs/dataPrep.log')
    if os.path.exists('logs/dropboxApp.log'):
        logList.append('logs/dropboxApp.log')
    if os.path.exists('logs/dropboxAPI.log'):
        logList.append('logs/dropboxAPI.log')
        
    logFile = open(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'.log','w')
    for log in logList:
        f = open(log,'r')
        logFile.write(f.read())
        f.close()
        os.remove(log)
    logFile.close()
############################################################
