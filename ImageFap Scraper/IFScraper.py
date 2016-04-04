#!/usr/bin/env python

import urllib2
import os
import time
import re
from lib import pyperclip

PARANOID_SLEEP = 1

def zeroPad(num, maxnum):
    """Return the correct number or preceeding zeros to make the numbers sort cleanly in a filesystem
    """
    if num < 0 or maxnum < 0 or num > maxnum:
        print("error")
        exit(-3)
    prefix = ''
    max_digits = len( str( maxnum ) )
    num_digits = len( str( num ) )
    zeros = max_digits - num_digits
    for i in range(0, zeros):
        prefix = prefix + '0'
    return str(prefix) + str(num)


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
    html = FetchPageText( pageurl )
    ############## DEBUG
    #with open("imgurl.html", "w") as text_file:
    #        text_file.write(html)
    #        text_file.close()
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
        #print('finalimgurl = [' + imgurl + ']')
    return imgurl

def GetGalleryIndex( ctx ):
    html = FetchPageText( ctx['gallery_index_url'] )
    ###### DEBUG #######
    #with open("response.html", "w") as text_file:
    #        text_file.write(html)
    #        text_file.close()
    ####################
    ctx = ExtractMetadata( ctx, html )
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
    needle = 'href=\"/photo'
    imgcount = 0
    fetch_ary = []
    offset = 0
    idx = html.find(needle, offset)
    while not (idx == -1): 
        imgcount += 1
        new_url = html[idx+6:]
        new_url = new_url.split('<img style=')[0]
        new_url = new_url.split('\"')[0]
        new_url = 'http://www.imagefap.com' + new_url
        new_url = new_url.replace('&amp;', '&')
        #print('url=[' + new_url +']') 
        fetch_ary.append(new_url);
        offset = idx + len(needle)
        idx = html.find(needle, offset)

    ctx['image_count'] = imgcount
    ctx['image_preview_urls'] = fetch_ary
    return ctx


def ExtractMetadata( ctx, html ):
    name = ''
    uploader = ''
    date = ''
    # Name
    needle = 'http://www.imagefap.com/pictures/'
    idx = html.find(needle)
    if idx == -1:
        print("Error: Could not find gallery name.")
        exit(-3)
    else:
        name = html[idx+len(needle):]
        name = name.split('?')[0]
        name = name.split('/')[1]
        name = urllib2.unquote(name)
        bad_winchars = {'*':'', '.':'', '"':'', '/':'', '\\':'', '[':'(', ']':'(', ':':'', ';':'', '|':'-', '=':'-', ',':'', '!':''}
        for o_char,n_char in bad_winchars.iteritems():
            name = name.replace(o_char, n_char)
        #print("name = [" + name + "]\n")

    # Uploader
    needle = '<b><font size="3" color="#CC0000">Uploaded by '
    idx = html.find(needle)
    if idx == -1:
        print("Error: Could not find gallery uploader.")
        exit(-4)
    else:
        uploader = html[idx+len(needle):]
        uploader = uploader.split('</font>')[0]
        #print("uploader = [" + uploader + "]\n")

    # Date
    ctx['download_date'] = time.strftime("%c")
    ctx['gallery_name'] = name
    ctx['gallery_uploader'] = uploader
    return ctx

def EmitMetadata( ctx, dname ):
    """Saves the context metadata about the gallery name/uploader/urls/etc to a log file beginning with three underscores"""
    preamble = '<html><head><title>ImageFap Scrape Data</title></head>\n<body><pre>\n'
    postamble = '\n</pre></body></html>\n'
    fname = dname + '/___ImageFap_Scrape_Info.html'
    print('Writing log to [' +fname+']')
    f = open(fname, 'w')
    f.write(preamble)
    f.write( str(ctx) )
    f.write(postamble)
    f.close()
    return

def FetchAndSaveImages( ctx ):
    """
    Runs through the array ctx['image_preview_urls'] using each preview url to determine the full res image url. Then downloads and saves the full image.
    """
    foldername = 'Downloads/' + ctx['gallery_name']
    try:
        os.makedirs(foldername)
    except:
        print("Error, make sure there is no directory with this script")
        return 0
    imgnum = 0
    imgcount = ctx['image_count']
    for cur in ctx['image_preview_urls']:
        time.sleep( PARANOID_SLEEP )
        imgurl = FetchImageURL(cur)
        ctx['image_urls'].append(imgurl)
        orig_fname = imgurl[imgurl.rindex('/')+1:]
        imgname = foldername+'/'+zeroPad(imgnum,imgcount)+'__'+orig_fname
        print('Saving [' +imgname+']')
        f = open(imgname, 'wb')
        f.write(urllib2.urlopen(imgurl).read())
        f.close()
        print('\t'+str(imgnum+1)+'/'+str(imgcount)+ ' completed')
        imgnum += 1
    EmitMetadata(ctx, foldername)
    return ctx

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
              'download_date' : '',
              'image_count' : 0,
              'image_preview_urls': [],
              'image_urls': []}
    gid_str = ''
    gid_num = 0
    res = re.search('[^p]gid=(\d+)', a_url) 
    if res:
        # print("case 1")
        # It was found we are on a page in the gallery.... somewhere
        gid_num = res.groups()[0] 
        gid_str = 'gid=' + str(gid_num)
    else:
        # print("case 2")
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

    result['gallery_id'] = gid_num
    #     http://www.imagefap.com/gallery.php?gid=$THE_GID&view=2
    result['gallery_index_url'] = 'http://www.imagefap.com/gallery.php?gid=' + str(gid_num) + '&view=2'

    return result
    
def main():
    urltest = pyperclip.paste()
    print("URL in clipboard: " + urltest)
    use = raw_input("\nWould you like to use the above url? 1=yes 2=input other: ")
    if use == '1' or use == 'y':
        url = urltest
    else:
        url = raw_input("\nEnter the url: ")

    ctx = FindFullGalleryURL( url );
    print('Fetching full gallery index at [' + ctx['gallery_index_url'] + ']')    
    ctx = GetGalleryIndex( ctx )

    print("\n\nThere are "+str(ctx['image_count'])+" pics in the gallery: \""+ ctx['gallery_name']+"\".")
    contnum = 2
    contnum = raw_input("Would you like to download them all? 1=yes 2=no: ")
    if contnum == '1' or contnum == 'y':
        print('\n')
        ctx = FetchAndSaveImages( ctx )
    else:
        print("Bailing out.\n")
        exit(0)

main()
