import re
import os


not_word_digit_pattern = re.compile(r'^[^\w\d]+|[^\w\d]+$')
def power_strip(string):
    return re.sub(not_word_digit_pattern, '', string)
