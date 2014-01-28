import urllib2
import os
from lib import pyperclip

def PageScrape(pageurl):
    hdr= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}             
    req = urllib2.Request(pageurl, "", hdr)
    response = urllib2.urlopen(req)
    html = response.read()
    search = 'Gallery:'
    for i in range(len(html)-len(search)):
        if search == html[i:i+len(search)]:
            foldername = html[i+len(search)-1:]
            foldername = foldername.split('<')[3].split('>')[1]
    while foldername[-1]=='.' or foldername[-1]==' ':
        foldername = foldername[:-1]
    search = 'original=\"'
    imgnum = 1
    imgcount = 0
    for i in range(len(html)-len(search)):
        if search == html[i:i+len(search)]:
            imgcount += 1
    print "\n\nThere are "+str(imgcount)+" pics in the gallery: "+foldername+"."
    contnum = 2
    contnum = raw_input("Would you like to download them all? 1=yes 2=no: ")
    foldername = 'Downloads/'+foldername
    if contnum == '1':
        print '\n'
        try:
            os.makedirs(foldername)
        except:
            print "Error, make sure there is no directory with this script"
            return 0
        for i in range(len(html)-len(search)):
            if search == html[i:i+len(search)]:
                imgurl = html[i+len(search):]
                imgurl = imgurl.split('"')[0]
                if imgurl[-4] == '.':
                    imgname = foldername+'/'+str(imgnum)+imgurl[-4:]
                else:
                    imgname = foldername+'/'+str(imgnum)+imgurl[-5:]
                f = open(imgname, 'wb')
                f.write(urllib2.urlopen(imgurl).read())
                f.close()
                print '\t'+str(imgnum)+'/'+str(imgcount)+ ' completed\n'
                imgnum += 1
    return 0
    

urltest = pyperclip.paste()
print "URL in clipboard: "+ urltest
use = raw_input("\nWould you like to use the above url? 1=yes 2=input other: ")
if use == '1':
    url = urltest
else:
    url = raw_input("\nEnter the url: ")
PageScrape(url)

