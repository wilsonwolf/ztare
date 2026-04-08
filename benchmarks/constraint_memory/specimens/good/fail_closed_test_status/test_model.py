def fail_closed_status(status: str) -> bool:
    mapping = {
        'pass': False,
        'fail': True,
        'missing': True,
        'timeout': True,
    }
    if status not in mapping:
        raise ValueError(f'unknown status: {status}')
    return mapping[status]

assert fail_closed_status('pass') is False
assert fail_closed_status('fail') is True
assert fail_closed_status('missing') is True
assert fail_closed_status('timeout') is True

raised = False
try:
    fail_closed_status('maybe')
except ValueError:
    raised = True
assert raised is True

print('Fail-closed test-status gate behaves as specified.')
