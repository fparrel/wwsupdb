rm evo.json
rm evo.log
scrapy runspider evo_scrap.py -o evo.json --logfile=evo.log
grep log_count evo.log
