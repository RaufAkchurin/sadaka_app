import requests

url = "http://localhost:8000/app/v1/payments/tinkoff/callback"
callback_mock_success = {
    "Amount": 1000,
    "CardId": 610280382,
    "Data": {
        "Device": "Desktop",
        "DeviceBrowser": "Safari",
        "DeviceIframe": "false",
        "DeviceOs": "Mac OS",
        "DeviceWebView": "false",
        "Project_id": "1",
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
        "paymentUrl": "https://pay.tbank.ru/sk4Fst80",
    },
    "ErrorCode": "0",
    "ExpDate": "1230",
    "OrderId": "51",
    "Pan": "430000******0777",
    "PaymentId": 7152275652,
    "Status": "AUTHORIZED",
    "Success": True,
    "TerminalKey": "1752237644677DEMO",
    "Token": "30db333980487c2d73167d6a68b706697d80b82b73ac31c23cba0611f45e1411",
}

response = requests.post(url, json={"object": callback_mock_success})
