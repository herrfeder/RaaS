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
    mt.init_hosts("subdomain")
    mt.do.save_to_sqlite()

    ip_series = mt.get_ip_list()
    domain_list = mt.get_domain_list()

    env["dftype"] = "portscan"

    ps = ThreadManager.threadManager.newPortScanner(env)
    pt = ThreadManager.threadManager.newMergeResults(env, do=mt.do, load=True)
    '''
    for domain in domain_list[:5]:
        if env["project"] in domain:
            print(domain)
            print(mt.domain_to_ip(domain))
            result_list = ps.run(mt.domain_to_ip(domain))
            pt.merge_portscan(result_list, mt.domain_to_ip(domain))
        else:
            print("isn't in scope")
    '''
    pt.validate_portscan()

    env["dftype"] = "dirtraversal"
    dt = ThreadManager.threadManager.newDirectoryTraversal(env)
    dm = ThreadManager.threadManager.newMergeResults(env, do=pt.do, load=True)
    '''
    for domain in domain_list:
        if env["project"] in domain:
            if (dm.get_host_state(domain=domain) == 'up') and\
               ("web" in dm.get_host_purpose(domain=domain)):
                for port in dm.get_host_ports(domain=domain, porttype="web"):
                    print(port)
                    result_list = dt.run(domain, port)
                    dm.merge_dirtraversal(result_list)

    debughere()
    dm.save_to_sqlite()
    '''

    env["dftype"] = "spider"
    spider = ThreadManager.threadManager.newSpider(env)
    sm = ThreadManager.threadManager.newMergeResults(env, do=dm.do)
    for domain in domain_list:
        if env["project"] in domain:
            if (dm.get_host_state(domain=domain) == 'up') and\
               ("web" in dm.get_host_purpose(domain=domain)):
                for port in dm.get_host_ports(domain=domain, porttype="web"):
                    result_list = spider.run(domain, port)
                    sm.merge_spider(result_list)


