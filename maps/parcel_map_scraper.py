# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 01:10:45 2017

@author: raleigh-littles
"""

import requests, csv


def get_map_info():
    """ Parses the Parcel_Map_Index to get a list of urls for the maps."""
    file_name = 'Parcel_Map_Index.csv'

    # A list of tuples.
    # Tuple entry is: {Map URL, APN (if available), Surveyed Date}
    map_tuple_list = []

    #headers = ['FiledAs', 'ProjType', 'ProjectNo', 'ProjCode', 'Jurisdict', 'Book', 'BookOf', 'BookAbbrev', 'Page', 'Sheets', 'DateFiled', 'Status', 'RecorderNo', 'Title', 'SurveyDate', 'SurveyMo', 'SurveyYear', 'Descript', 'Owner', 'RequestOf', 'Company', 'Surveyor', 'LicType', 'LicenseNo', 'APN', 'APN2', 'CorrBy', 'CorrByDt', 'CorrBy2', 'CorrByDt2', 'Corrects', 'Reference', 'Reference2', 'SubType', 'ID', 'PDF', 'Hyperlink', 'PopUp', 'GISFTN', 'ScanPPI', 'SHPfiled', 'SHPdate', 'Loader', 'SerialNo']

    with open(file_name, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            datetime_obj = datetime.strptime(row['SurveyDate'])
            map_tuple_list.append(tuple(row['Hyperlink']


    map_urls.pop(0) # the first entry contains headers info, so remove it
    return(map_urls)
            
            
        
def get_map(urls_array):
    """ Takes a url for a map and saves the contents of that URL (the map PDF) locally"""
    for url in urls_array:
        print("Checking if a map exists at url:", url)
    
        response = requests.get(url)
        
        file_dir =  "Maps/" + url.split('/')[-2] + "-" + url.split('/')[-1] + ".pdf"
        
        print("Saving to file: ", file_dir)
        
        if "We were unable to service your request" not in response.text:
            with open(file_dir, 'wb') as my_file:
                my_file.write(response.content)
        
    
                
map_url_array = get_map_info()
get_map(map_url_array)