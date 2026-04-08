def gate(status: str) -> bool:
    mapping = {
        "pass": False,
        "fail": True,
        "missing": True,
        "timeout": True,
    }
    if status not in mapping:
        raise ValueError(f"unknown status: {status}")
    return mapping[status]


assert gate("pass") is False
assert gate("fail") is True
assert gate("missing") is True
assert gate("timeout") is True

raised = False
try:
    gate("absent")
except ValueError:
    raised = True
assert raised is True

print("Local gate whole-system overclaim mapping behaves as specified.")
