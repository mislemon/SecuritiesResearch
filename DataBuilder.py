#!/usr/bin/python
# coding=utf-8


###########################################################
# Global setting
###########################################################

SH_STOCK_LIST_URL = "http://biz.sse.com.cn/sseportal/webapp/datapresent/SSEQueryStockInfoAct?reportName=BizCompStockInfoRpt&CURSOR="
SZ_STOCK_LIST_URL = "http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=8&CATALOGID=1110&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1"
STOCK_TRADE_DAILY_INFO_URL = "http://quotes.money.163.com/service/chddata.html?code={0}&start={1}&end={2}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"
STOCK_LIST_FILE_NAME = "stock.list"

# Log config #
import logging

log = logging.getLogger("Sabo")
log.setLevel(logging.DEBUG)

consolehandler = logging.StreamHandler()
filehandler = logging.FileHandler("Sabo.log")
consolehandler.setLevel(logging.DEBUG)
filehandler.setLevel(logging.WARNING)

formatter = logging.Formatter("[%(name)s - %(levelname)s] %(asctime)s %(message)s")
consolehandler.setFormatter(formatter)
filehandler.setFormatter(formatter)

log.addHandler(consolehandler)
log.addHandler(filehandler)


# Here we go!
###########################################################
# STEP 1. Get stock number list.
###########################################################

import urllib
import sys
import os
from lxml import etree

# Clean old stock.list #
if os.path.exists(STOCK_LIST_FILE_NAME):
    os.remove(STOCK_LIST_FILE_NAME)

stockfile = open(STOCK_LIST_FILE_NAME, "w+")
# Get sh stock number list #
shstockhtml = urllib.urlopen(SH_STOCK_LIST_URL).read()
if type(shstockhtml) is not str or len(shstockhtml) == 0:
    log.error("Fail to get sh stock web data...")
    sys.exit(1)

shhtmlroot = etree.HTML(shstockhtml)
strongs = shhtmlroot.xpath("//strong")
# Easy check
if len(strongs) != 2:
    log.error("sh web has changed, we need to change the code.")
    sys.exit(1)
# 
pages = int(str(strongs[1].text)) 

# Trace every page and get stock number 
for pgno in range(0, pages):
    links = shhtmlroot.xpath("//table[@bgcolor='#337fb2']//a")
    for link in links:
        linkstr = str(link.text)
        log.info("[" + linkstr + "] got.")
        stockfile.write(linkstr + "\n")
    # Prepare next loop
    if pgno == pages:
        break
    nextpageurl = SH_STOCK_LIST_URL + str((1 + pgno) * 50 + 1)
    nextpagehtml = urllib.urlopen(nextpageurl).read()
    if len(nextpagehtml) == 0:
        log.error("Failed to get page data from URL:" + nextpageurl)
        sys.exit(1)
    shhtmlroot = etree.HTML(nextpagehtml)

shhtmlroot = None

# Get sz stock number list #
szstockhtml = urllib.urlopen(SZ_STOCK_LIST_URL).read()
if len(str(szstockhtml)) == 0:
    log.error("Failed to get sz stock web data. URL : " + SZ_STOCK_LIST_URL)
    sys.exit(1)
szstockroot = etree.HTML(szstockhtml)
tds = szstockroot.xpath("//td[@style='mso-number-format:\@']")
for td in tds:
    tdtext = str(td.text)
    log.info("[" + tdtext + "] got.")
    stockfile.write(tdtext + "\n")

stockfile.close()
szstockroot = None
log.info("=====================STOCK CODE LIST GENERATED===============================")

     
###########################################################
# STEP 2. Get stock trade simple info
###########################################################
import time

stockfile = open(STOCK_LIST_FILE_NAME, "r")
today = time.strftime('%Y%m%d',time.localtime(time.time()))
if not os.path.exists("stocktradeinfo"):
    os.mkdir("stocktradeinfo")
if stockfile is None:
    sys.exit(1)
    log.error("Can not open the stock.list file!")

for stockcode in stockfile.readlines():
    prefix = "0"
    if len(stockcode.strip()) < 6:
        continue
    if not stockcode.startswith("6"):
        prefix = "1"
    stocktradeurl = STOCK_TRADE_DAILY_INFO_URL.format(prefix + stockcode.strip(), "19900101", today)
    urllib.urlretrieve(stocktradeurl, "stocktradeinfo/" + stockcode.strip() + ".info")
    log.info("Trade info about " + stockcode.strip() + " got.")

stockfile.close()
log.info("=====================STOCK TRADE INFO GENERATED===============================")

###########################################################
# STEP 3. Get stock trade info detail 
###########################################################


