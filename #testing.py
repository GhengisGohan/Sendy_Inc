import urllib
import requests
from bs4 import BeautifulSoup as bs   
import re   

def grab_sites():
    # format of url to pull individual site data xml: https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites=01646500&parameterCd=00060,00065&siteStatus=all;
    url = 'https://waterdata.usgs.gov/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&group_key=NONE&format=scroll_list&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'
    r = requests.get(url)
    con = r.content
    soup = bs(con, features="lxml")
    site_nos = re.findall('\d{8}', str(soup))
    return site_nos

        
def site(site_nos):        
    url_nose = "https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites="
    site_no = str(site_nos[0])
    print(site_no)
    url_tail = "&parameterCd=00060,00065&siteStatus=all"
    url = url_nose + site_no + url_tail
    site = requests.get(url)
    site_con = bs(site.content, features='lxml')

    site_name = site_con.find("gml:name").text
    loc = site_con.find("gml:pos").text
    gauge_ht = site_con.find_all("wml2:value")[0].text
    cfs = site_con.find_all("wml2:value")[1].text     
    print( site_name, loc, gauge_ht, cfs)

def main():
    site_nums = grab_sites()
    site(site_nums)

main()