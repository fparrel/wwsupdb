
#
# Screen scrap from eauxvives.org and output to a .json file
#

# To run:
# scrapy runspider evo_scrap.py -o eauxvives_org.json --logfile=eauxvives_org.log


import scrapy
import urlparse


def get_contents(tag):
    i = tag.find('>')+1
    j = tag.rfind('<')
    return tag[i:j].strip()

class BlogSpider(scrapy.Spider):
    name = 'eauxvivesorgspider'
    start_urls = ['http://www.eauxvives.org/en/rivieres/liste']

    def parse(self, response):
        print 'parse %s'%response
        cptr=0
        for i in response.css('.nom_site'):
            name = i.xpath('a/text()').extract()[0] #.encode('utf8')
            href = i.css('a::attr(href)').extract()[0]
            print name.encode('utf8'),href
            full_url = urlparse.urljoin(response.url, href)
            infos = scrapy.Request(full_url, callback=self.parse_river, meta={'name':name})
            cptr+=1
            #if cptr==10:
            #    break
            yield infos

    def parse_river(self, response):
        print 'parse_river %s'%response
        doc = {'name':response.meta['name'],'src_url':response.url}
        for toextract in ('situation_geographique','presentation','alimentation','periode_favorable','echelle','debit','source_niveaux','niveau_temps_reel','qualite_eau','temperature_eau','risques_particuliers','secours','prestataires_eau_vive','clubs_locaux','bonnes_adresses','bibliographie','web_utiles','reglementation_accords','commentaires'):
            values = response.xpath('//div[contains(@id,"%s-riviere_")]/text()'%toextract).extract()
            if len(values)==1:
                value = values[0].strip() #.decode(response.encoding).encode('utf-8')
                if len(value)>0:
                    doc[toextract] = value
            elif len(values)>1:
                value = ''.join(values).strip()
                if len(value)>0:
                    doc[toextract] = value
            else:
                print '%s: cannot extract %s-riviere: len=%s'%(response,toextract,len(values))
            doc['alternatives_navigation'] = [alt for alt in response.css('#alternatives_de_navigation > li').xpath('text()').extract()]
        doc['parcours'] = {}
        parcours=[]
        for i in range(0,20):
            r = response.css('#p%d'%i)
            if len(r)==1:
                doc['parcours']['P%d'%i] = {}
                parcours.append('P%d'%i)
            elif len(r)==0:
                pass
            else:
                raise Exception('More than 1 parcours with same name')
        for toextract in ('nom_site','cotation','embarquement','debarquement','presentation','physionomie','pente_moyenne','logistique','paysage','isolement','playboating','duree','guide_kilometrique','date_derniere_descente'):
            values = response.xpath('//div[contains(@id,"%s-parcours_")]'%(toextract)).extract()
            if len(values)!=len(parcours):
                raise Exception('%s %d %d',(response,len(values),len(parcours)))
            i=0
            for value in values:
                doc['parcours'][parcours[i]][toextract]=get_contents(value)
                doc['parcours'][parcours[i]]['name']=parcours[i]
                i+=1
        #TODO: commentaires
        for parcour in doc['parcours']:
            doc['parcours'][parcour].update({'name':parcour})
        doc['parcours'] = doc['parcours'].values()
        yield doc

if __name__=='__main__':
    print 'Run me with the following command: scrapy runspider eauxvives_org-scrap.py -o eauxvives_org.json --logfile=eauxvives_org.log'
