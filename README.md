# archive-big-data-dropbox
Upload large volume (PB) of data to Dropbox seamlessly

## Introduction
Dropbox has started [paid services](https://www.dropbox.com/business/pricing) which provide unlimited data storage space to its subscribers. This can be useful for small to medium sized businesses which generate large amount of data and do not wish to invest on building their own servers for data management. However, uploading hundreds of terabytes of data to Dropbox servers can be challenging and time consuming primarily due to three reasons -

1. *If the number of files synchronized to [Dropbox exceeds 300,000](https://help.dropbox.com/accounts-billing/space-storage/file-storage-limit) the performance of the desktop application may decline.* To solve this problem, it is recommended to make a zip file from a folder containing a large number of small files.
2. *Dropbox is not good at synchronizing [terabytes of data](https://help.dropbox.com/installs-integrations/desktop/unexpected-quit) at a time.* To solve this problem it is recommended to synchronize the data to Dropbox in small batches (a few hundred GB)
3. *Dropbox desktop app cannot synchronize very large files.*
 Contrary to their claim, Dropbox app cannot synchronize single files if they exceed 600 GB (This number could be smaller but I have done tests on a 600 GB file.) A way to resolve this is to split the large file into smaller chunks and then upload it to Dropbox. The split files can be downloaded and joined together using the python script "joinFiles.py".

This package provides a complete solution to seamlessly archive your data to Dropbox.

## Requirements
* Windows 10
* [Dropbox application](https://www.dropbox.com/install) installed on your computer and linked to the Business account
* [7zip](https://www.7-zip.org/)
* Any office package which can edit and save .xlsx files - [Microsoft Office](https://www.office.com)/[Libre Office](https://www.libreoffice.org)/[Open Office](https://www.openoffice.org)/[WPS Office](https://www.wps.com)
* python >= 3.6.9
    * numpy 1.17.2
    * pandas 0.25.1
    * xlrd 1.2.0
    * tqdm 4.36.1
    * psutil 5.4.2
    * dropbox 10.2.0
    
## Usage
As of now the package is divided into two parts - 1. data compression, and 2. data synchronization with Dropbox.

### Data comression
1. Due to its inability to handle a large number of files, it is recommended to zip a folder containing a large number of small files. For example, suppose the Gatan OneView camera records a movie at 100 fps and stores every frame in a directory '001'. In this case it we will compress the files in the folder '001' and make a new large file '001.zip'.
2. Navigate to the directory preProcess and enter the path of the directory you want to move to Dropbox in the 'listDirToZip' tab of the excel file 'zipDir.xlsx'. Save and run the code "1_listDirToZip.py". This will make a list of all the folders that you should zip before uploading to Dropbox. The directory list is written to file 'directoryZipList.txt'. Typically a 50 TB folder will take around 2 hours to navigate through.
3. Copy the list of directories that need to be zipped to the 'zipDir' tab of excel file 'zipDir.xlsx'. After compression using the [7zip](https://www.7-zip.org/) package the original folders are deleted by default. If there are any additional folders that you think need compressing add them to the list, and run "2_zipDir.py". A 50 TB directory may take upto a week to compress.
4. After completing steps 2 and 3, the files are ready to be moved to Dropbox.

A log file is generated at the end and placed in ./logs/preProcess folder.

### Uploading to Dropbox
This can be done using the Dropbox Windows Desktop application, or using Dropbox's API to upload directly to Dropbox.

#### APP
1. Fill out the 'dropboxUpload_APP' sheet in 'inputs.xlsx'. The first column can be a directory or a file you want to upload. The second column is the local Dropbox directory where you want to upload the data.  
2. Open the python scripy "app.py" and make sure the variable *sheetName* is set as 'dropboxUpload_APP'. Enter the location of *dropboxDir*, and you can change the values for *fileSizeLimit_GB* (Default: 500), *chunkSizeSplit_MB* (Default: 1024), *batchSize_GB* (Default: 1000), *sleepTime_s* (Default: 30, not recommended to change), and *batchTimeLimit_hour* (Default: 24, not recommended to change).
3. Run "app.py". Around 1.5-2 TB of data can be archived in a day.

The script looks at the all the files that need to be uploaded. If any file is bigger than *fileSizeLimit_GB* (default is 500 GB), it is split into smaller pieces. After the data preparation is done the files are uploaded to Dropbox in batches of size *batchSize_GB* (default is 1000 GB). The script pauses if
* Dropbox physical hard drive gets full
* The batch synchronization did not complete in 24 hours (*batchTimeLimit_hour*). This will usually happen if Dropbox application crashes.
* TODO - Dropbox quota reached

A log file is generated at the end and placed in ./logs/dataPrep and ./logs/upload folders.

#### API
1. Fill out the 'dropboxUpload_API' sheet in 'inputs.xlsx'. The first column can be a directory or a file you want to upload. The second column in the server Dropbox directory where you want to upload the data.  
2. Open the python scripy "app.py" and make sure the variable *sheetName* is set as 'dropboxUpload_API'.  
3. Run "app.py".

You will need to generate an access token to your Dropbox by creating a [developer app](https://www.dropbox.com/developers/apps). You can also change the *chunkSize_MB* (default is 128 MB, maximum 150 MB). The data preparation is done exactly the same way but the data is uploaded directly to Dropbox. This method is generally slower. The script pauses if **Dropbox quota reached (TODO)**. A log file is generated at the end and placed in ./logs/upload folder.

### Downloading from Dropbox
Downloading the files from Dropbox is easy. One can select the file and change its Smart Sync status to Local. After downloading all the corresponding split files, they can be joined together using the script "joinFiles.py". Only the name of the first split file needs to be entered, and the script will look for all the subsequent splits and join the files together. After joining the files the zip archive is unzipped and the combined file is deleted. 

## Recap
### Data compression
1. List the folder you want to navigate for compression in the 'listDirToZip' tab in 'zipDir.xlsx' and run "1_listDirToZip.py". Runtime for 50 TB folder is approx. 2 hours.
2. From the output file 'directoryZipList.txt', enter the list of directories for archiving in the 'zipDir' tab in 'zipDir.xlsx' and run "2_zipDir.py". Runtime for 50 TB folder is approx. 1-2 weeks.

### Data uploading
3. In the tab 'dropboxUpload_APP' of 'inputs.xlsx' enter the directory you want to move to Dropbox with its corresponding Dropbox Directory and run "app.py". Runtime for 50 TB data is approx. 1 month.