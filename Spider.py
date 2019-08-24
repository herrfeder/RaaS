from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as sel_excepts
from bs4 import BeautifulSoup as bs
import traceback
import time
import re
from lxml.html.diff import htmldiff
from selenium.common.exceptions import WebDriverException
from exceptions import WrongDomainSyntax, DomainNoIp
from IPython.core.debugger import Tracer; debughere = Tracer()
from selenium.webdriver.firefox.options import Options
import operator
from functools import reduce
import urllib3
import urllib3.exceptions as urllib3_exc
import pickle

from utility import eval_url, join_url, checkdir, checkfile, url_to_filename
from misc.settings import raas_dictconfig
from misc.settings import bcolors
import logging
from logging.config import dictConfig
import os

tag_list = ["a", "form", "option","script","img"]
attr_list = ["href","type","src","action"]
notcrawlext_list = ["pdf", "docx", "csv", "xls", "png", "jpg"]

return_vals_template = {"url":"",
                       "status":"",
                       "headers":"",
                       "result":"",
                       "cookies":"",
                       "page_source":"",
                       "source_path":"",
                       "screenshot_path":"",
                       "number_links":0,
                       "type":""
                       }


service_args = [
    '--proxy=127.0.0.1:8090',
    '--proxy-type=http',
    ]

