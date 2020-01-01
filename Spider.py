import threading
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as sel_excepts
from bs4 import BeautifulSoup as bs
import traceback
import time
import re
from lxml.html.diff import htmldiff
from selenium.common.exceptions import WebDriverException
from exceptions import WrongDomainSyntax, DomainNoIp, ServerBlocked, SpiderError
from IPython.core.debugger import Tracer; debughere = Tracer()
from selenium.webdriver.firefox.options import Options
import operator
from functools import reduce
import urllib3
import urllib3.exceptions as urllib3_exc
import pickle
import itertools
import pprint
import uuid
import sys

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

notcrawlext_list = ["epub", "pdf", "docx", "csv", "xls", "png", "jpg", "zip", "xml"]

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
too_many_requests_sleep = 240
page_load_timeout = 20

class Spider(threading.Thread):

    def __init__(self, env, start_url, base_dir="raas_output",limit=""):
        super(Spider , self).__init__()
        self.fin = 0
        # Preparing Config and Logger
        dictConfig(raas_dictconfig)
        self.lgg = logging.getLogger("RAAS_spider")

        # Preparing Selenium Browser and urllib3 client
        self.br = []
        self.httpreq = urllib3.PoolManager()

        # Init some variables for runtime      
        self.last_visited= ""
        self.last_html = ""
        self.temp_count = 0

        # Getting and evaluate Start URL
        self.start_url = start_url
        base_url, base_url_dict = eval_url(self.start_url)
        self.base_ssl = base_url_dict["ssl"]
        self.base_port = base_url_dict["port"]
        self.base_url = base_url_dict["base_url"]
        self.final_url = base_url_dict["final_url"]

        # Prepare some Regex Variables
        self.reg_dict = {}
        self.reg_dict["login"] = r'[Ll][Oo][Gg][Ii][Nn]'
        self.reg_dict["user"] = r'[Uu]sern'
        self.reg_dict["password"] = r'[Pp]asswor[td]'
        self.logged_in = False

        # Create directories for storing data
        self.base_dir = checkdir(base_dir)
        self.tool_dir = checkdir(os.path.join(base_dir,"spider"))
        self.session_dir = checkdir(os.path.join(self.tool_dir,url_to_filename(self.base_url)))
        self.restore_file = os.path.join(self.session_dir,"session.p")
        self.result_file = os.path.join(self.session_dir,"result.p")
        self.form_file = os.path.join(self.session_dir,"form.p")
        self.form_comps_file = os.path.join(self.session_dir,"form_comps.p")


        self.limit = limit
        #Init or loading (after exiting before finish) runtime variables that collects all desired data
        if os.path.exists(self.result_file):
            self.result_list = pickle.load(open(self.result_file, "rb"))
        else:
            self.result_list = []

        if os.path.exists(self.restore_file):
            self.lgg.info("We've found an session file. We will continue.")
            recover_dict = pickle.load( open(self.restore_file,"rb"))
            self.links = recover_dict.get("links","")
            self.pop_links = recover_dict.get("pop_links","")
            self.forms = recover_dict.get("forms","")
            self.form_comps = recover_dict.get("form_comps","")
            self.visited = recover_dict.get("visited","")
        else:
            self.forms = []
            self.form_comps = []
            self.links = []
            self.pop_links = []
            self.visited = []

        self.thread = threading.Thread(target=self.run, args=(self.final_url))
        self.thread.deamon = True

    def run(self):
        self.lgg.info("[*] Running Module: Spider ")
        while True:
            try:
                self.init_browser()
                self.collect_links_wrap(self.final_url,limit=self.limit)
                return self.finish_return_crawler_state()
            except ServerBlocked:
                self.lgg.exception("Got Error ServerBlocked.")
                self.store_crawler_state()
                time.sleep(3600)
            except SpiderError:
                self.lgg.exception("Got Error SpiderError.")
                self.store_crawler_state()
                time.sleep(60)


    def init_browser(self):

        self.useragent = change_useragent()
        self.lgg.debug("Start Spider with new Useragent: {}".format(self.useragent))
        if self.br:
            self.finish_browser()
        try:
                options = Options()
                options.add_argument('--headless')
                profile = webdriver.FirefoxProfile()
                profile.set_preference("general.useragent.override", self.useragent)
                self.br = webdriver.Firefox(profile,options=options)
                self.br.set_page_load_timeout(page_load_timeout)

        except Exception as e:
            self.lgg.error(" [!] Browser object creation error: {}".format(traceback.format_exc()))


    def finish_browser(self):

        self.last_html = ""
        self.last_visited = ""
        self.br.close()
        self.br = []


    def store_crawler_state(self):

        recover_dict = {'base_url': self.base_url,
                        'links':self.links,
                        'visited':self.visited,
                        'forms':self.forms,
                        'form_comps':self.form_comps,
                        'pop_links':self.pop_links}
        pickle.dump(recover_dict, open(self.restore_file,"wb"))
        pickle.dump(self.result_list, open(self.result_file,"wb"))
        self.finish_browser()
        self.lgg.info("Spider stops. Will start again after some time.")
        return 1

    def finish_return_crawler_state(self):

        pickle.dump(self.result_list, open(self.result_file,"wb"))
        pickle.dump(self.forms, open(self.form_file,"wb"))
        pickle.dump(self.form_comps, open(self.form_comps_file,"wb"))
        try:
            os.remove(self.restore_file)
        except:
            pass
        self.finish_browser()
        self.fin = 1
        self.result_tuple = (self.result_list, self.forms, self.form_comps)
        return self.result_tuple

    def __wait(self):
            time.sleep(0.1)

    def close(self):
            self.br.close()


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
            if result_dict["number_links"] < 1:
                self.lgg.debug("Extracted nothing on site {}".format(result_dict["url"]))
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
            # Collect first link
            return_val = self.collect_links(link=link)
        while(True):
            self.pop_links = [i for n, i in enumerate(self.pop_links) if i not in self.pop_links[n + 1:]] 
            if len(self.pop_links) == 0:
                self.lgg.info("No links to process. Exiting Spider.")
                return
            try:
                link = self.pop_links.pop()
            except:
                self.lgg.info("It seems we're finished, no links to process.")
                return

            try:
                link["link"] = eval_url(link["link"])[0]
            except (WrongDomainSyntax, DomainNoIp):
                self.lgg.info("WrongDomainSyntax: "+link["link"])


            if (self.check_visit(link["link"],link["request"])) and (self.check_link(link["link"])):
                self.lgg.debug("Insert new link {} into crawler.".format(link["link"]))
                # Collect new link
                return_val = self.collect_links(link)
                if return_val["result"] == "exit":
                    self.lgg.exception("Got Error:")
                    raise SpiderError
                else:
                    self.visited.append(link)

            if limit != 0:
                if len(self.result_list)>=limit:
                    self.lgg.info("[*] We have %s links, thats enough"%(str(limit)))
                    return


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
                return_vals["headers"] = str(dict(resp.headers))
                return_vals["status"] = str(resp.status)
            except (urllib3_exc.MaxRetryError,urllib3_exc.LocationParseError):
                return_vals["result"] = "unknown_domain"
                return return_vals

            while True:
                try:
                    self.br.get(link["link"])
                except sel_excepts.InvalidArgumentException:
                    return_vals["result"] = "invalid_request"
                    return return_vals
                except (sel_excepts.UnexpectedAlertPresentException, sel_excepts.TimeoutException): # reCAPTCHA exception
                    self.lgg.exception("Got Error:")
                    return_vals["result"] = "too_many_requests"
                    return return_vals
                except (sel_excepts.WebDriverException): # Page Reload
                    self.lgg.exception("Got Error:")
                    continue
                break

            try:
                return_vals["page_source"] = self.br.page_source
            except sel_excepts.WebDriverException:
                return_vals["page_source"] = ""
                return_vals["result"] = "bs_parsing_error"
                return return_vals
            self.last_html = return_vals["page_source"]
            return_vals["cookies"] = str(self.br.get_cookies())
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
                self.lgg.info("Pausing for 30 seconds after 30 Requests. WAF and stuff :)")
                time.sleep(pause_sleep)
                self.temp_count = 0

            return_vals = self.get_link(link)

            temp_sleep = too_many_requests_sleep
            try_counter = 0
            while return_vals["result"] == "too_many_requests":
                self.lgg.info("Too many requests. Will rest for {} seconds".format(temp_sleep))
                time.sleep(temp_sleep)
                self.init_browser()
                return_vals = self.get_link(link)
                temp_sleep += 300
                try_counter += 1
                if try_counter == 5:
                    self.lgg.info("We got blocked by the web server. Saving state and exiting.")
                    raise ServerBlocked
            else:
                return return_vals


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

            result_entry = self.check_content_type(result_dict)
            if (result_entry["type"] == "javascriptasdfdsa") and (result_entry["status"] != 404):
                self.extract_html_get_js(inputdata=bsoup)
            elif (result_entry["type"] == "stylesheetadsfasdf") and (result_entry["status"] != 404):
                self.extract_html_get_css(inputdata=bsoup)
            else:
                result_dict["number_links"] = self.extract_html_get_link(inputdata=bsoup,attrkeys=attr_list_link)
                result_dict["number_forms"] = self.extract_html_get_form(inputdata=bsoup, tagkeys=tag_list_form,attrkeys=attr_list_form)

        result_entry = self.save_screenshot_source(result_dict)
        return result_entry


    def check_visit(self, new_link, request):
        if not any(vis["link"] == new_link for vis in self.visited):
            return True
        else:
            return False


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


        form_o_list = []
        form_comps_list = []
        tagkey = "form"
        forms = [x for x in inputdata.find_all(tagkey)]
        for form in forms:
            form_o_dict = {}

            # collect HTML attribute values for desired forms
            for attr in attrkeys:
                form_o_dict[attr] = str(form.get(attr,""))

            # create unique ID for matching form with form fields in seperate table
            form_o_dict["id"] = str(uuid.uuid1())

            # append forms for one HTML source
            form_o_list.append(form_o_dict)

            # collect form components for each form and create list of list of dicts
            form_comps = []
            for comp in comp_list_form:
                form_comps.extend(form_get_comp_list(form, comp, attr_list_form_comp, form_o_dict["id"]))
            form_comps_list.append(form_comps)

        return (form_o_list, form_comps_list)

 
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

    def check_dup_link(self, new_link):
        if not any((link["link"] == new_link["link"]) & \
                  (link["request"] == new_link["request"]) for link in self.links):
            return True
        else:
            return False


    def check_dup_form(self, new_form):
        if len(self.forms) == 0:
            return True

        if not any(all([ form["action"] == new_form["action"],
                         form["class"] == new_form["class"],
                         form["method"] == new_form["method"] ]) for form in self.forms):
            return True
        else:
            return False

    def extract_html_get_form(self, inputdata, tagkeys, attrkeys):
        number_forms = 0
        new_form_list, new_comps_list = self.gen_input_attr_form(inputdata, tagkeys, attrkeys)
        for new_form, new_comps in zip(new_form_list, new_comps_list):
            new_form["link"] = self.eval_link(new_form["action"])
            if new_form["method"] == '':
                new_form["method"] = 'get'
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
                new_link = join_url(self.base_ssl+":",link, urleval=True)
            if link.startswith("http"):
                new_link = join_url(link,urleval=True)

        elif (link.startswith("/")) and not (link.startswith("//")):
            new_link = join_url(self.start_url, link, urleval=True)

        elif (link.startswith("#")) and not \
             (self.last_visited.endswith("#")) and not \
             (self.last_visited.count("#") > 0):
            new_link = join_url(self.last_visited,link,urleval=True)
            new_link = ""

        return new_link

    def check_link(self,link_string):
        try:
            eval_url(link_string)
            return True
        except:
            return False

    def parse_html_to_bs(self,data):
        try:
            temp_bs = bs(data,"lxml")
        except Exception as e:
            self.lgg.exception("ERROR in BeautifulSoup Parser:")
            return None
        return temp_bs


if __name__ == "__main__":
    spider = Spider(env="",start_url="https://eurid.eu")
    spider.run(limit=20)
