def mask_phone_number(phone_number):
    """
    Masks a phone number showing only beginning and ending digits.
    Works with or without country code.
    """
    if not phone_number:
        return None
        
    # Clean the phone number
    phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # For very short numbers, return as is
    if len(phone_number) < 7:
        return phone_number
    
    # Determine prefix length based on format
    has_country_code = phone_number.startswith('+')
    prefix_length = 5 if (has_country_code and len(phone_number) > 12) else 4
    
    # Ensure prefix length doesn't exceed phone number length minus 2
    prefix_length = min(prefix_length, len(phone_number) - 2)
    
    # Get the parts
    prefix = phone_number[:prefix_length]
    suffix = phone_number[-2:]
    mask_length = len(phone_number) - prefix_length - 2
    
    # Return masked number
    return f"{prefix}{'*' * mask_length}{suffix}"
