import re
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from telegram import ReplyKeyboardMarkup, KeyboardButton
from validate_email_address import validate_email


POSSIBLE_NAME_REGEX = re.compile("^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$")


def create_keyboard(answers):
    keyboard = []
    row = []
    i = 1
    for answer in answers:
        row.append(KeyboardButton(answer, callback_data=answer))
        if i == 3:
            keyboard.append(row.copy())
            row = []
            i = 1
        else:
            i += 1
    keyboard.append(row)
    reply_markup = ReplyKeyboardMarkup(keyboard)
    reply_markup.resize_keyboard = True
    return reply_markup


def check_person_name(person_name):
    return POSSIBLE_NAME_REGEX.fullmatch(person_name)


def check_phone_number(phone_number, region_code="DE"):
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(phone_number, region_code))
    except NumberParseException:
        return False


def check_email_address(email_address):
    return validate_email(email_address, verify=False)

