import os
import sys
import pandas
import subprocess
import platform
import datetime

sys.path.append(os.path.abspath('../lib'))
import utils

############################################################
# READ THE INPUT EXCEL FILE AND ZIP ARCHIVE THE FOLDERS
############################################################
df = pandas.read_excel('zipDir.xlsx',sheet_name='zipDir',names=['inputDir','deleteFlag'],usecols=[0,1])
df = df.dropna(axis=0,how='all')

dirDetails = pandas.read_csv('directorySize.txt',delimiter='\t',names=['dirName','numSubDir','numFiles','size'],header=0)
logFile = open('../logs/preProcess/zipDir.log','w')
logFile.write('Timestamp\tDirectory to zip\tNumber of subdirectories\tNumber of files\tDirectory size (GB)\n')

if (platform.system()=='Linux'):
    executable = '7za'
elif (platform.system()=='Windows'):
    executable = 'C:/Program Files/7-Zip/7z.exe'
for inputDir,deleteFlag in df.values:
    print ('Archiving the folder %s' %(inputDir))
    zipFileName = inputDir+'.zip'
    numSubDir = dirDetails[dirDetails['dirName']==inputDir]['numSubDir']
    numFiles = dirDetails[dirDetails['dirName']==inputDir]['numFiles']
    size = dirDetails[dirDetails['dirName']==inputDir]['size']
    logFile.write('%s\t%s\t%d\t%d\t%.6f\n' %(utils.timestamp(),inputDir,numSubDir,numFiles,size))
    if (deleteFlag==0):
        subprocess.run([executable,'a',zipFileName,inputDir])
    else:
        subprocess.run([executable,'a',zipFileName,inputDir,'-sdel'])
        
logFile.close()
os.rename('../logs/preProcess/zipDir.log','../logs/preProcess/'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'.log')
############################################################
