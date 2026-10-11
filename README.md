# Hearing Mosaic

The room begins as a set of possible seats, not a wall of calendar fields.

A convener freezes three to eight hearing slots and the invited addresses. Each participant writes availability in ordinary language. Validators turn each statement into an exact slot mask and a bounded accommodation code. Contract code then computes a deterministic maximum matching, selecting the lexicographically earliest assignment when several seatings are equally large.

The hearing closes `FULL`, `PARTIAL`, or `INCOMPLETE`. The model never chooses the final seating.

Configured wallets in the live rehearsal are operator-controlled role fixtures, not independent participants.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

## Live chamber

- Contract: [`0xe838adf07997F960BD1B81CC3885319AC8AD7327`](https://explorer-studio.genlayer.com/address/0xe838adf07997F960BD1B81CC3885319AC8AD7327)
- Reviewed source: [`e38b497`](https://github.com/IDAK2/hearing-mosaic/tree/e38b497889b23d29e0514dd9c76d2e1a5c434c86)
- Live hearing: `HEAR-1791756980`, final state `FULL`, assignment `[[0,0],[1,1],[2,2]]`.
- Verification: finalized, majority agree, successful execution, exact deployed-source match.
