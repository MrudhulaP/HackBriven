import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Health check
res = client.get('/health')
assert res.status_code == 200
print('1. Health check:', res.json())

# 2. Demo login
res_auth = client.post('/api/auth/demo')
assert res_auth.status_code == 200
token = res_auth.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print('2. Demo login success! Token generated.')

# 3. List customers
res_cust = client.get('/api/customers', headers=headers)
assert res_cust.status_code == 200
custs = res_cust.json()
print('3. Customers in shop:', [(c['name'], c['outstanding_balance']) for c in custs])
ramesh = next(c for c in custs if c['name'] == 'Ramesh')
assert float(ramesh['outstanding_balance']) == 0.0

# 4. Voice Interpret multi-event: 'Ramesh ka 340 udhaar, kal 200 diya tha'
res_voice = client.post('/api/voice/interpret', json={'text': 'Ramesh ka 340 udhaar, kal 200 diya tha', 'language': 'hi'}, headers=headers)
assert res_voice.status_code == 200
voice_data = res_voice.json()
print('4. Voice interpreted events:', [(e['intent'], e['customer_name'], e['amount'], e['date_label']) for e in voice_data['events']])
assert len(voice_data['events']) == 2

# 5. Confirm both transactions
confirm_payload = {
    'language': 'hi',
    'items': [
        {
            'customer_id': ramesh['id'],
            'customer_name': 'Ramesh',
            'type': 'CREDIT',
            'amount': 340.0,
            'transaction_date': voice_data['events'][0]['transaction_date']
        },
        {
            'customer_id': ramesh['id'],
            'customer_name': 'Ramesh',
            'type': 'PAYMENT',
            'amount': 200.0,
            'transaction_date': voice_data['events'][1]['transaction_date']
        }
    ]
}
res_confirm = client.post('/api/voice/confirm', json=confirm_payload, headers=headers)
assert res_confirm.status_code == 200
confirm_data = res_confirm.json()
print('5. Confirm response:', confirm_data['spoken_response'])
print('   New calculated balance:', confirm_data['new_outstanding_balance'])
assert float(confirm_data['new_outstanding_balance']) == 140.0

# 6. Verify Ramesh Ledger
ramesh_id = ramesh['id']
res_ledger = client.get(f'/api/customers/{ramesh_id}/ledger', headers=headers)
assert res_ledger.status_code == 200
ledger_data = res_ledger.json()
print('6. Ramesh verified ledger balance:', ledger_data['outstanding_balance'], 'Transactions count:', len(ledger_data['transactions']))
assert float(ledger_data['outstanding_balance']) == 140.0

# 7. Ask Financial Assistant: 'Ramesh ka kitna baaki hai?'
res_qa = client.post('/api/assistant/query', json={'query': 'Ramesh ka kitna baaki hai?', 'language': 'hi'}, headers=headers)
assert res_qa.status_code == 200
print('7. Assistant response:', res_qa.json()['answer'])
assert '140' in res_qa.json()['answer']

print('\n>>> ALL LIVE ENDPOINTS AND ACCEPTANCE CRITERIA VERIFIED 100% SUCCESSFUL! <<<')
