import decimal
from decimal import Decimal


def flatten_json(nested_json, parent_key="", sep="."):
    """
    Flatten a nested JSON object into a flat dictionary with dot notation keys
    """
    items = {}
    for key, value in nested_json.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, sep=sep))
        else:
            items[new_key] = value
    return items


def format_obj(obj):
    """
    Recursively format all number strings in the object to int or float
    """
    if isinstance(obj, dict):
        # Handle dictionary
        return {k: format_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Handle list
        return [format_obj(item) for item in obj]
    elif isinstance(obj, str):
        # Try to convert string to number if possible
        try:
            # First try to convert to int
            if obj.isdigit():
                return int(obj)
            # If it has decimal point or scientific notation, convert to Decimal first
            decimal_val = Decimal(obj)
            # If it's a whole number, convert to int
            if decimal_val.as_tuple().exponent >= 0:
                return int(decimal_val)
            # Otherwise convert to float
            return float(decimal_val)
        except (ValueError, decimal.InvalidOperation):
            # If conversion fails, return original string
            return obj
    # Return all other types as is
    return obj