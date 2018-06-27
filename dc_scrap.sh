rm dc.log
rm dc.json
scrapy runspider dc_scrap.py -o dc.json --logfile=dc.log
grep log_count dc.log
