from issuepilot.sample_app.cart import subtotal


def test_subtotal_includes_first_item():
    assert subtotal([12.50, 3.25]) == 15.75


def test_empty_cart_subtotal_is_zero():
    assert subtotal([]) == 0.0


def test_single_item_subtotal_includes_item():
    assert subtotal([4.25]) == 4.25
