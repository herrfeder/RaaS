from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as bs
import time
import pdb
import re
from lxml.html.diff import htmldiff
from selenium.webdriver.common.keys import Keys
import logging
from selenium.common.exceptions import WebDriverException
service_args = [
    '--proxy=127.0.0.1:8090',
    '--proxy-type=http',
]

class SelObject(object):

    def __init__(self):
        self.useragent = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25"
        #profile = webdriver.PhantomJSProfile()
        #profile.set_preference("general.useragent.override",useragent)

        try:
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')
                self.br = webdriver.Firefox(firefox_options=options)
 
        except Exception as e:
            print(" [!] Browser object creation error: {}".format(e))

        self.forms_and_inputs = {}
        self.links = []
        self.clicked_links = []
        self.last_url = ""
        self.base_url = ""

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

        self.base_url = self.parse_malformed_url(url)

    def collect_link(self,url=""):
        index = 0
        if url == "":
            bsoup = self.parse_html_to_bs(self.last_html)
        else:
            self.temp_visited.append(url)
            #if "logout" in url:
            #    return
            result = self.get_link_sure(url)

            if result == False:
                return
            else:
                bsoup = self.parse_html_to_bs(result)
        if bsoup != None:
            templinks = bsoup.findAll("a")
            #for link in templinks:
            #    print link.attrs
            self.get_input_attr(inputdata=templinks,key="href")
            templinks = []
            for pair in self.input_pairs:
                if (self.base_url.replace("http://","").replace("https://","") in pair["href"]) or \
                (pair["href"].startswith("/")) or \
                ((re.search("^[a-zA-Z0-9]",pair["href"]) and not (re.search("^(http)",pair["href"])))) or \
                (pair["href"].endswith("php")):
                    templinks.append(pair["href"])

            for link in templinks:
                print(link)
                if not self.base_url.endswith("/"):
                    tempurl = self.base_url+"/"
                else:
                    tempurl = self.base_url

                if link.startswith("http"):
                    new_link = link
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

    def get_reg(self, key):
        return self.reg_dict[key]


    def find_all_forms(self,url="",response=""):
        if response == "":
            bsoup = self.parse_html_to_bs(self.get_link_sure(url=url))
            time.sleep(0.5)
        else:
            bsoup = response
        if bsoup != None:
            print(self.br.current_url)
            print(url)
            #if "text-file-viewer.php" in url:
            #    pdb.set_trace()
            forms = bsoup.findAll("form")
            form_temp_list = []
            for form in forms:
                inner_temp_list = []
                inputs = form.findAll("input")
                buttons = form.findAll("button")
                inner_temp_list.append(form)
                for element in inputs:
                    inner_temp_list.append(element)
                for button in buttons:
                    inner_temp_list.append(button)
                form_temp_list.append(inner_temp_list)

            self.forms_and_inputs[self.parse_malformed_url(url)] = form_temp_list

    def parse_malformed_url(self,url):
            if url.startswith("127.0.0.1"):
                url = "http://"+url
            elif not url.startswith("http"):
                url = "http://"+url
            return url

    def inject_sql(self,url="",index=0, subtype=""):
        if url != "":
            if not self.forms_and_inputs[url]:
                print("No forms on the site %s"%(url))
                return

        with open("sqli.txt","r") as f:
            self.sqli_list = f.readlines()
        f.close()

        if url == "":
            tempurl = self.links[index]
        else:
            tempurl = url

        self.get_link(url=tempurl)
        if self.login_page in self.br.current_url():
            self.do_login("admin","password")
            self.get_link(url=tempurl)

        for sqli in self.sqli_list:
            #print "URL:"+tempurl
            #print "SQLI:"+sqli
            self.submit_form_fields(payload=sqli, formindex=index,
                                    inputindex=0, subtype=subtype)

    def process_response(self,before_data,after_data, process_type = "injection", payloadpattern=""):
        diff_data = bs(str(htmldiff(after_data,before_data).split("<del>")[1:-1]))

        #pdb.set_trace()

        if process_type == "injection":
            if re.search(r'[sS][qQ][lL]',diff_data.text):
                try:
                    print(after_data.geturl())
                except:
                    pass
                #pdb.set_trace()

            if payloadpattern != "":
                if re.search(payloadpattern,after_data):
                    print("YESS YOU GOT IT")
                    pdb.set_trace()




    def check_login(self):

        if not self.forms_and_inputs:
            return
        try:
            for element in self.forms_and_inputs[self.last_url][0][1:-1]:
                if re.search(self.get_reg("login"),str(element)):
                    try:
                        if self.forms_and_inputs[self.last_url][1]:
                            pass
                    except:
                        self.login_page = self.br.current_url
                        return True

                    logging.warning("Other forms to try")
                    self.login=True
                    return False
        except Exception as e:
            print(e)
            self.login=True
            return False

    def check_valid_login_form(self,text):

        if re.search(self.get_reg("password"), text):
            return True
        else:
            return False

    def do_login(self, username, password, authtype="form"):
        key = "name"
        if authtype=="form":
            if not self.login_page in self.br.current_url:
                self.get_link(self.login_page)
            select = self.br.find_element_by_tag_name("form")
            if not self.check_valid_login_form(select.text):
                logging.warning("No login form found")
                return
            userfield = select.find_element_by_name("username")
            userfield.send_keys(username)
            passfield = select.find_element_by_name("password")
            passfield.send_keys(password)
            passfield.send_keys(Keys.ENTER)
            '''login_field = select.find_element_by_name("Login")
            login_field = self.br.find_element_by_xpath("//*[@type='submit']")
            login_field.submit()'''
            # why does this not work ???

            #self.get_input_attr()
            #for pair in self.input_pairs:
            #    if re.search(self.get_reg("user"),pair[key]):
            #        self.br.form[pair[key]]=username
            #    if re.search(self.get_reg("password"),pair[key]):
            #        self.br.form[pair[key]]=password

        #self.last_response = self.br.submit()
        #time.sleep(1)
        #pdb.set_trace()
        self.last_html = self.br.page_source
        self.login = True
        #print self.cookies


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


    def get_link(self,url,returntype="raw",response=""):

        url = self.parse_malformed_url(url)
        if not self.base_url:
            self.base_url = url
        self.last_url = url
        if "logout" in url: ### VERY IMPORTANT, BUT NEEDS ENHANCEMENT
            logging.warning("There was logout in the url")
            return False
        if response=="":
            try:
                self.br.get(url)
                self.last_html = self.br.page_source
            except WebDriverException:
                try:
                    self.br.get(url.replace("http","https"))
                    self.last_html = self.br.page_source
                except:
                    pass
        else:
            self.last_response = response
        if returntype == "raw":
            return self.last_html


    def get_input_attr(self, inputdata="",key="name",formindex=0):
        self.input_pairs = []
        if inputdata=="":
            process_data = self.forms_and_inputs[self.last_url][formindex][1:-1]
        else:
            process_data = inputdata
        for inputfield in process_data:
            for attr in inputfield.attrs:
                if str(attr) == key:
                    try:
                        self.input_pairs.append({key:inputfield.attrs[key]})
                    except Exception as e:
                        print(e)

        return self.input_pairs


    def modify_cookie(self, payload):

        self.cookies = self.br.get_cookies()

        cur_cookie = self.cookies[0]

        cookie_value = cur_cookie["value"]
        cur_cookie["value"] = cookie_value+payload

        self.br.add_cookie(cur_cookie)

        temp_data_before = self.last_html

        self.br.refresh()
        temp_data_after = self.br.page_source
        self.process_response(temp_data_before,temp_data_after,payloadpattern = payload)

    def execute_javascript(self,payload):
        val_payload = self.validate_javascript(payload)
        self.br.execute_script(val_payload)


    def validate_javascript(self,payload):
        return payload

    def print_forms(self):
        for link in self.links:
            self.find_all_forms(url = link)
        for key in self.forms_and_inputs.keys():
            print("++++++++++ "+key+" ++++++++++"+"\n\n")
            form_index = 0
            for form in self.forms_and_inputs[key]:
                print("[*] FORM")
                print(form)
                print("[*] FORMFIELDS")
                for i in range(1,len(self.forms_and_inputs[key][form_index])):
                    #print "[+]"+str(self.forms_and_inputs[key][form_index][i])
                #print "\n\n"
                    form_index += 1
