import unittest
from decimal import Decimal as D
from src.invoice import net_total

class InvoiceTests(unittest.TestCase):
    def test_exact_cents(self): self.assertEqual(net_total(D('12.50'), 2), D('25.00'))
    def test_half_up(self): self.assertEqual(net_total(D('1.005'), 1), D('1.01'))
    def test_aggregate_first(self): self.assertEqual(net_total(D('0.335'), 3), D('1.01'))
    def test_discount_before_round(self): self.assertEqual(net_total(D('1.005'), 2, D('0.5')), D('1.01'))
    def test_negative_half(self): self.assertEqual(net_total(D('-1.005'), 1), D('-1.01'))
    def test_zero_qty(self): self.assertEqual(net_total(D('1.005'), 0), D('0.00'))
    def test_full_discount(self): self.assertEqual(net_total(D('12.50'), 2, D('1')), D('0.00'))
    def test_negative_qty(self):
        with self.assertRaises(ValueError): net_total(D('1'), -1)
    def test_rate_above_one(self):
        with self.assertRaises(ValueError): net_total(D('1'), 1, D('1.1'))
    def test_negative_rate(self):
        with self.assertRaises(ValueError): net_total(D('1'), 1, D('-0.1'))

if __name__ == '__main__': unittest.main()
