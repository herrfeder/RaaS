import ThreadManager
from IPython.core.debugger import Tracer
from exceptions import DomainNoIp
from subdomainlist import subdomains

debughere=Tracer()

env = {"dftype":"","project":"shop-apotheke.com"}




if __name__ == '__main__':

    env["dftype"] = "subdomain"
    
    '''
    wt = ThreadManager.threadManager.newSubdomainCollector(env["project"],env="")
    wt.start()
    getFin = 0
    while getFin == 0 :
        getFin = wt.getFin()
    getFin == 0
    debughere()
    '''

    mt = ThreadManager.threadManager.newMergeResults(env,
                                                    columns=['domain', 'ip4_1', 'ip4_2', 'ip6_1', 'ip6_2'],
                                                    result_list=subdomains)
    mt.run()
    mt.do.save_to_sqlite()

    ip_series = mt.get_ip_list()
    domain_list = mt.get_domain_list()

    env["dftype"] = "portscan"

    ps = ThreadManager.threadManager.newPortScanner(env)
    pt = ThreadManager.threadManager.newMergeResults(env)
    for domain in domain_list:
        if env["project"] in domain:
            print(domain)
            print(mt.domain_to_ip(domain))
            result_list = ps.run(mt.domain_to_ip(domain))
            pt.merge_portscan(result_list, mt.domain_to_ip(domain))
        else:
            print("isn't in scope")
    debughere()
    pt.validate_portscan()
    pt.do.save_to_sqlite()

    '''
    env["dftype"] = "dirtraversal"
    dt = ThreadManager.threadManager.newDirectoryTraversal(env)
    for domain in domain_list:

        ip = sd.domain_to_ip(domain)
        if ip:
            host_ser = pt.return_data(ip)
            if (host_ser['host'].item() == 'up') and (not host_ser['web'].empty):
                for port in host_ser['web'].item().split(":"):
                    try:
                        dt.run(domain, port)
                    except Exception as e:
                        print(e)
                        mt = ThreadManager.threadManager.newMergeResults(env,
                                                         columns="",
                                                         result_list=dt.result_list)
                        mt.run()
                        mt.do.saveToCSV()


    mt = ThreadManager.threadManager.newMergeResults(env,
                                                     columns="",
                                                     result_list=dt.result_list)
    mt.run()
    mt.do.saveToCSV()
    '''
