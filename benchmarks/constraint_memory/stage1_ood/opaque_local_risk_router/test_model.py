def route_risk(label: str) -> str:
    mapping = {
        "critical": "manual_review",
        "medium": "secondary_review",
        "low": "auto_clear",
    }
    if label not in mapping:
        raise ValueError(f"unknown label: {label}")
    return mapping[label]


assert route_risk("critical") == "manual_review"
assert route_risk("medium") == "secondary_review"
assert route_risk("low") == "auto_clear"

raised = False
try:
    route_risk("ambiguous")
except ValueError:
    raised = True
assert raised is True

print("Opaque local risk router behaves as specified.")
