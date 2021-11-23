# CVE Automation Tool
# STAGE: Peer Review | 1st Draft
import requests
from datetime import datetime, timedelta
import json

# TODO: query = ?
# TODO: Return data format to JSON
# 1. "startIndex"
# 2. "addOns"
# 3. "pubEndDate"
# 4. "pubStartDate"
# 5. "cvssV3Severity"
# 6. "resultsPerPage"

# answer = input("What is it that you want? ")

keys = 'android' 
# only one keyword seems to work with the NVD API. 
# So leave empty if you want all results(). 
# Or, skip to bottom 'for' loop and edit 'keywords' for accurate results

now = datetime.utcnow()
by_week = now - timedelta(days=45) #change number of days to expand/shrink API request results
this_filter_date = by_week # yyyy-MM-dd'T'HH:mm:ss:SSS UTC-05:00
iso_last_week = f'{this_filter_date.strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
iso_now = f'{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'

test_result = {'resultsPerPage': '2000',
               'keyword': keys,
               'pubStartDate': iso_last_week,
               'pubEndDate': iso_now,
               'startIndex': '0'}

response = requests.get(url='https://services.nvd.nist.gov/rest/json/cves/1.0', params=test_result)

nvd_data = response.json()

with open('initial_nvd.json', 'w+') as sourceFile:
    sourceFile.write(json.dumps(nvd_data, indent=2))
    
ds = json.loads(response.text)
# print(ds["result"])

final_ds = []

for a_key in ds["result"]["CVE_Items"]:
    cve_data_meta_id = a_key["cve"]["CVE_data_meta"]["ID"]
    cvssV3 = ''
    pub_date = ''
    last_mod_date = ''
    description = ''
    try:
        cvssV3 = a_key["impact"]["baseMetricV3"]["cvssV3"]
    except KeyError:
        pass
    try:
        pub_date = a_key["publishedDate"]
    except KeyError:
        pass
    try:
        last_mod_date = a_key["lastModifiedDate"]
    except KeyError:
        pass

    for desc in a_key["cve"]["description"]["description_data"]:
        description = desc["value"]
    # Append to the final_ds results
    final_ds.append({"CVE_data_meta": cve_data_meta_id,
                     "description": description,
                     "impact": cvssV3,
                     "publishedDate": pub_date,
                     "lastModifiedDate": last_mod_date
                     })

print(json.dumps(final_ds, indent=2))

with open('my_results.json', 'w+') as outFile:
    outFile.write(json.dumps(final_ds, indent=2))

# Now begin reading the my_results.json, looking for keywords and printing the values 
print('\n''\n''\n' 'EXAMINING PERTINENT THREATS FROM NVD.NIST.GOV''\n''\n''\n''THIS MAY TAKE A SECOND...''\n''\n'
'\n''Please check Final CVEs.json for results''\n''\n')

keywords = 'escalation of privilege', 'denial of service', 'android'
myresults = open("my_results.json", "r")
scope = json.load(myresults)
output_json=[]
for k in keywords:
    items = [x for x in scope if k in x['description']]
    for item in items: 
        output_json.append(item)

with open("Final CVEs.json", "w+") as outFile2:
    outFile2.write(json.dumps(output_json, indent=2, sort_keys=True))
