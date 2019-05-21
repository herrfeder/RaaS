import socket
import re
from exceptions import WrongDomainSyntax, DomainNoIp, WrongProjectEnvironment
import sys
import os

allowed_dftypes = ["subdomain", "portscan", "dirtraversal"]

def get_env(dftype, project=""):
    env_skeleton = {"dftype":"", "project":""}
    if project:
        env_skeleton["project"] = project
    elif os.getenv("PROJECT"):
        env_skeleton["project"] = os.getenv("PROJECT")

    return env_skeleton


def getIPfromDomain(domain):
    ip = ''

    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = ''

    return ip


def evalTarget(target):
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


def return_url(dic):

    dom_split = dic['domain'].split("/")

    return dic['ssl']+"://"+dom_split[0]+":"+dic['port']+"/"+"/".join(dom_split[1:])

def eval_url(domain, port=""):

    result_dict = {'domain':'','port':'','ssl':'http'}
    dom_split = domain.split(":")

    if len(dom_split) == 3:
        if dom_split[0] == "https":
            result_dict['ssl'] = dom_split[0]
        elif dom_split[0] == "http":
            pass
        else:
            raise WrongDomainSyntax
            return -1
        result_dict['port'] = dom_split[2].split("/")[0]
        try:
            result_dict['domain'] = dom_split[1].split("//")[1]+\
                                    "/"+"/".join(dom_split[2].split("/")[1:])
        except:
            raise WrongDomainSyntax
            return -1

    elif len(dom_split) == 2:
        if dom_split[0] == "https":
            result_dict['ssl'] = dom_split[0]
            result_dict['port'] = "443"
        elif dom_split[0] == "http":
            result_dict['port'] = "80"
        else:
            raise WrongDomainSyntax
            return -1
        try:
            result_dict['domain'] = dom_split[1].split("//")[1]
        except:
            raise WrongDomainSyntax
            return -1

    elif len(dom_split) == 1:
        if "." in dom_split[0]:
            result_dict['domain'] = dom_split[0]
            result_dict['port'] = "80"
        else:
            raise WrongDomainSyntax
            return -1

    else:
        raise WrongDomainSyntax
        return -1

    if not getIPfromDomain(result_dict['domain'].split("/")[0]):
            raise DomainNoIp
            return -1

    if port:
        result_dict['port'] = port
        if port in ["443","8443","4443"]:
            result_dict['ssl'] = "https"
    return return_url(result_dict),result_dict
