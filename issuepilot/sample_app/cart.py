"""A tiny shopping cart used to demonstrate reproducible bug investigation."""


def subtotal(prices: list[float]) -> float:
    """Return the subtotal for a list of item prices.

    Seeded bug: the loop starts at index 1, so the first item is omitted.
    IssuePilot-Repro may change this only after a human approval is recorded.
    """
    total = 0.0
    for index in range(1, len(prices)):
        total += prices[index]
    return round(total, 2)
