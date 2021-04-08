import re

def extract_int_from_string(word):
    if word:
        return int(re.search('[0-9]+', word).group())
    return None


if __name__ == '__main__':
    print(extract_int_from_string('500ms'))