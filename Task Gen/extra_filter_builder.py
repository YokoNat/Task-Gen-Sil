def build_extra_filter(section_price_list):
    """
    Given a list of (section, price) tuples, return a string like:
    '100:100, 105-108:250, FloorA:150'
    """
    return ', '.join(f"{section}:{price}" for section, price in section_price_list if section and price)

if __name__ == "__main__":
    # Minimal test
    test_data = [
        ("100", "100"),
        ("105-108", "250"),
        ("FloorA", "150"),
    ]
    result = build_extra_filter(test_data)
    print("Result:", result)
    # Should print: 100:100, 105-108:250, FloorA:150 