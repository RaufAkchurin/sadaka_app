import http.client
import json
import uuid

from app.settings import settings
from app.v1.payment_tinkoff.use_cases.create import TBankClient

client = TBankClient()

conn = http.client.HTTPSConnection("securepay.tinkoff.ru")
payload = {
    "TerminalKey": settings.TERMINAL_KEY,
    "PaymentId": 10063,
    "DataType": "PAYLOAD",
    "BankId": uuid.uuid4(),
    "Token": "871199b37f207f0c4f721a37cdcc71dfcea880b4a4b85e3cf852c5dc1e99a8d6",
}

payload_with_token = payload["Token"] = client

payload = json.dumps()
headers = {"Content-Type": "application/json", "Accept": "application/json"}
conn.request("POST", "/v2/GetQr", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
