NAME = "Queue"

BASE_URL = "https://www.plex.tv/pms/playlists/queue"

####################################################################################################
def Start():
    
    HTTP.CacheTime = 0 # in sec - was (=3600): CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'

####################################################################################################
@handler('/video/queue', NAME)
def MainMenu():

    oc = ObjectContainer(title1=NAME)

    if not Client.Platform in ('iOS', ) and not (Client.Platform == 'Safari' and Platform.OS == 'MacOSX'):
        oc.header = 'Not supported'
        oc.message = 'This channel is not supported on %s' % (Client.Platform if Client.Platform is not None else 'this client')
        return oc

    if not 'X-Plex-Token' in Request.Headers:
        oc.header = 'No X-Plex-Token'
        oc.message = 'Sign in to MyPlex first'
        return oc
    
    xml = XML.ElementFromURL(BASE_URL, headers={'X-Plex-Token': Request.Headers['X-Plex-Token']}, sleep=0.5)
    
    for section in xml.findall('Directory'):
        title = section.get('title','none')
        key = section.get('key','none')
        
        Log.Debug(title)
        Log.Debug(key)
        
        oc.add(DirectoryObject(
            key = Callback(Section, title=title, key=key),
            title = title
        ))
    
    return oc

####################################################################################################
@route('/video/queue/section')
def Section(title, key):
    
    oc = ObjectContainer(title1= NAME, title2=title)
    
    if not 'X-Plex-Token' in Request.Headers:
        oc.header = 'No X-Plex-Token'
        oc.message = 'Sign in to MyPlex first'
        return oc
    
    token = Request.Headers['X-Plex-Token']
    xml = XML.ElementFromURL(BASE_URL +'/'+ key, headers={'X-Plex-Token': Request.Headers['X-Plex-Token']}, sleep=0.5)
    
    for video in xml.findall('Video'):
        title = video.get('title','none')
        summary = video.get('summary','none')
        thumb = video.get('thumb','none')
        url = video.get('url','none')
        
        media = video.find('Media')
        
        part = media.find('Part')
        part_key = part.get('key','')
        
        Log.Debug(title)
        #Log.Debug(summary)
        #Log.Debug(thumb)
        Log.Debug(url)
        
        #if not url.startswith('http://'):
        #    url = BASE_URL + url
        
        oc.add(VideoClipObject(
            url = url,
            title = title,
            summary = summary,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb),
            items = [
                MediaObject(
                    parts = [
                        PartObject(
                            key = part_key
                        )
                    ]
                )
            ]
        ))
    
    return oc
