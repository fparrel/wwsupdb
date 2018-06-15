
#
# Screen scrap from ckfiumi.net and output to a .json file
#

# To run:
# scrapy runspider ckfiumi_scrap.py -o ckfiumi.json --logfile=ckfiumi.log

# begin of hard codes

bad_lengths = {'6 - 7':7,
'2.5 o 12':12,
'12 (totali andata e ritorno)':12,
'6-7':7,
'9 (+ 8)':17,
'7-8':8,
'3-3.5 km.':3.5,
'3km':3,
'6 Km':6,
'6/7':7,
'4.5/5.5':5.5,
'0.5/0.6':0.6,
'9-12':12,
'2 circa':2,
'7 4':7,
'4-5':5,
'1   1':2,
'500 metri':0.5,
'1.5 oppure 2.5':2.5,
'2-3':3,
'15 (6)':15,
'5.1 km2':5.1,
'8 (4.5 da Masanti)':8,
'5+5':10,
'7-8':8}

bad_slopes = {'lieve':10.0,'tanta':None,'da misurare':None,'estrema ,oltre il 70':70,'bassa':10.0,'50 circa':50.0,'alta':None}

bad_flows = {"A":None,"Minimo 10 mq":[10],"4 minimo  alla partenza":[4],"min 3 mc max 15 mc":[3,15],"da 50 a 200":[50,200],"20 a 50":[20,50],
             "all imbarco 8 m3 circa":[8],"allo sbarco 12 15":[12,15],"4 o 5":[4,5]}

bad_durations = {"30minuti":0.5,"2 la prima volta":2.0,"1, 30":1.5,"2 e mezza":2.5,"3 ore e 30 min":3.5,"dai 30 min, alle 2 ore":2.0,"15 min":0.25,
"45 min":0.75,"20 min":0.3,"una o due":2.0,"1,5 discesa":1.5,"3.5 in prima":3.5,"da 1 a 3 ore":3.0,"da 1 a 2":2.0,"1ora e mezza":1.5,
"4 ore e 30":4.5,"1 ora e 45":1.75,"4 ore in prima":4.0,"30 min o 1h e 40":1.8,"1 e mezza":1.5,"30 minuti":0.5,"45'":0.75,
"2 ore circa oppure 3":3.0,"0,30 minuti":0.5,"circa  1 ora e 30":1.5,"45 min in totale":0.75,"30 min":0.5,"4.5 Ore":4.5,"1h e 30min.":1.5,"2 o 3":30,
"2h":2.0,"2, 3":3.0}

translate_dict = {"Canoe chiuse":"Canoe (decked)", "Canoa":"Open canoe",
                  "buona":"good", "ottima":"very good", "mediocre":"average", "molto inquinata":"very bad", "inquinata":"bad",
                  "fredda":"cold", "fresca":"cool", "gelida":"very cold", "tiepida":"warm" }

# end of hard codes

import scrapy
import urlparse
import datetime


def strip_translate(italian):
    italian = italian.strip()
    out = translate_dict.get(italian)
    if out==None:
        return italian
    else:
        return out

def get_contents(tag):
    i = tag.find('>')+1
    j = tag.rfind('<')
    return tag[i:j].strip()

