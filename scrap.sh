rm eauxvives_org.json
rm eauxvives_org.log
scrapy runspider eauxvives_org-scrap.py -o eauxvives_org.json --logfile=eauxvives_org.log
#python format_eauxvives_org_json.py

