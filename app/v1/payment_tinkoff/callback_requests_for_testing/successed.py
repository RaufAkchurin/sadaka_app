import requests

url = "http://localhost:8000/app/v1/payments/tbank/callback"
callback_mock_success = {
    "Amount": 1000,
    "CardId": 610280382,
    "Data": {
        "Device": "Desktop",
        "DeviceBrowser": "Safari",
        "DeviceIframe": "false",
        "DeviceOs": "Mac OS",
        "DeviceWebView": "false",
        "REDIRECT": "false",
        "SEND_EMAIL": "N",
        "SaveCard": "false",
        "Source": "cards",
        "VeAuthRc": "00",
        "accept": "application/json",
        "connection_type": "PF",
        "connection_type_pf": "true",
        "isMIDSyncEnabled": "true",
        "order_id_unique_processed": "ignored",
        "payAction": "3DS",
        "paymentUrl": "https://pay.tbank.ru/EdLymlTe",
        "project_id": "1",
        "user_id": "1",
    },
    "ErrorCode": "0",
    "ExpDate": "1230",
    "OrderId": "63",
    "Pan": "430000******0777",
    "PaymentId": 7160853973,
    "Status": "CONFIRMED",
    "Success": True,
    "TerminalKey": "1752237644677DEMO",
    "Token": "2794408b52ecc7d5b241935353269db2f511cc146418e9d3a63cf450f19e7235",
}

response = requests.post(url, json=callback_mock_success)
