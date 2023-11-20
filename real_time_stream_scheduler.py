import requests
import pprint


if __name__ == '__main__':
    BASE_URL = "sstech-siagraph.centralus.cloudapp.azure.com"
    BASE_PORT = 8000

    data_status_handle = "getDeltaForRawAndGraphData"
    data_export_handle = "startCaseExport"

    API_URL = f"http://{BASE_URL}:{BASE_PORT}/{data_status_handle}"

    r = requests.post(API_URL)
    resp = r.json()
    print(f"API Response code: {r.status_code}", type(r.status_code))
    print(f"Response of update of ProcessedTime: {r.json()}")
    status = resp["status"]
    if status == "no":
        print("Data is up to date")
    else:
        query = resp["query"]
        pprint.pprint(query)
        print("delta found, going to start export of data")
        r = requests.post(f'http://{BASE_URL}:{BASE_PORT}/{data_export_handle}', json=query)
        if r.status_code == 200:
            print("Data has successfully started the export. The caseId generated is")
            print(r.json())
