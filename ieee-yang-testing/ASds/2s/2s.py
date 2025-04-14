
def signed_to_hex_twos_complement(number, bit_size):
    if number < -(2**(bit_size - 1)) or number >= 2**(bit_size - 1):
        raise ValueError("Number out of range for the given bit size.")

    # If the number is negative, calculate two's complement
    if number < 0:
        number = (1 << bit_size) + number

    # Convert to hexadecimal and format
    hex_representation = f"{number:0{bit_size // 4}X}"
    return hex_representation

def unsigned_to_hex(number, bit_size):
    if number < 0 or number >= 2**bit_size:
        raise ValueError("Number out of range for the given bit size.")

    # Convert to hexadecimal and format
    hex_representation = f"{number:0{bit_size // 4}X}"
    return hex_representation

def hex_twos_complement_to_decimal(hex_str, bit_size):
    # Remove any "0x" prefix if present
    hex_str = hex_str.lstrip("0x")

    # Convert the hex string to an integer
    value = int(hex_str, 16)

    # Check if the number is negative (if the most significant bit is set)
    if value >= 2**(bit_size - 1):
        value -= 2**bit_size

    return value

# Example usage
try:
    bit_size = 96  # Example: 96-bit

    print(f"\nsigned dec -> hex\n")

    signed_number = -2
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = -1
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = 1
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = 2
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = 39614081257132168796771975167
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = -604462909807314587353088
    hex_result = signed_to_hex_twos_complement(signed_number, bit_size)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement): {hex_result}")

    signed_number = -604462909807314587353088
    hex_result = signed_to_hex_twos_complement(signed_number, 80)
    print(f"Signed number: {signed_number}")
    print(f"Hexadecimal (two's complement) (80-bit): {hex_result}")

    print(f"\nsigned hex->dec\n")

    signed_hex_number = "FFFFFFFFFFFFFFFFFFFFFFFF"
    dec_result = hex_twos_complement_to_decimal(signed_hex_number, bit_size)
    print(f"Signed Hex number: {signed_hex_number}")
    print(f"Decimal: {dec_result}")

    signed_hex_number = "EFFFFFFFFFFFFFFFFFFFFFFF"
    dec_result = hex_twos_complement_to_decimal(signed_hex_number, bit_size)
    print(f"Signed Hex number: {signed_hex_number}")
    print(f"Decimal: {dec_result}")

    signed_hex_number = "8FFFFFFFFFFFFFFFFFFFFFFF"
    dec_result = hex_twos_complement_to_decimal(signed_hex_number, bit_size)
    print(f"Signed Hex number: {signed_hex_number}")
    print(f"Decimal: {dec_result}")

    signed_hex_number = "800000000000000000000000"
    dec_result = hex_twos_complement_to_decimal(signed_hex_number, bit_size)
    print(f"Signed Hex number: {signed_hex_number}")
    print(f"Decimal: {dec_result}")


    signed_hex_number = "7FFFFFFFFFFFFFFFFFFFFFFF"
    dec_result = hex_twos_complement_to_decimal(signed_hex_number, bit_size)
    print(f"Signed Hex number: {signed_hex_number}")
    print(f"Decimal: {dec_result}")

    unsigned_number = 79228162514264337593543950335
    hex_result = unsigned_to_hex(unsigned_number, bit_size)
    print(f"Unsigned number: {unsigned_number}")
    print(f"Hexadecimal: {hex_result}")
except ValueError as e:
    print(e)

