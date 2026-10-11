# Hearing Mosaic

The room begins as a set of possible seats, not a wall of calendar fields.

A convener freezes three to eight hearing slots and the invited addresses. Each participant writes availability in ordinary language. Validators turn each statement into an exact slot mask and a bounded accommodation code. Contract code then computes a deterministic maximum matching, selecting the lexicographically earliest assignment when several seatings are equally large.

The hearing closes `FULL`, `PARTIAL`, or `INCOMPLETE`. The model never chooses the final seating.

Configured wallets in the live rehearsal are operator-controlled role fixtures, not independent participants.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```
