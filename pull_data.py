"""
Recursive script that pulls data for all water gauges in the USA from usgs water services.
More info at https://waterdata.usgs.gov

Input: none
Return: geojson with all site numbers, names, and instantaneous water gauge flow value (height and cfs).
"""

from cmath import nan
import pandas as pd
import requests
import urllib
import numpy as np
import os
from bs4 import BeautifulSoup as bs
import re

class ILT:
    def grab_site_numbers():
        
        # Uses requests to grab table data values from USGS list of site numbers
        # request.reponse.content will contain all gauge site numbers
        # format: https://waterdata.usgs.gov/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&group_key=NONE&format=scroll_list&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection
        # table: <select id="site_no" multiple="multiple" size="10" name="site_no" tabindex="1">
        # output: series of site nombers
        print('grabbing site numbers')
        url = 'https://waterdata.usgs.gov/nwis/current?index_pmcode_STATION_NM=1&index_pmcode_DATETIME=2&group_key=NONE&format=scroll_list&sitefile_output_format=html_table&column_name=agency_cd&column_name=site_no&column_name=station_nm&sort_key_2=site_no&html_table_group_key=NONE&rdb_compression=file&list_of_search_criteria=realtime_parameter_selection'
        url_contents = requests.get(url).content
        soup = bs(url_contents, features="lxml")
        site_nos = re.findall('\d{8}', str(soup))
        return pd.Series(site_nos), site_nos
    
    def save_sites_list(input_list):
        site_nos = input_list
        with open(r"/home/ghengis_gohan/pyproj/Sendy_Inc/sites.txt", 'w') as sites:
            for item in site_nos:
                sites.write("%s\n" % item)
            print("Done")

    def parse_site_xml(site_num):

        # pull xml data from waterservice and create list
        # Input: site number
        # format of url to pull individual site data xml: https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites=01646500&parameterCd=00060,00065&siteStatus=all;
        # Output: list of site details
        site_name, loc, gauge_ht, cfs = np.nan, np.nan, np.nan, np.nan
        url_nose = "https://waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites="
        site_no = str(site_num)
        url_tail = "&parameterCd=00060,00065&siteStatus=all"
        url = url_nose + site_no + url_tail
        r = requests.get(url)
        soup_content = bs(r.content, features = "lxml")
        print(soup_content)
        print("\n")
        try:
            site_name, loc, gauge_ht, cfs = soup_content.find("gml:title").text, soup_content.find(r"gml:pos srsname='urn:ogc:def:crs:EPSG:4326'").text, soup_content.find_all("wml2:value")[0].text, soup_content.find_all("wml2:value")[1].text 
        except AttributeError:
            pass
        except IndexError:
            pass

        site_dict = {
                "type":"Feature", 
                "geometry": {
                "type": "Point", 
                "coordinates": loc #[str(loc).split(' ')[0], str(loc).split(' ')[1]]
                },
                "properties": {
                    "name": site_name,
                    "gauge height (ft)": gauge_ht,
                    "water flow (cfs)": cfs
                }
            }
        print(site_dict)

def main():
    site_nums, site_nos = ILT.grab_site_numbers()
    ILT.save_sites_list(site_nos)
    print('parsing xml data')
    print('aggregating site data')
    site_details = site_nums.apply(ILT.parse_site_xml)
    print('GeoJson build complete')
    print(len(site_details))
    print(site_details[:10])

if __name__ == "__main__":
    main()