import unittest

from src.delivery import calculate_delivery_cost


class TestDeliveryService(unittest.TestCase):
    def test_returns_error_for_zero_weight(self):
        self.assertEqual(calculate_delivery_cost(0, 200, "обычный"), (-1, "0000-00-00"))

    def test_returns_error_for_weight_over_fifty_kg(self):
        self.assertEqual(calculate_delivery_cost(50.01, 200, "обычный"), (-1, "0000-00-00"))

    def test_returns_error_for_negative_distance(self):
        self.assertEqual(calculate_delivery_cost(2, -1, "обычный"), (-1, "0000-00-00"))

    def test_returns_error_for_distance_over_limit(self):
        self.assertEqual(calculate_delivery_cost(2, 5001, "обычный"), (-1, "0000-00-00"))

    def test_returns_error_for_invalid_package_type(self):
        self.assertEqual(calculate_delivery_cost(2, 200, "коробка"), (-1, "0000-00-00"))

    def test_calculates_regular_package_cost(self):
        self.assertEqual(calculate_delivery_cost(2, 200, "обычный"), (1200, "2026-09-04"))

    def test_calculates_fragile_package_cost(self):
        self.assertEqual(calculate_delivery_cost(5, 200, "хрупкий"), (1500, "2026-09-04"))

    def test_calculates_dangerous_package_cost(self):
        self.assertEqual(calculate_delivery_cost(5, 200, "опасный"), (2200, "2026-09-04"))

    def test_applies_coefficient_for_weight_above_five_kg(self):
        self.assertEqual(calculate_delivery_cost(6, 200, "обычный"), (1440, "2026-09-04"))

    def test_applies_medium_coefficient_below_twenty_kg(self):
        self.assertEqual(calculate_delivery_cost(19.9, 200, "обычный"), (1440, "2026-09-04"))

    def test_applies_medium_coefficient_at_exactly_twenty_kg(self):
        self.assertEqual(calculate_delivery_cost(20, 200, "обычный"), (1440, "2026-09-04"))

    def test_applies_heavy_coefficient_for_fifty_kg(self):
        self.assertEqual(calculate_delivery_cost(50, 200, "обычный"), (1800, "2026-09-04"))

    def test_uses_one_day_for_exactly_five_hundred_km(self):
        self.assertEqual(calculate_delivery_cost(2, 500, "обычный"), (2700, "2026-09-04"))

    def test_uses_two_days_for_five_hundred_one_km(self):
        self.assertEqual(calculate_delivery_cost(2, 501, "обычный"), (2705, "2026-09-05"))

    def test_uses_three_days_for_one_thousand_four_hundred_ninety_nine_km(self):
        self.assertEqual(calculate_delivery_cost(2, 1499, "обычный"), (7695, "2026-09-06"))

    def test_uses_three_days_for_one_thousand_five_hundred_km(self):
        self.assertEqual(calculate_delivery_cost(2, 1500, "обычный"), (7700, "2026-09-06"))

    def test_express_service_adds_fifty_percent_to_cost(self):
        cost, _ = calculate_delivery_cost(2, 200, "хрупкий", True)
        self.assertEqual(cost, 2250)

    def test_express_service_never_returns_same_day_delivery(self):
        _, delivery_date = calculate_delivery_cost(2, 499, "обычный", True)
        self.assertEqual(delivery_date, "2026-09-04")

    def test_express_service_rounds_half_days_up(self):
        _, delivery_date = calculate_delivery_cost(2, 1001, "обычный", True)
        self.assertEqual(delivery_date, "2026-09-05")

    def test_result_contains_cost_and_date(self):
        result = calculate_delivery_cost(2, 200, "обычный")
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], int)
        self.assertRegex(result[1], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
