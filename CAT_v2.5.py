import requests
from datetime import datetime, timedelta
import json
from pprint import pprint
# #==========================================================================================
# # user input section
# #==========================================================================================
day = 120 #number in days
apikey = ['Android']
keywords = ['escalation of privilege', 'remote code execution', 'arbitrary code execution', 'denial of service', 'kernel']
# #==========================================================================================
# # setting time variables in UTC -5hrs and -3ms digits
# #==========================================================================================
now = datetime.utcnow()
by_week = now - timedelta(days=day) 
this_filter_date = by_week
iso_last_week = f'{this_filter_date.strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
iso_now = f'{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S:%f")[:-3]} UTC-05:00'
test_result = {'resultsPerPage': '2000',
               'keyword': apikey,
               'cweId': '',
               'modStartDate': iso_last_week,
               'modEndDate': iso_now,
               'pubStartDate': iso_last_week,
               'pubEndDate': iso_now,
               'startIndex': '0'}
# #==========================================================================================
# # retrieve CVEs
# #==========================================================================================
print("\n""Searching database...")
response = requests.get(url='https://services.nvd.nist.gov/rest/json/cves/1.0', params=test_result)

nvd_data = response.json()

with open('1-initial_nvd.json', 'w+') as sourceFile:
    sourceFile.write(json.dumps(nvd_data, indent=2))

rawData = json.loads(response.text)

# #==========================================================================================
# # cherry-pick relevant keys
# #==========================================================================================
print("\n""Searched for", apikeys, keywords"\n")
cleanData = []
items = rawData['result']['CVE_Items']

for item in items:
    cve_data_meta_id = item["cve"]["CVE_data_meta"]["ID"]
    baseScore = ''
    vectorString = ''
    pub_date = ''
    last_mod_date = ''
    description = ''
    cweId = ''
    references = ''
    cweValue = ''
    try:
        baseScore = item["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
    except KeyError:
        pass
    try:
        vectorString = item["impact"]["baseMetricV3"]["cvssV3"]["vectorString"]
    except KeyError:    
        pass
    try:
        pub_date = item["publishedDate"]
    except KeyError:
        pass
    try:
        last_mod_date = item["lastModifiedDate"]
    except KeyError:
        pass
    try:
        cweID = item["problemtype"]["problemtype_data"]["description"]
    except KeyError:
        pass
    #pull description
    for desc in item["cve"]["description"]["description_data"]:
        description = desc["value"]
    #pull related CWE values
    for id in item["cve"]["problemtype"]["problemtype_data"]:
        cweId = id["description"]
        for i in id["description"]:
            cweValue = i['value']
    #pull references
    for ref in item["cve"]["references"]["reference_data"]:
        references = ref["url"]
    cleanData.append({"CVE_data_meta": cve_data_meta_id,
                     "description": description,
                     "baseScore": baseScore,
                     "vectorSring": vectorString,
                     "cweID": cweValue, 
                     "cweID URL": "https://cwe.mitre.org/data/definitions/"+str(cweValue)+".html",
                     "references": references,
                     "publishedDate": pub_date,
                     "lastModifiedDate": last_mod_date
                     })


with open('2-cleanData.json', 'w+') as outFile:
    outFile.write(json.dumps(cleanData, indent=2))

# # ==========================================================================================
# # narrow response with additional 'keywords'
# # ==========================================================================================
myResults = open("2-cleanData.json", "r")
scope = json.load(myResults)
output_json=[]
results = []
for k in keywords:
    counter = 0
    items = [x for x in scope if k in x['description']]
    for item in items: 
        output_json.append(item)
        counter += 1
    results.append(counter)
deduped = []    
seen = set()
for object in output_json:
    cvekey = object['CVE_data_meta']
    if cvekey not in seen:
        deduped.append(object)
        seen.add(cvekey)
with open("3-Final CVEs.json", "w+") as outFile2:
    outFile2.write(json.dumps(deduped, indent=2,))

# # ==========================================================================================
# # results logging per type
# # ==========================================================================================
resultObj = dict(zip(keywords, results))
total = len(output_json)

print("\n""{} Total Found:".format(total))

for r in resultObj:
    print("{} {} vulnerabilities".format(resultObj[r], r))