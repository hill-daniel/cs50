from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""
    linesOfA = set()
    tokensA = a.split("\n")
    linesOfA.update(tokensA)

    linesOfB = set()
    tokensB = b.split("\n")
    linesOfB.update(tokensB)

    # compute intersection i.e. set which contains only lines of both, a and b
    result = linesOfA.intersection(linesOfB)
    return result


def sentences(a, b):
    """Return sentences in both a and b"""
    sentencesOfA = set()
    sentencesOfA.update(sent_tokenize(a, language='english'))

    sentencesOfB = set()
    sentencesOfB.update(sent_tokenize(b, language='english'))

    # compute intersection i.e. set which contains only sentences of both, a and b
    result = sentencesOfA.intersection(sentencesOfB)
    return result


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""
    subs = set()
    if (n > len(a)):
        return subs
    if (a == b and len(a) == n):
        return [a]

    for i in range(0, len(a) - n + 1):
        substring = a[i:i+n]
        if (substring in b):
            subs.add(substring)
    return subs
