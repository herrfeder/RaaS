import ThreadManager
from IPython.core.debugger import Tracer
from exceptions import NoScanAvailable
debughere=Tracer()

env = {"dftype":"","project":"eurid.eu"}

if __name__ == '__main__':

    #wt = ThreadManager.threadManager.newSubdomainCollector(env["project"],env="")
    #wt.run()
    #getFin = 0
    #while getFin == 0 :
    #    getFin = wt.getFin()
    #getFin == 0
    #
    env["dftype"] = "subdomain"
    #mt = ThreadManager.threadManager.newMergeResults(env,
    #                                                columns=['domain', 'ip4_1', 'ip4_2', 'ip6_1', 'ip6_2'],
    #                                                result_list=wt.getResultList())
    #mt.run()
    #mt.do.saveToCSV()

    mt = ThreadManager.threadManager.newMergeResults(env, load=True)
    ip_series = mt.get_ip_list()
    domain_list = mt.get_domain_list()
    ip_list = []
    for domain in domain_list:
        ip = mt.domain_to_ip(domain)
        if ip:
            ip_list.append(ip)
    env["dftype"] = "portscan"
    #ps = ThreadManager.threadManager.newPortScanner(env)
    #for ip in ip_series[0]:
    #    ps.run(ip)
    mt = ThreadManager.threadManager.newMergeResults(env,load=True)
    debughere()
    mt.validate_portscan()
    print(mt.do.df)
    '''
    for ip in ip_list:
        print("list:"+ip)
        try:
            print(mt.returnPortscan(ip))
        except NoScanAvailable:
            pass
    '''
