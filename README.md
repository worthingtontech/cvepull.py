# cvepull.py
script that pulls cve collections from NVD.NIST.GOV. 

edit line 17 (timedelta) number to change the amount of days to search backwards from current date. 
edit line 24 to add different keywords for your search to the API. 
Output will have the following relevant info:   
    final_ds.append({"CVE_data_meta": cve_data_meta_id,
                     "description": description,
                     "impact": cvssV3,
                     "publishedDate": pub_date,
                     "lastModifiedDate": last_mod_date


Happy Searching
