## Hex Byte Parser

### Claim

This component performs one narrow task: given an exactly two-character hexadecimal token, Python converts it into the corresponding integer byte in `[0, 255]`.

The claim is local and deterministic:
- accepted inputs are exactly two hexadecimal characters
- accepted tokens map to their canonical integer value
- any token outside that finite input alphabet is rejected

This component does **not** make any forecast, causal, or whole-system claim. It is only a parser over a fixed input alphabet.

### Local Mapping

Let `token` be a string.

The component:
- strips no whitespace
- accepts no prefixes such as `0x`
- accepts no separators, signs, decimals, or longer strings
- accepts only `[0-9A-Fa-f]{2}`
- returns `int(token, 16)` for accepted inputs

### Falsification Logic

The thesis fails if any of the following occur:
- a valid two-character hexadecimal token is rejected
- an accepted token maps to the wrong integer byte
- an invalid token is silently accepted

### Core Position

The thesis is that deterministic local parsing over a fixed two-character hexadecimal alphabet can be specified and falsified without relying on any external reality claim.
