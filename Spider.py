from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs
import time
import re
from lxml.html.diff import htmldiff
from selenium.common.exceptions import WebDriverException
from utility import eval_url
from exceptions import WrongDomainSyntax, DomainNoIp
from IPython.core.debugger import Tracer; debughere = Tracer()

service_args = [
    '--proxy=127.0.0.1:8090',
    '--proxy-type=http',
    ]


class SelObject(object):

    def __init__(self, base_url):
        self.useragent = "Mozilla/5.0"
        #profile = webdriver.PhantomJSProfile()
        #profile.set_preference("general.useragent.override",useragent)

        try:
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')
                self.br = webdriver.Firefox(firefox_options=options)
                self.br.set_page_load_timeout(10)

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
            time.sleep(2)

    def close(self):
            self.browser.close()

    def set_base_url(self,url):

        self.base_url = url

    def collect_link(self,url=""):
        index = 0
        if url == "":
            bsoup = self.parse_html_to_bs(self.last_html)
        else:
            self.temp_visited.append(url)
            if "logout" in url:
                return
            result = self.get_link_sure(url)

            if result == False:
                return
            else:
                bsoup = self.parse_html_to_bs(result)
        if bsoup != None:
            #templinks = bsoup.findAll("a")
            #self.get_input_attr(inputdata=templinks,key="href")
            #templinks = self.extract_link()
  
            keys=["href","type"]
            templinks = bsoup.findAll("link")
            self.get_input_attr_raw(inputdata=templinks, key=keys)
            new_links = self.extract_link(keys)

            debughere()

            for link in templinks:
                tempurl = self.base_url
                if not link.startswith("/"):
                    tempurl = self.base_url+"/"
                if link.startswith("http"):
                    new_link = link
                elif link.startswith(self.base_url):
                    new_link = "https://"+link
                else:
                    new_link = tempurl+link
                if new_link not in self.links:
                    print("[*] discovered new link: {}".format(new_link))
                    self.links.append(new_link)

    

    def parse_html_to_bs(self,data):
        try:
            temp_bs = bs(data,"lxml")
        except Exception as e:
            logging.warning("ERROR: %s"%(e))
            return None
        return temp_bs

    def collect_all_links(self, url="",limit=0):
        try:
            if self.links[0]:
                pass
        except:
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
        #print(url)
        if not self.base_url:
            self.base_url = url
        self.last_url = url
        #if "logout" in url: ### VERY IMPORTANT, BUT NEEDS ENHANCEMENT
        #    logging.warning("There was logout in the url")
        #return False
        if response=="":
            try:
                if not url.split(".")[-1] in ["pdf","docx"]:
                    print("URL to get: {}".format(url))
                    self.br.get(url)
                    self.last_html = self.br.page_source
            except WebDriverException as e:
                print(e)
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
                time.sleep(0.5)
                self.get_link(url,returntype="raw",response="")
                try_index += 1
                if try_index == 5:
                    return self.last_html
            return self.last_html

    def get_input_attr_raw(self, inputdata, key):
        self.input_pairs = []

        process_data = inputdata
        for inputfield in process_data:
            for attr in inputfield.attrs:
                print(attr)
                if str(attr) == key:
                    try:
                        self.input_pairs.append({key:inputfield.attrs[key]})
                    except Exception as e:
                        print(e)

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
        for pair in self.input_pairs:
                if (self.base_url.replace("http://","").replace("https://","") in pair["href"]) or \
                (pair["href"].startswith("/")) or \
                ((re.search("^[a-zA-Z0-9]",pair["href"]) and not (re.search("^(http)",pair["href"])))) or \
                (pair["href"].endswith("php")):
                    
                    temp_dict = [dict(item, **{key:pair[key]}) for key in keys]
                    templinks.append(temp_dict)

        return templinks
