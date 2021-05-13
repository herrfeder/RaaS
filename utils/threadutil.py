from datetime import datetime


# decorator for naming threads and set start time
def name_thread_crawl(method):
    def inner(ref):
        ref.start_time = datetime.now().strftime("%H:%M:%S")
        ref.setName(type(ref).__name__ +"_"+"-".join(ref.tool)+"_"+ref.domain_name+"_"+ref.start_time)

        return method(ref)

    return inner


def name_thread_datalinker(method):
    def inner(ref):
        ref.start_time = datetime.now().strftime("%H:%M:%S")
        ref.setName(type(ref).__name__ +"_"+ref.datatype+"_"+ref.start_time)

        return method(ref)

    return inner

