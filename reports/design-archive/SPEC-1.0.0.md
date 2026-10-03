# Invoice contract

`net_total(price, qty, rate=Decimal('0'))` computes `price * qty * (1-rate)`
in Decimal arithmetic, then rounds once to cents using ROUND_HALF_UP.
Negative prices are valid credit lines. Negative quantities and rates outside
[0, 1] raise ValueError. Preserve the function's name, signature and validation.

The existing tests expose a real arithmetic defect. Read this contract before
editing. Run `python verify.py` before editing and after the final edit.
