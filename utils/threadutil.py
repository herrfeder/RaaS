from datetime import datetime


# decorator for naming threads and set start time
def name_time_thread(method):
    def inner(ref):
        ref.setName(type(ref).__name__ +"_"+"-".join(ref.choosen)+"_"+ ref.domain_name)

        ref.start_time = datetime.now().strftime("%H:%M:%S")

        return method(ref)

    return inner
