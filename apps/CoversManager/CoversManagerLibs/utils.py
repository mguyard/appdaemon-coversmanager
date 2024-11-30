import re


def isEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant entity.

    Parameters:
        value (str): The value to be checked.

    Returns:
        str: The input value if it is in the correct format.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    if re.match(r"^(([a-z_]+)\.([a-z0-9_]+))(\.(([a-z0-9_]+)(\[([a-z0-9_]+)\])?)+)?$", value) is None:
        raise ValueError("Value must be a valid HA sensor format")
    return value


def isSpecificEntityFormat(value: str, formats: list) -> str:
    """
    Checks if the given value is in one of the specific entity formats.

    Args:
        value (str): The value to be checked.
        formats (list): A list of specific entity formats.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in one of the specified entity formats.
    """
    value = isEntityFormat(value)
    for format in formats:
        if value.startswith(f"{format}."):
            return value
    supported_formats = ", ".join(formats)
    raise ValueError(f"Value must be a valid HA entity in one of the formats: {supported_formats}")


def isCoverEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant cover entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, ["cover"])


def isSensorEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant sensor entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, ["sensor"])


def isBinarySensorEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of a Home Assistant binary sensor entity.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    return isSpecificEntityFormat(value, ["binary_sensor"])


def isLockerEntityFormat(value: str) -> str:
    """
    Checks if the given value is in the format of supported Home Assistant entity for locker.

    Args:
        value (str): The value to be checked.

    Returns:
        str: The validated value.

    Raises:
        ValueError: If the value is not in the correct format.
    """
    supported_formats = ["binary_sensor","input_boolean"]
    return isSpecificEntityFormat(value, supported_formats)
