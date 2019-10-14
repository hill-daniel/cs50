from cs50 import get_int

while True:
    # ask for correct input as long as it takes
    height = get_int("Height: ")
    if (height <= 8 and height > 0):
        break

for i in range(height):
    # calculate whitespaces before blocks to align the last line to screen
    gap = " " * (height - (i + 1))
    # calculate number of blocks for this line
    blocks = "#" * (i + 1) + "  " + "#" * (i + 1)
    print(gap + blocks)
