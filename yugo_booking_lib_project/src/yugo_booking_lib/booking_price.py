from datetime import datetime


class BookingPrice:
    """
    Simple price helper, similar style to the 'NumberProperties' example
    from the tutorial. It focuses on:
      - calculating number of nights
      - calculating total price with optional tax + fixed fee
    """

    def calculate_nights(self, check_in_str: str, check_out_str: str, fmt: str = "%Y-%m-%d") -> int:
        
        check_in = datetime.strptime(check_in_str, fmt).date()
        check_out = datetime.strptime(check_out_str, fmt).date()
        diff = (check_out - check_in).days
        return max(diff, 0)

    def calculate_total_price(
        self,
        nights: int,
        nightly_rate: float,
        tax_rate: float = 0.0,
        fixed_fee: float = 0.0,
    ) -> float:
        """
        Given nights + nightly_rate, apply optional tax + fixed fee.
        total = nights * nightly_rate + tax + fixed_fee
        """
        base = nights * nightly_rate
        tax = base * tax_rate
        total = base + tax + fixed_fee
        return round(total, 2)


if __name__ == "__main__":
    
    bp = BookingPrice()
    nights = bp.calculate_nights("2026-01-08", "2026-01-15")
    total = bp.calculate_total_price(nights, nightly_rate=60.0, tax_rate=0.13, fixed_fee=50.0)

    print(f"Nights: {nights}")
    print(f"Total price: €{total}")
