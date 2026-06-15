from secrets import randbelow


def generate_verification_code():
    return str(randbelow(900000) + 100000)