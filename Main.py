import ThreadManager
from IPython.core.debugger import Tracer
from exceptions import DomainNoIp

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

    sd = ThreadManager.threadManager.newMergeResults(env, load=True)
    ip_series = sd.getIPList()
    domain_list = sd.getDomainList()

    ip_list = []

    env["dftype"] = "portscan"

    #ps = ThreadManager.threadManager.newPortScanner(env)
    #for ip in ip_series[0]:
    #    ps.run(ip)
    pt = ThreadManager.threadManager.newMergeResults(env,load=True)
    pt.validatePortscan()
    #env["dftype"] = "portscan"

    #ps = ThreadManager.threadManager.newPortScanner(env)
    #for ip in ip_series[0]:
    #    ps.run(ip)
    #mt = ThreadManager.threadManager.newMergeResults(env,
    #                                                 columns=['ip','hoststatus','tcp','udp'],
    #                                                 result_list=ps.result_list)
    #mt.run()
    #mt.do.saveToCSV()

    #mt = ThreadManager.threadManager.newMergeResults(env, load=True)
    #debug_here()

    env["dftype"] = "dirtraversal"
    dt = ThreadManager.threadManager.newDirectoryTraversal(env)
    for domain in domain_list:

        ip = sd.DomainToIP(domain)
        if ip:
            host_ser = pt.returnData(ip)
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
