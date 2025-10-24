import requests

url = "http://localhost:8000/app/v1/payments/tbank/callback"
callback_mock_success = {
    'TerminalKey': '1752237644723',
    'RequestKey': '94630502',
    'Status': 'ACTIVE',
    'Success': True,
     'ErrorCode': '0',
     'Message': 'Запрос обработан успешно',
     'AccountToken': '4010a4729af34d4b9c6a838077eb36c6',
     'BankMemberId': '100000000004',
    'BankMemberName': 'Т-Банк',
     'Token': '30e15b1cdaa6185361d314b005e4bd8fa3b9bdb25cbce624a541f0316f028f0d',
     'NotificationType': 'LINKACCOUNT'}

response = requests.post(url, json=callback_mock_success)
