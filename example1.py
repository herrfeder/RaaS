from Spider import SelObject 
from IPython.core.debugger import Tracer; debughere = Tracer()

url = "https://eurid.eu"
url = "https://www.hsu-hh.de/"

selob = SelObject("eurid.eu")
#selob.find_all_forms(url)
selob.collect_all_links(url)
#if (selob.check_login()):
#    selob.do_login("admin","password")
#selob.collect_all_links(url)
print(selob.links)

debughere()
#for link in selob.links:
#    selob.find_all_forms(link)
#selob.print_forms()
#selob.modify_cookie("<script>document.getElementByTagName('body').innerHTML = ''</script>")

