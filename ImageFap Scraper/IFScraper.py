import urllib2
import os
import time
from lib import pyperclip

def zeroPad(num):
    result = ''
    if num < 0:
        print("error")
        exit(-3)
    elif num < 10:
        result = '00' + str(num)
    elif num < 100:
        result = '0' + str(num)
    else:
        result = str(num)
    return result

def FetchImageURL(pageurl):
    imgurl = ''
    hdr= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}             
    req = urllib2.Request(pageurl, "", hdr)
    response = urllib2.urlopen(req)
    html = response.read()
    ##############
    with open("response.html", "w") as text_file:
            text_file.write(html)
            text_file.close()
    ##############
    needle = '\"contentUrl\": \"'
    idx = html.find(needle) 
    if idx == -1:
        print('Sorry, cannot parse index. Something must have changed. Bailing out.\n');
        exit(-2);
    else:
        imgurl = html[idx+len(needle):]
        imgurl = imgurl.split('</script>')[0]
        imgurl = imgurl.split('\"')[0];
        print('finalimgurl = [' + imgurl + ']')
    return imgurl

def PageScrape(pageurl):
    hdr= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}             
    req = urllib2.Request(pageurl, "", hdr)
    response = urllib2.urlopen(req)
    html = response.read()
    ##############
    with open("response.html", "w") as text_file:
            text_file.write(html)
            text_file.close()
    ##############
    search = '<b><font size=\"4\" color='
    idx = html.find(search) 
    if idx == -1:
        print('Sorry, cannot parse index. Something must have changed. Bailing out.\n');
        exit(-2);
    else:
        foldername = html[idx:]
        foldername = foldername.split('</font></b>')[0]
        foldername = foldername.split('>')[2]        
        while foldername[-1]=='.' or foldername[-1]==' ':
            foldername = foldername[:-1]
    search = 'href=\"/photo'
    imgcount = 0
    fetch_ary = []
    for i in range(len(html)-len(search)):
        if search == html[i:i+len(search)]:
            imgcount += 1
            new_url = html[i+6:]
            new_url = new_url.split('<img style=')[0]
            new_url = new_url.split('\"')[0]
            new_url = 'http://www.imagefap.com' + new_url
            print('url=[' + new_url +']') 
            fetch_ary.append(new_url);
    print "\n\nThere are "+str(imgcount)+" pics in the gallery: \""+foldername+"\"."
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
        imgnum = 1
        for cur in fetch_ary:
            time.sleep(6)
            imgurl = FetchImageURL(cur)
            orig_fname = imgurl[imgurl.rindex('/')+1:]
            imgname = foldername+'/'+zeroPad(imgnum)+'__'+orig_fname
            print('Preparing to write to [' +imgname+']')
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
url_front = url.split('?')[0]
url_back = url.split('?')[1]
gid_str = url_back[url_back.find('gid='):]
gid_str = gid_str.split('&')[0]
final_url = url_front + '?' + gid_str + '&view=2'
print('fetching full gallery at [' + final_url + ']\n')
PageScrape(url)

