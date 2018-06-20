
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

        #yield scrapy.Request('http://www.eauxvives.org/en/rivieres/voir/daronne', callback=self.parse_river, meta={})
        #return

        for tr in response.css('.liste_sites tr'):
            name = tr.css('.nom_site').xpath('a/text()').extract_first()
            href = tr.css('.nom_site a::attr(href)').extract_first()
            place = tr.css('td:nth-child(even)').xpath('text()').extract_first()
            situation = map(lambda x:x.strip(),place.split('>'))
            full_url = urlparse.urljoin(response.url, href)
            cptr+=1
            print name,href,situation
            yield scrapy.Request(full_url, callback=self.parse_river, meta={'name':name,'situation':situation})

    def parse_river(self, response):
        print 'parse_river %s'%response
        # Ignore some pages
        if response.url=='http://www.eauxvives.org/en/rivieres/voir/cartes-des-pyrenees':
            return
        # Add info already got
        doc = {'src_url':response.url}
        doc.update(response.meta)
        # Extract general infos
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
        parcours=[]
        for i in range(0,20):
            r = response.css('#p%d'%i)
            if r:
                #print 'parcours',i
                parcour = {'name': 'P%d'%i}
                for toextract in ('nom_site','cotation','embarquement','debarquement','presentation','physionomie','pente_moyenne','logistique','paysage','isolement','playboating','duree','guide_kilometrique','date_derniere_descente'):
                    value = r.css('div[id*="%s-parcours_"]'%(toextract)).extract_first()
                    parcour[toextract] = get_contents(value)
                parcours.append(parcour)
        doc['parcours'] = parcours
        #TODO: commentaires
        yield doc

if __name__=='__main__':
    print 'Run me with the following command: scrapy runspider eauxvives_org-scrap.py -o eauxvives_org.json --logfile=eauxvives_org.log'
