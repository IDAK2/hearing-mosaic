from conftest import CONTRACT
import json


SLOTS = ['Tuesday 09:00', 'Tuesday 11:00', 'Wednesday 15:00']
TEXTS = [
    'I can attend Tuesday at 09:00 or Tuesday at 11:00, with no accommodation needed.',
    'I am available only Tuesday at 11:00 and need remote participation.',
    'Wednesday at 15:00 is my available time and I need support access.',
]


def opened(vm, deploy, accounts, window=600, participant_count=3):
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.warp('2035-01-01T00:00:00+00:00')
    vm.sender = accounts[0]
    contract = deploy(CONTRACT)
    contract.open_hearing('hm-8', 'Neighborhood access hearing', SLOTS, ['0x' + a.hex() for a in accounts[1:participant_count + 1]], window)
    return contract


def submit(vm, contract, accounts, indexes=(1, 2, 3)):
    for account_index, text in zip(indexes, TEXTS):
        vm.sender = accounts[account_index]
        contract.submit_availability('hm-8', text)


def llm(vm, masks=(3, 2, 4)):
    vm.mock_llm(r'.*HearingMosaic availability normalization.*', json.dumps({'rows': [
        {'index': i, 'slot_mask': mask, 'accommodation_code': i} for i, mask in enumerate(masks)
    ]}))


def test_full_maximum_matching(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    contract.seat('hm-8')
    row = contract.get_hearing('hm-8')
    assert row['state'] == 'FULL'
    assert row['assignment'] == [[0, 0], [1, 1], [2, 2]]
    assert len(row['digests']) == 3


def test_collision_yields_partial_seating(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm, (1, 1, 1))
    contract.seat('hm-8')
    row = contract.get_hearing('hm-8')
    assert row['state'] == 'PARTIAL' and row['assignment'] == [[0, 0]]


def test_named_participant_and_replay(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    direct_vm.sender = direct_accounts[4]
    with direct_vm.expect_revert('named participant'):
        contract.submit_availability('hm-8', TEXTS[0])
    direct_vm.sender = direct_accounts[1]
    contract.submit_availability('hm-8', TEXTS[0])
    with direct_vm.expect_revert('one statement'):
        contract.submit_availability('hm-8', TEXTS[0])


def test_sparse_expired_collection_uses_dense_indexes(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30, 4)
    submit(direct_vm, contract, direct_accounts, (1, 3, 4))
    direct_vm.warp('2035-01-01T00:00:31+00:00'); llm(direct_vm)
    contract.seat('hm-8')
    assert contract.get_hearing('hm-8')['state'] == 'PARTIAL'


def test_validator_rejects_forged_mask(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    row = contract.hearings['HM-8']
    texts = [{'index': i, 'participant_index': i, 'text': TEXTS[i]} for i in range(3)]
    result = contract._map(row, texts)
    assert direct_vm.run_validator(leader_result=result) is True
    forged = {'rows': [dict(item) for item in result['rows']]}; forged['rows'][0]['slot_mask'] = 0
    assert direct_vm.run_validator(leader_result=forged) is False


def test_permissionless_incomplete_close(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30)
    direct_vm.warp('2035-01-01T00:00:31+00:00'); direct_vm.sender = direct_accounts[5]
    contract.close_incomplete('hm-8')
    assert contract.get_hearing('hm-8')['state'] == 'INCOMPLETE'
