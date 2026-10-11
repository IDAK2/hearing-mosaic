import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result['method'] = method
    if args:
        result['args'] = args
    if kwargs:
        result['kwargs'] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / 'accounts.env').read_text()
DEPLOYMENT = json.loads((ROOT / 'deployment.json').read_text())
ADDRESS = DEPLOYMENT['contractAddress']
COMMIT = DEPLOYMENT['sourceCommit']


def account(number):
    key = re.search(rf'^ACCOUNT_{number}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
    return create_account(account_private_key=key)


def client(number):
    return create_client(chain=studionet, account=account(number))


def write(number, name, args):
    active = client(number)
    tx = active.write_contract(address=ADDRESS, function_name=name, args=args)
    print(name + '_tx=' + str(tx), flush=True)
    receipt = active.wait_for_transaction_receipt(transaction_hash=tx, wait_until='finalized', retries=180, interval=5000, full_transaction=True)
    leaders = receipt.get('consensus_data', {}).get('leader_receipt') or []
    leaders = [leaders] if isinstance(leaders, dict) else leaders
    assert receipt.get('result_name') == 'MAJORITY_AGREE'
    assert any(item.get('execution_result') == 'SUCCESS' for item in leaders)
    return str(tx)

hearing_id = 'HEAR-' + str(int(time.time()))
role_numbers = (1, 3, 4)
participants = [str(account(number).address) for number in role_numbers]
transactions = {}
transactions['open'] = write(7, 'open_hearing', [
    hearing_id, 'Neighborhood access hearing',
    ['Tuesday 09:00', 'Tuesday 11:00', 'Wednesday 15:00'], participants, 3600,
])
statements = [
    'I can attend Tuesday at 09:00 or Tuesday at 11:00, with no accommodation needed.',
    'I am available only Tuesday at 11:00 and need remote participation.',
    'Wednesday at 15:00 is my available time and I need support access.',
]
for number, statement in zip(role_numbers, statements):
    transactions['availability' + str(number)] = write(number, 'submit_availability', [hearing_id, statement])
transactions['seat'] = write(7, 'seat', [hearing_id])
state = client(7).read_contract(address=ADDRESS, function_name='get_hearing', args=[hearing_id])
assert state['state'] == 'FULL'
assert state['assignment'] == [[0, 0], [1, 1], [2, 2]]
proof = {'hearingId': hearing_id, 'transactions': transactions, 'state': state,
         'disclosure': 'The participant wallets are operator-controlled role fixtures, not independent people.'}
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence' / 'live-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof, indent=2), flush=True)

