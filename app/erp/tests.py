from django.test import TestCase
import requests
import json

url_session = "https://CFR-I7-1:50000/b1s/v1/Login"

payload_session = json.dumps({
  "CompanyDB": "BDPRUEBASOCL",
  "Password": "m1r1",
  "UserName": "manager"
})
headers_session = {
  'Content-Type': 'application/json',
  'Cookie': 'B1SESSION=d266d95e-4e81-11ef-8000-b42e99e90cf9; ROUTEID=.node3'
}

response_session = requests.request("POST", url_session, headers=headers_session, data=payload_session, verify=False)


if response_session.status_code == 200:
    # Parsear la respuesta JSON
    response_json = response_session.json()
    
    # Acceder a los valores del JSON
    company_db = response_json.get('SessionId')

    
    print(f"CompanyDB: {company_db}")
else:
    print(f"Error en la solicitud: {response_session.status_code}")

url = "https://CFR-I7-1:50000/b1s/v1/PurchaseRequests"

payload = json.dumps({
    [
  {
    "Requester": "SAP-004",
    "ReqType": 2,
    "DocType": "dDocument_Items",
    "DocDate": "2024-07-24",
    "DocCurrency": "SOL",
    "Comments": "",
    "TaxDate": "2024-07-24",
    "Series": 75,
    "DocumentLines": [
      {
        "ItemCode": "P-0001",
        "LineVendor": "001",
        "Quantity": 2,
        "CostingCode": "Proveedor",
        "Currency": "SOL"
      },
      {
        "ItemCode": "P-0002",
        "LineVendor": "002",
        "Quantity": 5,
        "CostingCode": "Proveedor",
        "Currency": "SOL"
      }
    ]
  }
]
})
cookie = 'B1SESSION=' + company_db +'; ROUTEID=.node3'
headers = {
  'Content-Type': 'application/json',
  'Cookie': cookie
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text)

# Create your tests here.
