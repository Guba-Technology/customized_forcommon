# Mapping for Amharic numbers
ONES = [
    "", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"
]

TENS = [
    "", "አስራ", "ሃያ", "ሠላሳ", "አርባ", "አምሳ", "ስልሳ", "ሰባ", "ሰማንያ", "ዘጠና"
]

HUNDRED = "መቶ"
THOUSAND = "ሺ"
MILLION = "ሚሊዮን"
BILLION = "ቢሊዮን"


def num_to_amharic_words(n: int) -> str:
    """Convert integer numbers to Amharic words (basic version)."""
    if n == 0:
        return "ዜሮ"

    words = ""

    if n >= 1_000_000_000:
        words += num_to_amharic_words(n // 1_000_000_000) + " " + BILLION + " "
        n %= 1_000_000_000

    if n >= 1_000_000:
        words += num_to_amharic_words(n // 1_000_000) + " " + MILLION + " "
        n %= 1_000_000

    if n >= 1_000:
        words += num_to_amharic_words(n // 1_000) + " " + THOUSAND + " "
        n %= 1_000

    if n >= 100:
        words += ONES[n // 100] + " " + HUNDRED + " "
        n %= 100

    if n >= 10:
        words += TENS[n // 10] + " "
        n %= 10

    if n > 0:
        words += ONES[n] + " "

    return words.strip()


def currency_in_amharic(amount: float) -> str:
    """Convert a currency amount into Amharic words with ብር."""
    integer_part = int(amount)
    decimal_part = round((amount - integer_part) * 100)

    words = num_to_amharic_words(integer_part) + " ብር"

    if decimal_part > 0:
        words += " ከ " + num_to_amharic_words(decimal_part) + " ሳንቲም"

    return words.strip()
