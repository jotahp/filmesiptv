#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, base64
import xbmcgui
import xbmc
import xbmcvfs
import time
import urllib
import urllib2
import re
import sys
import traceback
import json
import Trakt
import Database
from t0mm0.common.net import Net

import controlo

__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}


#enen92 class (RatoTv) adapted for MrPiracy.xyz addon

class Player(xbmc.Player):
    def __init__(self, url, idFilme, pastaData, temporada, episodio, nome, logo):
        xbmc.Player.__init__(self)
        self.url=url
        self.temporada=temporada
        self.episodio=episodio
        self.playing = True
        self.tempo = 0
        self.tempoTotal = 0
        self.idFilme = idFilme
        self.pastaData = xbmc.translatePath(pastaData)
        self.nome = nome
        self.logo = logo
        self.API_SITE = base64.urlsafe_b64decode('aHR0cDovL21ycGlyYWN5Lndpbi9hcGkv')

        if not xbmcvfs.exists(os.path.join(pastaData,'tracker')):
            xbmcvfs.mkdirs(os.path.join(pastaData,'tracker'))


        if self.temporada != 0 and self.episodio != 0:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'_S'+str(self.temporada)+'x'+str(self.episodio)+'.mrpiracy')
            self.content = 'episode'
        else:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'.mrpiracy')
            self.content = 'movie'



    def onPlayBackStarted(self):
        #print '=======> player Start'
        self.tempoTotal = self.getTotalTime()
        #print '==========> total time'+str(self.tempoTotal)

        if xbmcvfs.exists(self.pastaVideo):
            #print "Ja existe um ficheiro do filme"

            f = open(self.pastaVideo, "r")
            tempo = f.read()
            tempoAux = ''
            minutos,segundos = divmod(float(tempo), 60)
            if minutos > 60:
                horas,minutos = divmod(minutos, 60)
                tempoAux = "%02d:%02d:%02d" % (horas, minutos, segundos)
            else:
                tempoAux = "%02d:%02d" % (minutos, segundos)

            dialog = xbmcgui.Dialog().yesno('MrPiracy', u'Já começaste a ver antes.', 'Continuas a partir de %s?' % (tempoAux), '', 'Não', 'Sim')
            if dialog:
                self.seekTime(float(tempo))



    def onPlayBackStopped(self):
        #print 'player Stop'
        self.playing = False
        tempo = int(self.tempo)
        #print 'self.time/self.totalTime='+str(self.tempo/self.tempoTotal)
        if (self.tempo/self.tempoTotal > 0.90):

            #self.adicionarVistoBiblioteca()
            #self.adicionarVistoSite()

            try:
                xbmcvfs.delete(self.pastaVideo)
            except:
                print "Não apagou"
                pass

    def adicionarVistoSite(self):
        controlo.headers['Authorization'] = 'Bearer %s' % controlo.addon.getSetting('tokenMrpiracy')
        links = self.url.split('/')
        if 'filme' in url:
            id_video = links[-1]
            post = {'id_filme': id_video}
            url = self.API_SITE+'filmes/marcar-visto'
            tipo = 0
        elif 'serie' in url:
            id_video = links[5]
            temporada = links[7]
            episodio = links[-1]
            post = {'id_serie': id_video, 'temporada': temporada, 'episodio':episodio}
            url = self.API_SITE+'series/marcar-visto'
            tipo = 1
        elif 'anime' in url:
            id_video = links[5]
            temporada = links[7]
            episodio = links[-1]
            post = {'id_anime': id_video, 'temporada': temporada, 'episodio':episodio}
            url = self.API_SITE+'animes/marcar-visto'
            tipo = 2

        resultado = controlo.abrir_url(url, post=json.dumps(post), header=controlo.headers)
        if resultado == 'DNS':
            controlo.alerta('MrPiracy', 'Tem de alterar os DNS para poder usufruir do addon')
            return False
        
        resultado = json.loads(resultado)
        
        if resultado['codigo'] == 200:
            xbmc.executebuiltin("XBMC.Notification(MrPiracy,"+"Marcado como visto"+","+"6000"+","+ os.path.join(controlo.addonFolder,'icon.png')+")")
            xbmc.executebuiltin("Container.Refresh")
        if resultado['codigo'] == 201:
            xbmc.executebuiltin("XBMC.Notification(MrPiracy,"+"Marcado como não visto"+","+"6000"+","+ os.path.join(controlo.addonFolder,'icon.png')+")")
            xbmc.executebuiltin("Container.Refresh")
        elif resultado['codigo'] == 204:
            controlo.alerta('MrPiracy', 'Ocorreu um erro ao marcar como visto')

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def adicionarVistoBiblioteca(self):
        try:
            if self.content == 'episode':
                Database.markwatchedEpisodioDB(self.idFilme, self.temporada, self.episodio)
                if Trakt.loggedIn():
                    Trakt.markwatchedEpisodioTrakt(self.idFilme, self.temporada, self.episodio)
            elif self.content == 'movie':
                Database.markwatchedFilmeDB(self.idFilme)
                if Trakt.loggedIn():
                    Trakt.markwatchedFilmeTrakt(self.idFilme)
        except:
            pass

    def adicionarVistoBiblioteca2(self):
        pastaVisto=os.path.join(self.pastaData,'vistos')

        try:
            os.makedirs(pastaVisto)
        except:
            pass

        if int(self.temporada) != 0 and int(self.episodio) != 0:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'_S'+str(self.temporada)+'x'+str(self.episodio)+'.mrpiracy')
        else:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'.mrpiracy')


        if not os.path.exists(ficheiro):
            f = open(ficheiro, 'w')
            f.write('')
            f.close()
            xbmc.executebuiltin("XBMC.Notification(MrPiracy.win,"+"Marcado como visto"+","+"6000"+","+ self.logo+")")
            xbmc.executebuiltin("Container.Refresh")
        else:
            print "Já foi colocado antes"

           


    def trackerTempo(self):
        try:
            self.tempo = self.getTime()
            f = open(self.pastaVideo, mode="w")
            f.write(str(self.tempo))
            f.close()
        except:
            traceback.print_exc()
            print "Não gravou o conteudo em %s" % self.pastaVideo
