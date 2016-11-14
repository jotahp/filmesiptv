#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib,json,os,sys

import controlo

def add(items, cacheToDisc=True, content=None, mediatype=None, infotype='video'):
    if items == None or len(items) == 0: return

    sysaddon = sys.argv[0]
    syshandle = int(sys.argv[1])
    sysicon = os.path.join(controlo.addonInfo('path'), 'resources', 'img', 'v1')
    sysimage = controlo.addonInfo('icon')
    sysfanart = controlo.addonInfo('fanart')

    for i in items:
        try:
            titulo = i['titulo'] 
            imagem = i['imagem']
            link = i['link']
            modo = i['modo']
            

            url = '%s?modo=%s' % (sysaddon, modo)

            try: url += '&url=%s' % urllib.quote_plus(link)
            except: pass
            try: url += '&imagem=%s' % urllib.quote_plus(i['imagem'])
            except: pass

            cm = []
            menus = i['cm'] if 'cm' in i else []

            for menu in menus:
                try:
                    try: tmenu = control.lang(menu['title']).encode('utf-8')
                    except: tmenu = menu['title']
                    qmenu = urllib.urlencode(menu['query'])
                    cm.append((tmenu, 'RunPlugin(%s?%s)' % (sysaddon, qmenu)))
                except:
                    pass

            meta = dict((k,v) for k, v in i.iteritems() if not k == 'cm' and not v == '0')
            if not mediatype == None: meta['mediatype'] = mediatype

            item = control.item(label=label, iconImage=image, thumbnailImage=image)

            item.setArt({'icon': image, 'thumb': image, 'poster': image, 'tvshow.poster': image, 'season.poster': image, 'banner': banner, 'tvshow.banner': banner, 'season.banner': banner})

            item.setProperty('Fanart_Image', fanart)

            item.addContextMenuItems(cm)
            item.setInfo(type=infotype, infoLabels = meta)
            if isFolder == False: item.setProperty('IsPlayable', 'true')
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
        except:
            pass

    try:
        i = items[0]
        if i['next'] == '': raise Exception()

        url = '%s?action=%s&url=%s' % (sysaddon, i['nextaction'], urllib.quote_plus(i['next']))
        icon = i['nexticon'] if 'nexticon' in i else os.path.join(sysicon, 'next.png')
        fanart = i['nextfanart'] if 'nextfanart' in i else sysfanart
        try: label = control.lang(i['nextlabel']).encode('utf-8')
        except: label = 'next'

        item = control.item(label=label, iconImage=icon, thumbnailImage=icon)
        item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'tvshow.poster': icon, 'season.poster': icon, 'banner': icon, 'tvshow.banner': icon, 'season.banner': icon})
        item.setProperty('Fanart_Image', fanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
    except:
        pass

    if not content == None: control.content(syshandle, content)
    control.directory(syshandle, cacheToDisc=cacheToDisc)
