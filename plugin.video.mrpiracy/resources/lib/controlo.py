#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs,sys,urllib,urllib2,unicodedata,re,urlparse,json
from datetime import datetime

from t0mm0.common.addon import Addon

addonInfo = xbmcaddon.Addon().getAddonInfo
addon = xbmcaddon.Addon(addonInfo("id"))
addonFolder = addon.getAddonInfo('path')
definicoes = xbmcaddon.Addon().getSetting
artFolder = os.path.join(addonFolder,'resources','img')
fanart = os.path.join(addonFolder,'fanart.jpg')
skin = 'v1'
alerta = xbmcgui.Dialog().ok
select = xbmcgui.Dialog().select
mensagemprogresso = xbmcgui.DialogProgress()
teclado = xbmc.Keyboard
pastaDados = Addon(addonInfo("id")).get_profile().decode("utf-8")
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7', 'Content-Type': 'application/json'}
dataHoras = datetime.now()

def addDir(name,url,modo,iconimage,pagina=False,tipo=False,infoLabels=False,poster=False,visto=False):
    menu = []
    if infoLabels: infoLabelsAux = infoLabels
    else: infoLabelsAux = {'Title': name}

    if poster: posterAux = poster
    else: posterAux = iconimage

    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&modo="+modo
    ok=True
    fan = fanart
    overlay = 6
    playcount = 0
    if visto == True:
        menu.append(('Marcar como não visto', 'XBMC.RunPlugin(%s?modo=marcar-visto&url=%s)' % (sys.argv[0], urllib.quote_plus(url))))
        overlay = 7
        playcount = 1
    elif visto == False:
        menu.append(('Marcar como visto', 'XBMC.RunPlugin(%s?modo=marcar-visto&url=%s)' % (sys.argv[0], urllib.quote_plus(url))))

    if tipo == 'filme':
        fan = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    elif tipo == 'serie':
        fan = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif tipo == 'episodio':
        fan = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    else:
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')

    infoLabelsAux["overlay"] = overlay
    infoLabelsAux["playcount"] = playcount
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fan)
    liz.setInfo( type="Video", infoLabels=infoLabelsAux )
    liz.addContextMenuItems(menu, replaceItems=True)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addVideo(name,url,modo,iconimage,visto,tipo,temporada,episodio,infoLabels,poster, trailer=False,serieNome=False):

    menu = []

    if tipo == 'filme':
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
        #visto = checkVisto(url)
       
        if addon.getSetting('trailer-filmes') == 'true':
            try:
                idYoutube = urlparse.urlparse(trailer).path.split("=")[-1]
                linkTrailer = 'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+idYoutube
            except:
                linkTrailer = ''
        else:
            linkTrailer = ''
    elif tipo == 'serie':
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        visto = checkVisto(url, temporada, episodio)
        idIMDb = re.compile('imdb=(.+?)&').findall(url)[0]
        linkTrailer = ""
    elif tipo == 'episodio':
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        #visto = checkVisto(url, temporada, episodio)
        
        linkTrailer = ""

    overlay = 6
    playcount = 0

    

    if visto == True:
        menu.append(('Marcar como não visto', 'XBMC.RunPlugin(%s?modo=marcar-visto&url=%s)' % (sys.argv[0], urllib.quote_plus(url))))
        overlay = 7
        playcount = 1
    elif visto == False:
        menu.append(('Marcar como visto', 'XBMC.RunPlugin(%s?modo=marcar-visto&url=%s)' % (sys.argv[0], urllib.quote_plus(url))))


    if not serieNome:
        serieNome = ''

    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&modo="+modo
    ok=True
    #&name="+urllib.quote_plus(name)+"
    infoLabels["overlay"] = overlay
    infoLabels["playcount"] = playcount

    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setProperty('fanart_image', poster)
    liz.setInfo( type="Video", infoLabels=infoLabels )

    if linkTrailer != '':
        menu.append(('Ver Trailer', 'XBMC.PlayMedia(%s)' % (linkTrailer)))

    #menu.append(('Marcar como visto (Site)', 'XBMC.RunPlugin(%s?mode=16&url=%s)' % (sys.argv[0], urllib.quote_plus(url))))

    menu.append(('Download', 'XBMC.RunPlugin(%s?modo=download&url=%s)'%(sys.argv[0], urllib.quote_plus(url))))
    liz.addContextMenuItems(menu, replaceItems=True)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok

def to_unicode(text):
	nfkd_form = unicodedata.normalize('NFKD', text)
	return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def abrir_url(url, post=None, header=None, code=False, erro=False):

    if header == None:
        header = headers

    if post:
        req = urllib2.Request(url, data=post, headers=header)
    else:
        req = urllib2.Request(url, headers=header)

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as response:
        if erro == True:
            return str(response.code), "asd"

    link=response.read()

    if 'myapimp.tk' in url:
        coiso = json.loads(link)
        if 'error' in coiso:
            if coiso['error'] == 'access_denied':
                headers['Authorization'] = 'Bearer %s' % addon.getSetting('tokenMrpiracy')
                dados = {'refresh_token': addon.getSetting('refreshMrpiracy'),'grant_type': 'refresh_token', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
                resultado = abrir_url('http://myapimp.tk/api/token/refresh',post=json.dumps(dados), headers=controlo.headers)
                resultado = json.loads(resultado)
                addon.setSetting('tokenMrpiracy', resultado['access_token'])
                addon.setSetting('refreshMrpiracy', resultado['refresh_token'])
                if post:
                    return abrir_url(url, post=post, headers=header)
                else:
                    return abrir_url(url, headers=header)
                
    if 'judicial' in link:
        return 'DNS'
    if code:
        return str(response.code), link

    response.close()
    return link