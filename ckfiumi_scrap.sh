rm ckfiumi.json
rm ckfiumi.log
scrapy runspider ckfiumi_scrap.py -o ckfiumi.json --logfile=ckfiumi.log
grep log_count ckfiumi.log

