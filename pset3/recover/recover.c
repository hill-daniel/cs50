#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef uint8_t  BYTE;

bool isJpgBlock(BYTE *buffer);
void recoverJpgs(FILE *inptr);

const int BLOCK_SIZE = 512;

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover infile\n");
        return 1;
    }

    // read raw image
    FILE *infile = fopen(argv[1], "r");
    if (infile == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", argv[1]);
        return 2;
    }

    recoverJpgs(infile);
    return 0;
}

// checks if given buffer block is start of jpg data
bool isJpgBlock(BYTE *buffer)
{
    return buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0;
}

// recovers jpgs from file
void recoverJpgs(FILE *f)
{
    int jpgFileIndex  = 0;
    FILE *outptr = NULL;
    BYTE *buffer = malloc(BLOCK_SIZE * sizeof(BYTE));

    while (fread(buffer, 1, 512, f) > 0)
    {
        if (isJpgBlock(buffer))
        {
            // start of new jpg block, hence close current file
            if (outptr != NULL)
            {
                jpgFileIndex++;
                fclose(outptr);
            }
            char outfile[8];
            sprintf(outfile, "%03i.jpg", jpgFileIndex);
            outptr = fopen(outfile, "wb");
        }

        if (outptr != NULL)
        {
            fwrite(buffer, BLOCK_SIZE, 1, outptr);
        }
    }
    free(buffer);
    fclose(f);
}
