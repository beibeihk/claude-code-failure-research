"""Small public API with intentionally incorrect cent rounding."""
from decimal import Decimal, ROUND_DOWN

def net_total(price: Decimal, qty: int, rate: Decimal = Decimal('0')) -> Decimal:
    """Aggregate, apply a proportional discount, then round half up to cents."""
    if qty < 0:
        raise ValueError('qty must be non-negative')
    if not Decimal('0') <= rate <= Decimal('1'):
        raise ValueError('rate must be between zero and one')
    # Existing defect: rounds each unit down before aggregation and discount.
    unit = price.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    return (unit * qty * (Decimal('1') - rate)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
