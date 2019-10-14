import sys
from cs50 import get_string

NUM_WORDS_ALPHA = 26

# encrypt text


def encrypt(text, shift):
    result = ""
    for c in text:
        asciiC = ord(c)
        # shift ascii value of c according to value of shift
        if (c.isalpha() and c.isupper()):
            shiftValue = (asciiC + shift) % ord('Z')
            if (shiftValue < NUM_WORDS_ALPHA):
                shiftValue = ord('A') - 1 + shiftValue
        elif(c.isalpha() and c.islower()):
            shiftValue = (asciiC + shift) % ord('z')
            if (shiftValue < NUM_WORDS_ALPHA):
                shiftValue = ord('a') - 1 + shiftValue
        else:
            # ignore non alphabetical characters
            shiftValue = asciiC
        result += chr(shiftValue)
    return result


def main():
    # guard conditions to ensure correct usage
    if (len(sys.argv) != 2):
        print("usage: python caesar.py number")
        sys.exit(1)
    shift = int(sys.argv[1])
    text = get_string("plaintext: ")
    if (shift > NUM_WORDS_ALPHA):
        shift = shift % NUM_WORDS_ALPHA
    if (shift == 0):
        print(text)
        sys.exit(0)
    if (shift < 0):
        print("Invalid shift value. Should be > 0")
        sys.exit(2)

    # shift / encrypt given text
    encrypted = encrypt(text, shift)
    print(f"ciphertext: {encrypted}")
    sys.exit(0)


main()