class Spider(object):

    def __init__(self, start_url, base_dir="raas_output"):
        self.useragent = "Mozilla/5.0"

        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_spider")
        self.lgg.debug("Starting Spider") 
        try:
                options = Options()
                options.add_argument('--headless')
                self.br = webdriver.Firefox(options=options)
                self.br.set_page_load_timeout(5)

        except Exception as e:
            self.lgg.ERROR(" [!] Browser object creation error: {}".format(traceback.format_exc()))

        self.result_list = []

        self.httpreq = urllib3.PoolManager()

        self.forms_and_inputs = {}
        self.clicked_links = []
        self.last_url = ""
        self.start_url = start_url
        base_url, base_url_dict = eval_url(self.start_url)
        self.base_ssl = base_url_dict["ssl"]
        self.base_port = base_url_dict["port"]
        self.base_url = base_url_dict["base_url"]

        self.last_html = ""

        self.reg_dict = {}
        self.reg_dict["login"] = r'[Ll][Oo][Gg][Ii][Nn]'
        self.reg_dict["user"] = r'[Uu]sern'
        self.reg_dict["password"] = r'[Pp]asswor[td]'
        self.logged_in = False

        self.base_dir = checkdir(base_dir)
        self.tool_dir = checkdir(os.path.join(base_dir,"spider"))
        self.session_dir = checkdir(os.path.join(self.tool_dir,url_to_filename(self.base_url)))
        self.restore_file = os.path.join(self.session_dir,"session.p")
   
        if os.path.exists(self.restore_file):
            recover_dict = pickle.load( open(self.restore_file,"rb"))
            self.links = recover_dict["links"]
            self.visited = recover_dict["visited"]
        else:

            self.links = []
            self.visited = []

    def __wait(self):
            time.sleep(0.1)

    def close(self):
            self.br.close()

    def set_base_url(self,url):

        self.base_url = url

    def process_link_response(self, result_dict, method="GET"):
        if result_dict != "nocrawlfile":
            sitedir =  checkdir(os.path.join(self.session_dir,url_to_filename(result_dict["url"])))
            if method == "GET":
                result_dict["source_path"] = os.path.join(sitedir,method+"_response_"+result_dict["status"]+"_"+checkfile(result_dict["url"]))
                with open(result_dict["source_path"], "w") as f:
                    f.write("\n".join(["{}: {}".format(key,value) for key,value in result_dict["headers"].items()])+"\n")
                    f.write("\n\n")
                    f.write(result_dict["page_source"]+"\n")
                result_dict["page_source"] = ""
                if not result_dict["status"] in ["404", "403"]:
                    result_dict["screenshot_path"] = os.path.join(sitedir,method+"_screenshot_"+result_dict["status"]+"_"+checkfile(result_dict["url"])+".png")
                    self.br.save_screenshot(result_dict["screenshot_path"])

        return result_dict

    def parse_link_response(self, result_dict):

        if result_dict['page_source']:
            bsoup = self.parse_html_to_bs(result_dict['page_source'])
            templinks = [bsoup.findAll(x) for x in tag_list]
            templinks = reduce(operator.add, templinks)
            self.get_input_attr_raw(inputdata=templinks,keys=attr_list)
            result_dict["number_links"] = self.extract_link(keys=attr_list)
            if result_dict["number_links"] < 1:
                self.lgg.debug("Extracted nothing on site {}".format(result_dict["url"]))

        result_entry = self.process_link_response(result_dict)

        return result_entry


    def collect_links(self,url):
        if self.logged_in == True:
            if re.match("[Ll]ogout",url):
                self.lgg.warning("Found logout in logged in session in URL {}. Dismiss!".format(url))
                return None

        result_dict = self.get_link_wrap(url)

        if result_dict["result"] == "exit":
            return "exit"
        result_entry = None
        if result_dict["result"] == "success":
            result_entry = self.parse_link_response(result_dict)
        elif (result_dict["result"] != "unknown_domain") and not (result_dict["result"] == "sucess"):
            result_entry = self.parse_link_response(result_dict)
        self.lgg.info("Returned from crawl:\n{cs}Result:{result}\t\tStatus:{status}\t\tLinks:{number_links}\t\tURL:{url}{ce}".format(cs=bcolors.OKGREEN, ce=bcolors.ENDC,
                                                                                                               url=result_entry["url"],
                                                                                                               status=result_entry["status"],
                                                                                                               result=result_entry["result"],
                                                                                                               number_links=result_entry["number_links"] ))
        if result_entry != None:
            self.result_list.append(result_entry)
            return None


    def collect_all_links(self, url="",limit=0):
        if len(self.links) == 0:
            url = eval_url(url)[0]
            return_val = self.collect_links(url=url)
        while(True):
            self.links = list(set(self.links))
            if len(self.links) == 0:
                self.lgg.info("No links to process. Exiting Spider.")
                return
            link = self.links.pop()
            if link not in self.visited:
                self.lgg.debug("Insert new link {} into crawler.".format(link))
                return_val = self.collect_links(link)
                if return_val == "exit":
                    return
                self.visited.append(link)
 
            if limit != 0:
                if len(self.links)>=limit:
                    self.lgg.info("[*] We have %s links, thats enough"%(str(limit)))
                    return

    def get_link(self,in_url):

        return_vals = return_vals_template

        try:
            url = eval_url(in_url)[0]
            self.lgg.debug("URL before eval {} and after {}".format(in_url,url))
        except (WrongDomainSyntax,DomainNoIp) as e:
            self.lgg.exception("WrongDomainSyntax or DomainNoIp")

        return_vals["url"] = url
        if not url.split(".")[-1] in notcrawlext_list:
            return_vals["type"] = "webresource"
            self.lgg.debug("Crawl URL: {}".format(url))
            try:
                resp = self.httpreq.request("GET",url)
                return_vals["headers"] = dict(resp.headers)
                return_vals["status"] = str(resp.status)
            except urllib3_exc.MaxRetryError:
                return_vals["result"] = "unknown_domain"
                return return_vals
            try:
                self.br.get(url)
            except sel_excepts.InvalidArgumentException:
                return_vals["result"] = "invalid_request"
                return return_vals
            except (sel_excepts.UnexpectedAlertPresentException, sel_excepts.TimeoutException): # reCAPTCHA exception
                return_vals["result"] = "too_many_requests"
                return return_vals

            try:
                return_vals["page_source"] = self.br.page_source
            except sel_excepts.WebDriverException:
                return_vals["page_source"] = ""
                return_vals["result"] = "bs_parsing_error"
                return return_vals
            self.last_html = return_vals["page_source"]
            return_vals["cookies"] = self.br.get_cookies()
            return_vals["result"] = "success"
            if self.logged_in == False:
                self.br.delete_all_cookies()
            return return_vals
        else:
            return_vals["type"] = "nocrawlfile"
            return_vals["result"] = "no_crawling_extension"
            return return_vals 


    def get_link_wrap(self,url):
            try_index=0
            return_vals = self.get_link(url)
            '''
            while(try_index<5):
                if return_vals["result"] == "success":
                    return return_vals
                elif return_vals["result"] == "too_many_requests":
                    self.lgg.warning("We've send too many requests, the webserver enables mechanisms to protect from crawling.") 
                    time.sleep(5)
                    # improve to :change useragent and openvpn
                    return_vals = self.get_link(url)
                else:
                    print("IM HERE NOW")

                try_index += 1
                
                if try_index == 5:
                    recover_dict = {'base_url': self.base_url,
                                    'links':self.links,
                                    'visited':self.visited}
                    pickle.dump(recover_dict, open(self.restore_file,"wb")) 
                    return {"result":"exit"}
            return None
            '''
            return return_vals



    def get_input_attr_raw(self, inputdata, keys):
        self.input_pairs = []
        process_data = inputdata
        for inputfield in process_data:
            for attr in inputfield.attrs:
                for key in keys:
                    if str(attr) == key:
                        self.input_pairs.append((key,inputfield.attrs[key]))

        return self.input_pairs



    def get_input_attr_form(self, key, formindex=0):
        self.input_pairs = []
        process_data = self.forms_and_inputs[self.last_url][formindex][1:-1]
        for inputfield in process_data:
            for attr in inputfield.attrs:
                if str(attr) == key:
                    self.input_pairs.append({key:inputfield.attrs[key]})

        return self.input_pairs




    def extract_link(self, keys):
        templinks = []
        number_links = 0
        for pair in self.input_pairs:
                key = pair[0]
                value = pair[1]
                new_link = ""
                # baseURL is in link
                if (self.base_url in value):
                    if value.startswith("//"):
                        new_link = self.base_ssl+":"+value
                    if value.startswith("http"):
                        new_link = value
                elif (value.startswith("/")) and not (value.startswith("//")):
                    new_link = join_url(self.start_url, value, urleval=True)
                elif (value.startswith("//")):
                    new_link = self.base_ssl+":"+value
                if (new_link not in self.links) and (new_link != ""):
                    number_links += 1
                    self.links.append(new_link)
        return number_links

    def parse_html_to_bs(self,data):
        try:
            temp_bs = bs(data,"lxml")
        except Exception as e:
            self.lgg.exception("ERROR in BeautifulSoup Parser:")
            return None
        return temp_bs

if __name__ == "__main__":
    spider = Spider("https://eurid.eu")
    try:
        spider.collect_all_links(url="https://eurid.eu")
    except:
        spider.br.close()
        spider.lgg.exception("Got Error:")
