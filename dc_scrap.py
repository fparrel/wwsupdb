# -*- coding: utf-8 -*-

import scrapy
import urlparse
import urllib2
from xml.dom.minidom import parseString
import re

cot_pat_av = re.compile(r'a(\d+)v(\d+)([IV]+)')
cot_pat_va = re.compile(r'v(\d+)a(\d+)([IV]+)')

romain2arab = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7}

class BlogSpider(scrapy.Spider):
    name = 'canyonspider'
    start_urls = ['http://www.descente-canyon.com/canyoning/lieux/11/21/France.html',
                  'http://www.descente-canyon.com/canyoning/lieux/11/22/Italie.html']

    def parse(self, response):
        print 'parse %s'%response.url
        for href in response.css('#table-departement > tbody > tr > td a::attr(href)'):
            full_url = urlparse.urljoin(response.url, href.extract())
            if full_url.startswith('http://www.descente-canyon.com/boutique/') or full_url.startswith('http://www.descente-canyon.com/canyoning/topoguide/'):
                continue
            yield scrapy.Request(full_url, callback=self.parse_province)

    def parse_province(self, response):
        print 'parse_province %s'%response.url
        name = response.css('#content > h4').extract_first().split(' &gt; ')[-1]
        assert(name.endswith('</h4>'))
        name = name[:-5]
        for href in response.css('#table-1 > tbody > tr > td a::attr(href)'):
            full_url = urlparse.urljoin(response.url, href.extract())
            if full_url.startswith('http://www.descente-canyon.com/boutique/') or full_url.startswith('http://www.descente-canyon.com/canyoning/topoguide/') or full_url.startswith('http://www.descente-canyon.com/canyoning/canyon-new-geo/'):
                continue
            cid = href.extract().split('/')[3]
            yield scrapy.Request(full_url, callback=self.parse_canyon, meta={'cid':cid,'province_name':name})

    def parse_canyon(self, response):
        print 'parse_canyon %s'%response.url

        location = {}
        title = response.css('h1::text').extract_first()
        try:
            interet = float(filter(lambda x:not(x.startswith("Attention")),response.css('.fichetechnique strong::text').extract())[0])
        except:
            interet = -1
        valeurs = []
        for valeur in response.css('table.fichetechnique td.valeur'):
            for a in valeur.css('a::text'):
                valeurs.append(a.extract())
            for t in valeur.css('td::text'):
                valeurs.append(t.extract())
        if len(valeurs)!=10:
            print 'error valeurs ',response.url
        altdep,cotation,aller,deniv,longcorde,descente,longueur,retour,cascade,navette=valeurs

        geodoc = parseString(urllib2.urlopen('http://www.descente-canyon.com/canyoning/localized-point-search?t=xml2&idc='+response.meta['cid'][1:]).read())
        for marker in geodoc.getElementsByTagName('marker'):
            lat = marker.getAttributeNode('lat').nodeValue
            lon = marker.getAttributeNode('lng').nodeValue
            label = marker.getAttributeNode('label').nodeValue
            if label.startswith('parking'):
                location={'lat':float(lat),'lon':float(lon),'nature':'parking'}
                break
            if label.startswith('depart'):
                location={'lat':float(lat),'lon':float(lon),'nature':'depart'}
            if label.startswith('arrivee'):
                location={'lat':float(lat),'lon':float(lon),'nature':'arrivee'}
        doc = {'src_url':response.url,'localisation':location,'title':title,'interet':interet,'aller':aller,'descente':descente,'ret':retour}
        doc.update(response.meta)
        if longueur!='??':
            assert(longueur.endswith('m'))
            doc['lg'] = int(longueur[:-1])
        if longcorde not in ('??','...'):
            assert(longcorde.endswith('m'))
            doc['corde'] = int(longcorde[:-1])
        if cascade not in ('??','...'):
            assert(cascade.endswith('m'))
            doc['cascade'] = int(cascade[:-1])
        if deniv not in ('??','...'):
            assert(deniv.endswith('m'))
            doc['deniv'] = int(deniv[:-1])
        if altdep not in ('??','...'):
            assert(altdep.endswith('m'))
            doc['alt'] = int(altdep[:-1])
        if cotation not in ('??','...'):
            if cotation.startswith('a'):
                a,v,e = cot_pat_av.findall(cotation)[0]
            else:
                v,a,e = cot_pat_va.findall(cotation)[0]
            doc['cot'] = {'a':a,'v':v,'e':romain2arab[e]}
        if navette not in ('??','...') and not navette.endswith('ant'): #TODO: néant utf8
            assert(navette.endswith('km'))
            doc['navette'] = float(navette[:-2])

        commune = response.css('a[title="Voir les canyons de cette commune"]').xpath('text()').extract_first()
        if commune!=None:
            doc['commune'] = commune
        bassin = response.css('a[title="Voir les canyons qui alimentent ce bassin"]').xpath('text()').extract_first()
        if bassin!=None:
            doc['bassin'] = bassin

        return doc
