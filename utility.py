import socket
import random
import re
from exceptions import WrongDomainSyntax, DomainNoIp
import os
import datetime
from IPython.core.debugger import Tracer; debughere = Tracer()

def urljoin(*args):
        return "/".join(map(lambda x: str(x).rstrip('/'), args))

###### Filesystem
def url_to_filename(name):
    return name.replace("//","").\
                replace("/","_").\
                replace(":","_").\
                replace("?","_").\
                replace("&","_")

def checkfile(filename):
    return url_to_filename(filename)

def checkdir(dirname):
    if len(dirname) > 140:
        dirname = dirname[:140]
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return dirname
###### IP and DOMAIN
ssl_ports = ["443","8443","8080"]


def get_ip_from_domain(domain):
    ip = ''

    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = ''

    return ip


def eval_target(target):
    print(target)
    result = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}",target)
    if len(result) == 1:
        return ("range",result[0])

    result = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}",target)
    if len(result) == 1:
        return ("range", target)
 
    result = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",target)
    if len(result) == 1:
        return ("ip", result[0])

    ip = getIPfromDomain(target)
    if ip:
        return("ip", ip)
    else:
        return "invalid"


def join_url(base_url,uri="",urleval=False):

    if (base_url.replace("http://","").replace("https://","") in uri ):
        return eval_url(uri)[0]

    if urleval==False:
        return urljoin(base_url,uri)
    else:
        return eval_url(urljoin(base_url,uri))[0]


def return_url(dic):
    return dic['final_url']

def eval_url(domain, port="", check_online=False):
    result_dict = {'final_url':'',
                   'port':'',
                   'ssl':'http',
                   'uri': '',
                   'base_url':'',
                   'ip': ''}

    dom_split = domain.split(":")

    if len(dom_split) == 3:
        if dom_split[0] == "https":
            result_dict['ssl'] = dom_split[0]
        elif dom_split[0] == "http":
            result_dict['ssl'] = "http"
        else:
            raise WrongDomainSyntax
        if dom_split[1].startswith("//"):
            result_dict['base_url'] = dom_split[1].lstrip("//")
        else:
            raise WrongDomainSyntax
        port_uri = dom_split[2].split("/")
        if re.match("[0-9]{1,5}",port_uri[0]):
            result_dict["port"] = port_uri[0]
            if len(port_uri) > 1:
                result_dict["uri"] = "/".join(port_uri[1:])
        else:
            raise WrongDomainSyntax

    elif len(dom_split) == 2:
        # Pattern: test.de:80/blah
        port_uri = dom_split[1].split("/")
        if re.match("[0-9]{1,5}",port_uri[0]):
            result_dict["port"] = port_uri[0]
            if result_dict["port"] in ssl_ports:
                result_dict["ssl"] = "https"
            else:
                result_dict["ssl"] = "http"
            if len(port_uri) > 1:
                result_dict["uri"] = port_uri[1]
            result_dict["base_url"] = dom_split[0]
        # Pattern: http://test.de
        elif dom_split[0].startswith("http"):
            if dom_split[0] == "https":
                result_dict['ssl'] = "https"
                result_dict['port'] = "443"
            else:
                result_dict['ssl'] = "http"
                result_dict['port'] = "80"
            # Pattern: http://test.de/blah
            if dom_split[1].startswith("//"):
                result_dict['base_url'] = dom_split[1].lstrip("//").split("/")[0]
                result_dict['uri'] = "/".join(dom_split[1].lstrip("//").split("/")[1:])
            else:
                raise WrongDomainSyntax
        else:
            raise WrongDomainSyntax

    elif len(dom_split) == 1:
        if "." in dom_split[0]:
            result_dict['base_url'] = dom_split[0]
            result_dict['port'] = "80"
        else:
            raise WrongDomainSyntax

   
    result_dict['final_url'] = result_dict['ssl']+"://"+result_dict['base_url']+":"+result_dict['port']+"/"+result_dict['uri'].lstrip("/")
    
    if check_online==True:
        result_dict['ip'] = get_ip_from_domain(return_url(result_dict))

    return return_url(result_dict),result_dict


def change_useragent():

    useragents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15	",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36	",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0	Firefox 68.0 ",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0	Firefox 68.0 ",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0	Firefox 68.0 ",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",]

    return random.choice(useragents)

def create_timestamp():

    return datetime.datetime.strftime("%Y%m%d%H%M")

def return_newest_string(string_list):

    sorted_list = sorted(string_list, key=lambda x: datetime.datetime.strptime(x.split("_")[-1], "%Y%m%d%H%M"))
    return sorted_list[-1]


