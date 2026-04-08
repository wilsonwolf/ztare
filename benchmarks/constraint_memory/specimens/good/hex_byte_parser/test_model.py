def parse_hex_byte(token: str) -> int:
    if not isinstance(token, str):
        raise TypeError("token must be a string")
    if len(token) != 2:
        raise ValueError("token must be exactly two characters")
    if any(ch not in "0123456789abcdefABCDEF" for ch in token):
        raise ValueError("token contains non-hex characters")
    return int(token, 16)


assert parse_hex_byte("00") == 0
assert parse_hex_byte("0f") == 15
assert parse_hex_byte("7F") == 127
assert parse_hex_byte("ff") == 255

for bad_token in ["", "0", "000", "0x10", " 0f", "g1", "1-"]:
    raised = False
    try:
        parse_hex_byte(bad_token)
    except ValueError:
        raised = True
    assert raised is True, bad_token

raised = False
try:
    parse_hex_byte(None)  # type: ignore[arg-type]
except TypeError:
    raised = True
assert raised is True

print("Hex byte parser behaves as specified.")
