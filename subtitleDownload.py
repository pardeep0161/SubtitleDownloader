import urllib.request
import re
import sys
import subprocess
from subprocess import Popen, PIPE
import os
import zipfile
import time
import shutil
import fnmatch
import sys
from re import search


fullPath = sys.argv[1]
moviename=fullPath[fullPath.rindex('\\')+1:fullPath.rindex('.')]
movieSearchName=re.search(r'(.+)[.]{1}\d{4}[.]{1}',moviename)


openSubtitleSearchURL = 'https://www.opensubtitles.org/en/search2/sublanguageid-eng/moviename-' + movieSearchName.group()
idmEXEDir = "c: \n cd C:\Program Files (x86)\Internet Download Manager"
path_to_zip_file = r"C:\Users\RAD\Downloads\Compressed\srtzip.zip"
directory_to_extract_to = r"C:\Users\RAD\Downloads\Compressed\srtzip"
destination = fullPath[:fullPath.rindex('\\')] + "\\" + moviename +".srt"
movieID = ""



def findSRTFile():
    result = []
    for root, dirs, files in os.walk(directory_to_extract_to):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.srt"):
                result.append(os.path.join(root, filename))
    return result  

def downloadInIDMOnBasisOfMovieID(movieID):
    openSubtitleDLURL = 'https://dl.opensubtitles.org/en/download/sub/' + movieID
    idmURL = "idman.exe /n /f srtzip.zip /d " + openSubtitleDLURL
    cmd = idmEXEDir + " \n " + idmURL + " \n "
    process = Popen( "cmd.exe", shell=False, universal_newlines=True,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE )                             
    out, err = process.communicate( cmd )
    time.sleep(5)
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()
    os.remove(path_to_zip_file)
    result = findSRTFile()
    shutil.move(result[0],destination)
    shutil.rmtree(directory_to_extract_to)
        
def searchHighestRatedSubtitlesLink(html):
    searchresults = re.search(r'<table id="search_results">(.+)</table>',html).group()
    splittedREsults = searchresults.split('tr onclick=')
    currentHighestRated = {1:0,
                           2:0.0,
                           3:None}
    for i in range(1,len(splittedREsults)):
        spanVotes = re.search(r'span title="\d votes">(.+)</span>', splittedREsults[i]).group()
        noOfVotes = int(re.search(r'\d', re.search(r'="\d votes',spanVotes).group()).group())
        avgRating = float(re.search(r'\d+.\d+',spanVotes).group())
        movieID = re.search(r'\d+', (re.search(r'servOC.\d+.', splittedREsults[i]).group())).group()
        if((len(currentHighestRated) == 0) | (avgRating>currentHighestRated[2]) | ((avgRating==currentHighestRated[2]) & (noOfVotes>currentHighestRated[1]))):
            currentHighestRated[1] = noOfVotes
            currentHighestRated[2] = avgRating
            currentHighestRated[3] = movieID            
    return currentHighestRated[3]

def downloadMovieFromTag(url):
    with urllib.request.urlopen(url) as response:
        html = str(response.read())
        movieIDtag = re.search(r'data-product-id="\d+"', html)
        if(movieIDtag == None):
            movieID = searchHighestRatedSubtitlesLink(html)
        else:
            movieID = re.search(r'\d+', str(movieIDtag.group())).group()
        downloadInIDMOnBasisOfMovieID(movieID)
    
downloadMovieFromTag(openSubtitleSearchURL)
    
