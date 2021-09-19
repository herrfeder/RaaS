#!/usr/bin/python

import os
import re


DOMAIN_FOLDER="tweakers.net/domains/"


class FileObject():

    def __init__(self,domain,filetype="nmap"):

        self.domain = domain
        self.filetype = filetype
        self.file_content = ""
        
        self.open_file()

    def open_file(self):

        path = DOMAIN_FOLDER+self.domain+"/"

        files = os.listdir(path)
        for sfile in files:
            if self.filetype in sfile:
                with open(path+sfile) as f:
                    self.file_content = f.read()
                f.close()
                return True
        return False

    def get_content(self):
        return self.file_content



class OutputParser():

    def __init__(self,used_tool="nmap"):

        self.used_tool=used_tool

        self.regex_dict = {"nmap":{"hostup":re.compile(r"Host is up"),
                               "ip":re.compile(r"\(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\)"),
                               "tcpport":re.compile(r"\d{1,5}/tcp.*open.*"),
                               "udpport":re.compile(r"\d{1,5}/udp.*open.*")}
                          }


    def process_ip(self,inputstr):
       
        ip = ""

        aa = self.regex_dict[self.used_tool]["ip"].search(inputstr)
        if aa is not None:
            aa = aa.string[aa.start():aa.end()]
            if self.used_tool=="nmap":
                if aa.startswith("("):
                    ip = aa.split("(")[1].split(")")[0]
        return ip


    def process_services(self,inputstr,prot="tcp"):
       
        #should later be refactorized to own class
        service_port_dict = {"port":0,"service":"empty","status":"closed"}
        ports = []
        aa = ""
        if prot=="tcp":
            aa = self.regex_dict[self.used_tool]["tcpport"].findall(inputstr)
        else:
            aa = self.regex_dict[self.used_tool]["udpport"].findall(inputstr)

        if aa is not None:
            if self.used_tool=="nmap":
                for entry in aa:
                    port = int(entry.split("/")[0])
                    status = entry.split()[1]
                    try:
                        service = "".join(entry.split()[2:])
                    except:
                        service = "empty"
                    new_dict =dict(service_port_dict,
                                   port=port,
                                   service=service,
                                   status=status)

                    ports.append(new_dict)
        
        return ports 

    def process_upstate(self,inputstr):

        up = False
        aa = self.regex_dict[self.used_tool]["hostup"].search(inputstr)

        if aa is not None:
            if self.used_tool=="nmap":
                up = True

        return up


class DomainObject():

    def __init__(self):
        self.domain_dict = {"dn":"www.example.com",
                            "ip":"empty",
                            "adn":"empty",  #alternative domain name
                            "up":False,
                            "pmd":True,     #point to main domain
                            "services":"empty"}
        
        self.domain_list = []
        op = OutputParser()

        self.set_all_domains()


    def set_all_domains(self):
        for _,dirs,_ in os.walk(DOMAIN_FOLDER):
            for directory in dirs:
                if directory == None:
                    pass
                else:
                    if not any(d.get("dn") == directory for d in self.domain_list):
                        new_dict = self.get_domain_stats(directory)
                        self.domain_list.append(new_dict)

    def get_domain_stats(self,domain):

        fo = FileObject(domain)
        op = OutputParser()
        if fo==False:
            return dict(self.domain_dict,dn=domain)
        else:
            filestr = fo.get_content()
            services = op.process_services(filestr)
            ip = op.process_ip(filestr)
            up = op.process_upstate(filestr)


            return dict(self.domain_dict,dn=domain,services=services,ip=ip,up=up)


    def print_domains(self,domain_list=""):
        if domain_list:
            print ''.join("%s\n"%x for x in domain_list)
        else:
            print ''.join("%s\n"%x for x in self.domain_list)

    def filter_domains(self,notip,filt):
        templist=[]
        for domain in self.domain_list:
            if domain['ip'] in notip:
                pass
            else:
                templist.append(domain["dn"]+":"+domain["ip"])

        self.print_domains(templist)
        

    def get_unique_domains(self):
        pass
    



    def get_active_domains(self):
        pass





class MainObject():

    def __init__(self,maindomain):
        self.maindomain = maindomain
        self.do = DomainObject()


    def printall(self):
        self.do.print_domains()


    def filter_output(self,notip="",filt=""):
        self.do.filter_domains(notip,filt)


if __name__ == "__main__":
    mo = MainObject("tweakers.net")
    mo.printall()

    #mo.filter_output(notip=["213.239.154.30","213.239.154.31","31.22.80.152"],filt=["dn"])

