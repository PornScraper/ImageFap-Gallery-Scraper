import urllib2
import os
import time
from lib import pyperclip

def zeroPad(num, maxnum):
    if num < 0 or maxnum < 0:
        print("error")
        exit(-3)
    prefix = ''
    p10 = 10
    digits = len( str( maxnum ) )
    for i in range(0, digits):
        if num < p10:
            prefix = prefix + '0'
        p10 = p10 * 10        
    return result

def FetchPageText( pageurl ):
    """Fetch a page and return its html as a string"""
    hdr= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'}             
    req = urllib2.Request(pageurl, "", hdr)
    response = urllib2.urlopen(req)
    result = response.read()
    return result

def FetchImageURL(pageurl):
    """Takes a URL to a page that displays a single image like:
    http://www.imagefap.com/photo/$NUMBER/?pgid=&gid=$THE_GID&page=0&idx=$NUM
    and it returns the url of the full size image like:
    http://x.imagefapusercontent.com/u/$SOMENAME/$THE_GID/$NUMBER/Filename.jpg
    """
    imgurl = ''
    html = FetchPageText( pageurl ):
    ############## DEBUG
    with open("imgurl.html", "w") as text_file:
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

def FullGalleryScrape( ctx ):
    html = FetchPageText( ctx{'gallery_index_url'} ):
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

def FindFullGalleryURL( a_url ):
    """Takes some URL from somewhere in the gallery,
    determines the gid=XXXXXXXX and returns the URL
    of the page displaying the thumbnails of all images
    in the gallery together on a single page. The result
    should be of the form:
    http://www.imagefap.com/pictures/$THE_GID/$GALLERY_NAME?gid=$THE_GID&view=2
    or
    http://www.imagefap.com/gallery.php?gid=$THE_GID&view=2
    """
    result = {'gallery_name' : '',
              'gallery_id' : 0,
              'gallery_index_url' : '',
              'gallery_uploader' : '',
              'gallery_date' : '',
              'image_count' : 0,
              'image_preview_urls': [],
              'image_urls': []}
    gid_str = ''
    gid_num = 0
    #name = ''
    gid_idx = a_url.find('gid=')
    if gid_idx == -1:
        # it wasn't found. This is usually because we
        # are on the front page of the Gallery
        tmp_idx = a_url.find('imagefap.com/pictures')
        if tmp_idx == -1:
            print("could not parse\n")
            exit(-3)
        else:
            gid_num = a_url[tmp_idx:]
            gid_num = gid_num.split('/')[2]
            gid_str = 'gid=' + gid_num
            #name = a_url[tmp_idx:]
            #name = name.split('/')[3]
    else:
        # It was found we are on a page in the gallery.... somewhere
        gid_str = a_url[gid_idx:]
        gid_str = gid_str.split('&')[0]
        gid_num = gid_str.split('=')[1]
        #some_html = FetchPageText( a_url );       
        

    #result{'gallery_name'} = name
    result{'gallery_id'} = gid_num
    #     http://www.imagefap.com/gallery.php?gid=$THE_GID&view=2
    result{'gallery_index_url'} = 'http://www.imagefap.com/gallery.php?gid=' + gid_num + '&view=2'

    return result
    
def main():
    urltest = pyperclip.paste()
    print "URL in clipboard: "+ urltest
    use = raw_input("\nWould you like to use the above url? 1=yes 2=input other: ")
    if use == '1' or use == 'y':
        url = urltest
    else:
        url = raw_input("\nEnter the url: ")

    ctx = FindFullGalleryURL( url );
    print('fetching full gallery at [' + ctx{'gallery_index_url'} + ']\n')    
    FullGalleryScrape(clean_url)

main()
