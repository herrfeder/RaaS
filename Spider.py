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
import itertools
import pprint

from utility import eval_url, join_url, checkdir, checkfile, url_to_filename, change_useragent
from misc.settings import raas_dictconfig
from misc.settings import bcolors
import logging
from logging.config import dictConfig
import os

tag_list_link = ["a", "option","script","img"]
attr_list_link = ["href","type","src"] # action

tag_list_form = ["form"]
attr_list_form = ["action","enctype","method","name","class"]
attr_list_form_comp = ["class", "id", "name", "type", "value"]
comp_list_form = ["input","select"]

notcrawlext_list = ["epub", "pdf", "docx", "csv", "xls", "png", "jpg"]

RETS = {"too_many_requests":-5,
        "unknown_domain":-4,
        "no_crawling_extension":-3,
        "success":1}


return_vals_template = {"url":"",
                       "status":"",
                       "headers":"",
                       "result":"",
                       "cookies":"",
                       "page_source":"",
                       "source_path":"",
                       "screenshot_path":"",
                       "number_links":0,
                       "number_forms":0,
                       "type":"",
                       "request_type":"",
                       "from_attrib":""
                       }


pause_sleep = 60
too_many_requests_sleep = 120

class Spider(object):

    def __init__(self, start_url, base_dir="raas_output"):
        self.useragent = change_useragent()

        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_spider")
        self.lgg.debug("Starting Spider") 
        try:
                options = Options()
                options.add_argument('--headless')
                profile = webdriver.FirefoxProfile()
                profile.set_preference("general.useragent.override", self.useragent)
                self.br = webdriver.Firefox(profile,options=options)
                self.br.set_page_load_timeout(5)
            

        except Exception as e:
            self.lgg.error(" [!] Browser object creation error: {}".format(traceback.format_exc()))

        self.result_list = []

        self.httpreq = urllib3.PoolManager()

        self.last_visited= ""
        self.start_url = start_url
        base_url, base_url_dict = eval_url(self.start_url)
        self.base_ssl = base_url_dict["ssl"]
        self.base_port = base_url_dict["port"]
        self.base_url = base_url_dict["base_url"]

        self.last_html = ""
        self.temp_count = 0

        self.reg_dict = {}
        self.reg_dict["login"] = r'[Ll][Oo][Gg][Ii][Nn]'
        self.reg_dict["user"] = r'[Uu]sern'
        self.reg_dict["password"] = r'[Pp]asswor[td]'
        self.logged_in = False

        self.base_dir = checkdir(base_dir)
        self.tool_dir = checkdir(os.path.join(base_dir,"spider"))
        self.session_dir = checkdir(os.path.join(self.tool_dir,url_to_filename(self.base_url)))
        self.restore_file = os.path.join(self.session_dir,"session.p")
        self.result_file = os.path.join(self.session_dir,"result.p")

        self.pop_links = []

        if os.path.exists(self.restore_file):
            recover_dict = pickle.load( open(self.restore_file,"rb"))
            self.links = recover_dict.get("links","")
            self.forms = recover_dict.get("forms","")
            self.form_comps = recover_dict.get("form_comps","")
            self.visited = recover_dict.get("visited","")
        else:
            self.forms = []
            self.form_comps = []
            self.links = []
            self.visited = []

    def __wait(self):
            time.sleep(0.1)

    def close(self):
            self.br.close()

    def set_base_url(self,url):

        self.base_url = url

    def save_screenshot_source(self, result_dict, method="GET"):
        if result_dict["type"] != "nocrawlfile":
            sitedir =  checkdir(os.path.join(self.session_dir,url_to_filename(result_dict["url"])))
            if method == "GET":
                result_dict["source_path"] = os.path.join(sitedir,method+"_response_"+result_dict["status"])
                with open(result_dict["source_path"], "w") as f:
                    f.write("\n".join(["{}: {}".format(key,value) for key,value in result_dict["headers"].items()])+"\n")
                    f.write("\n\n")
                    f.write(result_dict["page_source"]+"\n")
                result_dict["page_source"] = ""
                if not result_dict["status"] in ["404", "403"]:
                    result_dict["screenshot_path"] = os.path.join(sitedir,method+"_screenshot_"+result_dict["status"]+"_"+checkfile(result_dict["url"])+".png")
                    self.br.save_screenshot(result_dict["screenshot_path"])

        return result_dict

    def check_content_type(self, result_dict):
        if isinstance(result_dict["headers"], dict):
            if result_dict["headers"].get("Content-Type") == "application/json":
                result_dict["type"] = "json"
            elif result_dict["headers"].get("Content-Type") == "text/plain":
                result_dict["type"] = "text"
        if result_dict["url"].split(".")[-1] == "js":
            result_dict["type"] = "javascript"
            #extract ajax links and forms
        if result_dict["url"].split(".")[-1] == "css":
            result_dict["type"] = "stylesheet"

        return result_dict

    def parse_link_response(self, result_dict):

        if result_dict['page_source']:
            bsoup = self.parse_html_to_bs(result_dict['page_source'])

            result_dict["number_links"] = self.extract_html_get_link(inputdata=bsoup,attrkeys=attr_list_link)
            result_dict["number_forms"] = self.extract_html_get_form(inputdata=bsoup, tagkeys=tag_list_form,attrkeys=attr_list_form)
            if result_dict["number_links"] < 1:
                self.lgg.debug("Extracted nothing on site {}".format(result_dict["url"]))

        result_entry = self.save_screenshot_source(result_dict)
        result_entry = self.check_content_type(result_entry)
        return result_entry


    def collect_links(self,link):
        if self.logged_in == True:
            if re.match("[Ll]ogout",link['link']):
                self.lgg.warning("Found logout in logged in session in URL {}. Dismiss!".format(url))
                return None

        result_dict = self.get_link_wrap(link)
        if result_dict["result"] == "exit":
            return {"result":"exit"}
        result_entry = None
        if result_dict["result"] == "success":
            result_entry = self.parse_link_response(result_dict)
            cs = bcolors.OKGREEN
        elif (result_dict["result"] != "unknown_domain") and not (result_dict["result"] == "sucess"):
            result_entry = self.parse_link_response(result_dict)
            cs = bcolors.WARNING
        elif (result_dict["result"] == "no_crawling_extension"):
            result_entry = result_dict
            cs = bcolors.OKBLUE
        else:
            cs = bcolors.HEADER

        if result_entry != None:
            self.lgg.info('''Returned from crawl:
                {cs}Result:{result}
                Status:{status}
                Links:{number_links}
                Forms:{number_forms}
                URL:{url}
                Type:{crawl_type}
                From:{from_attrib}
                Request:{request_type}{ce}'''.format(    cs=cs,
                                                    ce=bcolors.ENDC,
                                                    url=result_entry["url"],
                                                    status=result_entry["status"],
                                                    result=result_entry["result"],
                                                    number_links=result_entry["number_links"],
                                                    number_forms=result_entry["number_forms"],
                                                    crawl_type=result_entry["type"],
                                                    from_attrib=result_entry["from_attrib"],
                                                    request_type=result_entry["request_type"]))
            self.result_list.append(result_entry)
        return {"result":"success"}

    def collect_links_wrap(self, url="",limit=0):
        link = {"link":"", "attr":"", "tag":"", "request":"GET"}
        if len(self.pop_links) == 0:
            link["link"] = eval_url(url)[0]
            return_val = self.collect_links(link=link)
        while(True):
            self.pop_links = [i for n, i in enumerate(self.pop_links) if i not in self.pop_links[n + 1:]] 
            if len(self.pop_links) == 0:
                self.lgg.info("No links to process. Exiting Spider.")
                pickle.dump(self.result_list, open(self.result_file,"wb"))
                return
            try:
                link = self.pop_links.pop()
            except:
                self.lgg.info("It seems we're finished, no links to process.")
                pickle.dump(self.result_list, open(self.result_file,"wb"))
                return

            try:
                link["link"] = eval_url(link["link"])[0]
            except (WrongDomainSyntax, DomainNoIp):
                self.lgg.info("WrongDomainSyntax: "+link["link"])


            if self.check_visit(link["link"],link["request"]):
                self.lgg.debug("Insert new link {} into crawler.".format(link["link"]))
                return_val = self.collect_links(link)
                if return_val["result"] == "exit":
                    return
                self.visited.append(link)
 
            if limit != 0:
                if len(self.links)>=limit:
                    self.lgg.info("[*] We have %s links, thats enough"%(str(limit)))
                    return

    def check_visit(self, new_link, request):
        if not any(vis["link"] == new_link for vis in self.visited):
            return True
        else:
            return False

    def get_link(self,link):

        return_vals = {key:"" for key,value in return_vals_template.items()}
        return_vals["from_attrib"] = link.get("tag","")+":"+link.get("class","")+":"+link.get("attr","")
        return_vals["request_type"] = link.get("request","")

        return_vals["url"] = link["link"]
        if not link["link"].split(".")[-1] in notcrawlext_list:
            self.temp_count += 1
            return_vals["type"] = "webresource"
            self.lgg.debug("Crawl URL: {}".format(link["link"]))
            try:
                resp = self.httpreq.request("GET",link["link"])
                return_vals["headers"] = dict(resp.headers)
                return_vals["status"] = str(resp.status)
            except (urllib3_exc.MaxRetryError,urllib3_exc.LocationParseError):
                return_vals["result"] = "unknown_domain"
                return return_vals
            try:
                self.br.get(link["link"])
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
            self.last_visited = self.br.current_url
            return return_vals
        else:
            return_vals["type"] = "nocrawlfile"
            return_vals["result"] = "no_crawling_extension"
            return return_vals


    def get_link_wrap(self,link):
            try_index=0
            if self.temp_count == 30:
                time.sleep(pause_sleep)
                self.temp_count = 0

            return_vals = self.get_link(link)
            if return_vals["result"] == "too_many_requests":
                time.sleep(too_many_requests_sleep)
                self.useragent = change_useragent()
                return_vals = self.get_link(link)
                if return_vals["result"] == "too_many_requests":
                    recover_dict = {'base_url': self.base_url,
                                    'links':self.links,
                                    'visited':self.visited}
                    pickle.dump(recover_dict, open(self.restore_file,"wb"))
                    pickle.dump(self.result_list, open(self.result_file,"wb")) 
                    return {"result":"exit"}

            return return_vals


    def gen_input_attr_raw(self, inputdata, keys):
        for key in keys:
            found_attrs_list = [x for x in inputdata.find_all("", {key:re.compile(".*")})]
            for found_attrs in found_attrs_list: 
                yield {"tag":found_attrs.name, 
                        "attr":key, 
                        "link":found_attrs.attrs[key]}


    def gen_input_attr_form(self, inputdata, tagkeys, attrkeys):
        def form_get_comp_list(form, comp_el_name, attrs, index):
            comp_list = []
            comp_els = form.find_all(comp_el_name)
            for el in comp_els:
                new_el = {attr:form.get(attr,"") for attr in attrs}
                new_el["form_comp"] = comp_el_name
                new_el["index"] = index
                comp_list.append(new_el)
            return comp_list


        form_o_dict = {}
        form_comps = []
        for tagkey in tagkeys:
            forms = [x for x in inputdata.find_all(tagkey)]
            for index,form in enumerate(forms):
                for attr in attrkeys:
                    form_o_dict[attr] = form.get(attr,"")
                form_o_dict["index"] = index
                for comp in comp_list_form:
                    form_comps.extend(form_get_comp_list(form, comp, attr_list_form_comp, index))
                yield (form_o_dict, form_comps)

        

    def check_dup_link(self, new_link):
        if not any((link["link"] == new_link["link"]) & \
                  (link["request"] == new_link["request"]) for link in self.links):
            return True
        else:
            return False

    def add_link(self, link):
        if self.check_dup_link(link):
            self.lgg.debug("New link detected: {}".format(link["link"]))
            self.links.append(link)
            self.pop_links.append(link) 

            return 1
        else:
            return 0

    def add_form(self, new_form, new_form_comps):
        if self.check_dup_form(new_form):
            self.lgg.debug("New form detected: {}".format(new_form))
            self.forms.append(new_form)
            self.form_comps.extend(new_form_comps)

            self.add_link({"link":new_form["link"],
                           "tag":"form",
                           "attr":"",
                           "request":"get"})

            return 1
        else:
            return 0


    def check_dup_form(self, new_form):
        
        if not any((form["action"] == new_form["action"]) & \
                  (form["class"] == new_form["class"]) & \
                  (form["method"] == new_form["method"]) for form in self.forms):

            return True
        else:
            return False

    def extract_html_get_form(self, inputdata, tagkeys, attrkeys):
        number_forms = 0
        for form_tuple in self.gen_input_attr_form(inputdata, tagkeys, attrkeys):
            new_form, new_comps = form_tuple

            new_form["link"] = self.eval_link(new_form["action"])
            if new_form["method"] == '':
                new_form["method"] = "post"
            number_forms += self.add_form(new_form, new_comps)

        return number_forms

    def extract_html_get_link(self, inputdata, attrkeys):
        number_links = 0
        for link in self.gen_input_attr_raw(inputdata, attrkeys):
            link["link"] = self.eval_link(link["link"])
            link["request"] = "get"

            number_links += self.add_link(link)

        return number_links


    def eval_link(self, link):
        new_link = ""
        if (self.base_url in link):
            if link.startswith("//"):
                new_link = self.base_ssl+":"+link
            if link.startswith("http"):
                new_link = link
        elif (link.startswith("/")) and not (link.startswith("//")):
            new_link = join_url(self.start_url, link, urleval=True)
        elif (link.startswith("//")):
            new_link = self.base_ssl+":"+link
        
        elif (link.startswith("#")) and not \
             (self.last_visited.endswith("#")) and not \
             (self.last_visited.count("#") > 0):
            new_link = join_url(self.last_visited,link)
            new_link = ""

        return new_link

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
        spider.collect_links_wrap(url="https://eurid.eu")
    except:
        spider.br.close()
        spider.lgg.exception("Got Error:")
