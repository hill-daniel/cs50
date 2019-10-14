from cs50 import get_int


def calculateScore(digit):
    # calculate score accorung to luhn's algorithm
    product = digit * 2
    if (product > 9):
        product = (product // 10) + (product % 10)
    return product


def validate(checkSum, lastDigit, secondLastDigit):
    # validate and check which type of credit card supplier it is
    if (checkSum % 10 != 0):
        return "INVALID"
    prefix = lastDigit * 10 + secondLastDigit
    if (lastDigit == 4):
        return "VISA"
    if (prefix == 34 or prefix == 37):
        return "AMEX"
    if (prefix >= 51 and prefix <= 55):
        return "MASTERCARD"
    return "INVALID"


def main():
    ccNumber = get_int("Number: ")
    counter = 0
    checkSum = 0
    secondLastDigit = 0

    # process number digit for digit
    while True:
        counter += 1
        lastDigit = ccNumber % 10
        # calculate score for every other digit
        if (counter % 2 == 0):
            secondLastDigit = lastDigit
            checkSum += calculateScore(lastDigit)
        else:
            checkSum += lastDigit
        ccNumber //= 10
        if (ccNumber == 0):
            break

    # validate and print result
    print(validate(checkSum, lastDigit, secondLastDigit))


main()
