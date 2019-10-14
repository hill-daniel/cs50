import sys
from cs50 import get_string


def loadDic(dicFile):
    # load dictionary (i.e. a set) from text file
    file = open(dicFile, "r")
    dic = set()
    while True:
        line = file.readline()
        if (line == ""):
            break
        # add whitespace stripped word to dic
        dic.add(line.strip())
    return dic


def censor(message, dic):
    # censor a message with given dictionary
    # firs split message into individual words (i.e. tokens)
    tokens = message.split(" ")
    censoredMessage = []

    for token in tokens:
        if (token.lower() in dic):
            # add a star for each character in word to censor it
            censoredMessage.append("*" * len(token))
        else:
            censoredMessage.append(token)
    return " ".join(censoredMessage)


def main():
    if (len(sys.argv) != 2):
        print("usage: python bleep.py banned.txt")
        sys.exit(1)
    # get message and load dictionary
    message = get_string("What message would you like to censor? ")
    dic = loadDic(sys.argv[1])

    # censor message print result
    censored = censor(message, dic)
    print(censored)
    sys.exit(0)


if __name__ == "__main__":
    main()
