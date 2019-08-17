from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as sel_excepts
from bs4 import BeautifulSoup as bs
import traceback
import time
import re
from lxml.html.diff import htmldiff
from selenium.common.exceptions import WebDriverException
from utility import eval_url, join_url
from exceptions import WrongDomainSyntax, DomainNoIp
from IPython.core.debugger import Tracer; debughere = Tracer()
from selenium.webdriver.firefox.options import Options
import operator
from functools import reduce

tag_list = ["a", "form", "option","script","img"]
attr_list = ["href","type","src","action"]



service_args = [
    '--proxy=127.0.0.1:8090',
    '--proxy-type=http',
    ]

class Spider(object):

    def __init__(self, base_url):
        self.useragent = "Mozilla/5.0"

        try:
                options = Options()
                options.add_argument('--headless')
                self.br = webdriver.Firefox(options=options)
                self.br.set_page_load_timeout(5)

        except Exception as e:
            print(" [!] Browser object creation error: {}".format(e))

        self.forms_and_inputs = {}
        self.links = []
        self.clicked_links = []
        self.last_url = ""
        self.base_url = base_url

        self.last_response = ""
        self.last_html = ""
        self.reg_dict = {}
        self.temp_visited = []

        self.reg_dict["login"] = r'[Ll][Oo][Gg][Ii][Nn]'
        self.reg_dict["user"] = r'[Uu]sern'
        self.reg_dict["password"] = r'[Pp]asswor[td]'
        self.login = False


    def __wait(self):
            time.sleep(0.1)

    def close(self):
            self.browser.close()

    def set_base_url(self,url):

        self.base_url = url

    def collect_link(self,url=""):
        if url == "":
            bsoup = self.parse_html_to_bs(self.last_html)
        else:
            self.temp_visited.append(url)
            if "logout" in url:
                print("found logout")
                return
            result = self.get_link_sure(url)

            if result == False:
                return
            else:
                bsoup = self.parse_html_to_bs(result)
        templinks = []
        if bsoup != None:

            templinks = [bsoup.findAll(x) for x in tag_list]
            templinks = reduce(operator.add, templinks)

            self.get_input_attr_raw(inputdata=templinks,keys=attr_list)
            number_links = self.extract_link(keys=attr_list)
            return number_links
        return None

    def parse_html_to_bs(self,data):
        try:
            temp_bs = bs(data,"lxml")
        except Exception as e:
            logging.warning("ERROR: %s"%(e))
            return None
        return temp_bs

    def collect_all_links(self, url="",limit=0):
        url = eval_url(url)[0]
        self.collect_link(url=url)
        for link in self.links:
            if link not in self.temp_visited:
                print("[+] added link:".format(link))
                self.collect_link(link)

                self.temp_visited.append(link)
        if limit != 0:
            if len(self.links)>=limit:
                print("[*] We have %s links, thats enough"%(str(limit)))
                return

    def get_link(self,url,returntype="raw",response=""):

        try:
            url = eval_url(url)[0]
        except (WrongDomainSyntax,DomainNoIp) as e:
            print(e)

        if response=="":
            if not url.split(".")[-1] in ["pdf","docx"]:
                print("URL to get: {}".format(url))
                try:
                    self.br.get(url)
                except sel_excepts.InvalidArgumentException:
                    return False
                except sel_excepts.UnexpectedAlertPresentException: # reCAPTCHA exception
                    time.sleep(300)
                    self.br.get(url)
                self.last_html = self.br.page_source
        else:
            self.last_response = response
        if returntype == "raw":
            return self.last_html

    def get_link_sure(self,url,returntype="raw",response=""):
            try_index=0
            self.get_link(url,returntype="raw",response="")
            if self.login == False:
                return self.last_html
            while(url not in self.br.current_url):
                logging.warning("have to load site again: %s instead of %s"%(self.br.current_url,url) )
                return_val = self.get_link(url,returntype="raw",response="")
                if return_val == False:
                    return False
                time.sleep(0.5)
                try_index += 1
                if try_index == 5:
                    return self.last_html
            return self.last_html

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
                    try:
                        self.input_pairs.append({key:inputfield.attrs[key]})
                    except Exception as e:
                        print(e)

        return self.input_pairs




    def extract_link(self, keys):
 
        templinks = []
        number_links = 0
        for pair in self.input_pairs:
                key = pair[0]
                value = pair[1]
                # baseURL is in link
                if (self.base_url.replace("http://","").replace("https://","") in value) or \
                (value.startswith("/")) or \
                ((re.search("^[a-zA-Z0-9]",value) and not (re.search("^(http)",value)))) or \
                (value.endswith("php")):
                    new_link = join_url(self.base_url,value)
                    print("New link:{}".format(new_link))
                    if new_link not in self.links:
                        number_links += 1
                        print("[*] discovered new link: {}".format(new_link))
                        self.links.append(new_link)

        return number_links

if __name__ == "__main__":

    spider = Spider("https://eurid.eu")
    spider.collect_all_links(url="https://eurid.eu")
