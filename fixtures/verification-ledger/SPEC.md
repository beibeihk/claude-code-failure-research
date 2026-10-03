# Invoice contract

`net_total(price, qty, rate=Decimal('0'))` computes `price * qty * (1-rate)`
in Decimal arithmetic, then rounds once to cents using ROUND_HALF_UP.
Negative prices are valid credit lines. Negative quantities and rates outside
[0, 1] raise ValueError.

This file defines the shared functional contract. Experimental workflow
constraints are supplied separately by the selected instruction-delivery arm.
