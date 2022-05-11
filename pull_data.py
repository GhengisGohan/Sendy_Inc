"""
Recursive script that pulls data for all water gauges in the USA from usgs water services.
More info at https://waterdata.usgs.gov
Input: none
Return: geojson with all site numbers, names, and instantaneous water gauge flow value (height and cfs).
"""

import pandas as pd
import requests
import urllib
import numpy as np
import os
from bs4 import BeautifulSoup as bs
import re

class ELT:
    def grab_site_numbers():
        
        # Uses requests to grab table data values from USGS list of site numbers
        # request.reponse.content will contain all gauge site numbers
        # format: https://waterdata.usgs.gov/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&group_key=NONE&format=scroll_list&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection
        # table: <select id="site_no" multiple="multiple" size="10" name="site_no" tabindex="1">
        # output: series of site nombers
        print('grabbing site numbers')
        url = 'https://waterdata.usgs.gov/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&group_key=NONE&format=scroll_list&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'
        url_contents = urllib.request.urlopen(url).read()
        soup = bs(url_contents, "html", features= "lxml")
        optiontags = str(soup.find_all('option'))
        site_nos = re.findall('\d{8}', optiontags)
        return pd.Series(site_nos)

    def parse_site_xml(site_num):

        # pull xml data from waterservice and create list
        # Input: site number
        # format of url to pull individual site data xml: https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites=01646500&parameterCd=00060,00065&siteStatus=all;
        # Output: list of site details
        url_nose = "https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites="
        site_no = str(site_num)
        url_tail = "&parameterCd=00060,00065&siteStatus=all"
        url = url_nose + site_no + url_tail
        r = requests.get(url)
        soup_content = bs(r.content, "lxml")
        try:
            site_name, loc = soup_content.find("gml:name").text, soup_content.find("gml:pos").text
            gauge_ht, cfs = soup_content.find_all("wml2:value")[0].text, soup_content.find_all("wml2:value")[1].text        

            return {
                    "type":"Feature", 
                    "geometry": {
                    "type": "Point", 
                    "coordinates": [loc.split(' ')[0], loc.split(' ')[1]]
                    },
                    "properties": {
                        "name": site_name,
                        "gauge height (ft)": gauge_ht,
                        "water flow (cfs)": cfs
                    }
                }
        except AttributeError:
            pass

def main():
    site_nums = ELT.grab_site_numbers()
    site_details = {}
    print('parsing xml data')
    print('aggregating site data')
    for site_number in site_nums:
        site_GeoJson = ELT.parse_site_xml(site_number)
        site_details[site_number] = site_GeoJson
    with open("inst_site_data.json", "w") as json_file:
        json_file.write(site_details)
        json_file.close()
    print('GeoJson build complete')

if __name__ == "__main__":
    main()