class BlogSpider(scrapy.Spider):
    name = 'ckfiumispider'
    start_urls = ['https://ckfiumi.net/fiume.phtml/']

    def parse(self, response):
        print 'parse %s'%response
        cptr=0
        for i in response.css('.listaAlfabetica'):
            url = i.css('a::attr(href)').extract()[0]
            full_url = urlparse.urljoin(response.url, url)
            infos = scrapy.Request(full_url, callback=self.parse_letter)
            cptr+=1
            #if cptr==2:
            #    break
            yield infos
    def parse_letter(self, response):
        print 'parse_letter %s'%response
        for i in response.css('.usrListAlfabetica span a'):
            url = i.css('a::attr(href)').extract()[0]
            full_url = urlparse.urljoin(response.url, url)
            yield scrapy.Request(full_url, callback=self.parse_river)
    def parse_river(self, response):
        print 'parse_river %s'%response
        river_name = response.css('.riepilogo h1').xpath('text()').extract()[0]
        assert(river_name.startswith('fiume '))
        river_name=river_name[6:]
        print 'name',river_name
        i = 0
        for url in response.css('a::attr(href)').re(r'/consulta.phtml/[0-9]*/[0-9]*'):
            i+=1
            full_url = urlparse.urljoin(response.url, url)
            yield scrapy.Request(full_url, callback=self.parse_route, meta={'river_name':river_name,'order':i})
    def parse_route(self, response):
        print 'parse_route %s'%response
        route = {'src_url':response.url}
        river_route = response.css('.label_B').xpath('text()').extract_first()
        prefix = 'fiume  %s:'%response.meta['river_name']
        assert(river_route.startswith(prefix))
        route.update(response.meta)
        route['name'] = river_route[len(prefix):]
        region = response.css('.rapp-contatiner > div').xpath('text()').extract_first().strip()
        assert(region.startswith('regione '))
        region = region[8:]
        region_splited = region.split()
        if len(region_splited)==2:
            route['region'] = region_splited[0]
            route['province'] = region_splited[1][1:-1]
        else:
            route['region'] = region_splited[0]            
        route['desc'] = response.css('.box_head').xpath('text()').extract_first()
        for row in response.css('.rscTblContainer'):
            k = row.css('.rscTblListItemSx').xpath('text()').extract_first().strip()
            if k=='aggiornato al':
                route['open_date'] = datetime.datetime.strptime(row.css('.rscTblListItemDx').xpath('text()').extract_first().strip(), "%Y-%m-%d")
            elif k=='grado':
                route['wwgrade'] = []
                if row.css('.I'):
                    route['wwgrade'].append('I')
                if row.css('.Ip'):
                    route['wwgrade'].append('I+')
                if row.css('.II'):
                    route['wwgrade'].append('II')
                if row.css('.IIp'):
                    route['wwgrade'].append('II+')
                if row.css('.IIIp'):
                    route['wwgrade'].append('III+')
                if row.css('.IV'):
                    route['wwgrade'].append('IV')
                if row.css('.IVp'):
                    route['wwgrade'].append('IV+')
                if row.css('.V'):
                    route['wwgrade'].append('V')
                if row.css('.Vp'):
                    route['wwgrade'].append('V+')
                if row.css('.VI'):
                    route['wwgrade'].append('VI')
                if row.css('.VIp'):
                    route['wwgrade'].append('VI+')
                if row.css('.VII'):
                    route['wwgrade'].append('VII')
            elif k=='distanza':
                length = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                assert(length.endswith(' Km'))
                length = length[:-3].replace(',','.')
                if length.endswith(' km'):
                    length = length[:-3]
                if length.startswith('circa '):
                    length = length[6:]
                if length in bad_lengths:
                    route['length'] = bad_lengths[length]
                else:
                    route['length'] = float(length)
            elif k=='tempo previsto':
                duration = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                if len(duration)>0:
                    assert(duration.endswith(' Ore') or duration.endswith(' Ora'))
                    duration = duration[:-4]
                    if duration in bad_durations:
                        route['duration'] = bad_durations[duration]
                    else:
                        if duration.endswith(' circa'):
                            duration = duration[:-6]
                        if duration.endswith(' ore') or duration.endswith(' ora'):
                            duration = duration[:-4]
                        duration = duration.replace(",",".")
                        route['duration'] = float(duration)
            elif k=='pendenza':
                slope = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                if len(slope)>0:
                    assert(slope.endswith(' m/Km'))
                    slope = slope[:-5]
                    if slope.startswith('media '):
                        slope = slope[6:]
                    if slope in bad_slopes:
                        new_slope = bad_slopes[slope]
                        if new_slope!=None:
                            route['slope'] = new_slope
                    else:
                        route['slope'] = float(slope.replace(',','.'))
            elif k=='stelle WildWater':
                imgsrc = row.css('img::attr(src)').extract_first()
                assert(imgsrc.startswith('/img/'))
                route['wildness'] = int(imgsrc.split('_')[0][5:])
            elif k=='portata':
                flow = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                if flow.endswith(' mc/sec'):
                    flow = flow[:-7]
                if flow in bad_flows:
                    new_flow = bad_flows[flow]
                    if new_flow!=None:
                        route['flow'] = new_flow
                else:
                    route['flow'] = map(lambda f: int(float(f.replace(",","."))),flow.split())
            elif k=='stelle paesaggio':
                imgsrc = row.css('img::attr(src)').extract_first()
                assert(imgsrc.startswith('/img/'))
                route['landscape'] = int(imgsrc.split('_')[0][5:])
            elif k=='temperatura acqua':
                route['water_temperature'] = strip_translate(row.css('.rscTblListItemDx').xpath('text()').extract_first())
            elif k=="qualita' acqua":
                route['water_quality'] = strip_translate(row.css('.rscTblListItemDx').xpath('text()').extract_first())
            elif k=='periodo migliore':
                best_season = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                if best_season!="":
                    route['best_season'] = best_season
            elif k=='livello':
                level = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip()
                if level!="":
                    route['level'] = level
            elif k=='fiumi vicini':
                route['nearest_rivers'] = row.css('.rscTblListItemDx').xpath('text()').extract_first().strip().split(',')
            elif k=='imbarcazioni':
                rafts_sel = row.css('.rscTblListItemDx').xpath('text()')
                if rafts_sel:
                    route['rafts_kind'] = filter(lambda s:len(s)>0,map(strip_translate,rafts_sel.extract_first().split('|')))
        title = None
        for row in response.css('.tbl_print div'):
            title_sel = row.css('.label_titolo')
            if title_sel:
                title = title_sel.xpath('text()').extract_first()
            else:
                if title=='imbarco':
                    route['start'] = row.xpath('text()').extract_first().strip()
                elif title=='sbarco':
                    route['end'] = row.xpath('text()').extract_first().strip()
                elif title=='assistenza da riva':
                    route['ground_security'] = row.xpath('text()').extract_first().strip()
                elif title=='attenzione':
                    route['dangers'] = row.xpath('text()').extract_first().strip()
                elif title=='siti web per approfondire':
                    route['links'] = row.extract()
                elif title=='idrometro':
                    route['hydro'] = row.extract()
                elif title=='locals di riferimento':
                    route['local_contacts'] = row.extract()
        yield route

if __name__=='__main__':
    import sys
    print 'Run me with the following command: scrapy runspider %s -o ckfiumi.json --logfile=ckfiumi.log' % sys.argv[0]
