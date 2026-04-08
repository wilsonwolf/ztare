# Program Genesis

This directory holds immutable genesis artifacts for supervisor-routed programs.

Purpose:
- record why a program was opened
- bind it to a human-authored seed spec
- preserve explicit out-of-scope boundaries

Rules:
- one file per program: `<program_id>.json`
- write once at program acceptance
- never mutate after creation
- referenced by the supervisor program registry, but not embedded in it

Not every legacy program has a genesis artifact. Older programs may predate this contract.
