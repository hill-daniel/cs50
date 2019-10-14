// Resizes a BMP file

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "bmp.h"


int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize n infile outfile\n");
        return 1;
    }

    // remember filenames and f
    char *fstr = argv[1];
    int n = atoi(fstr);
    if (n <= 0)
    {
        fprintf(stderr, "Provide valid number for n, n > 0.\n");
        return 1;
    }
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    BITMAPFILEHEADER bfOut = bf;

    BITMAPINFOHEADER biOut = bi;
    // calc resized width and heigth
    biOut.biWidth = n * bi.biWidth;
    biOut.biHeight = n * bi.biHeight;

    // determine padding for scanlines
    int paddingIn = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int paddingOut = (4 - (biOut.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // calc new file size
    biOut.biSizeImage = ((sizeof(RGBTRIPLE) * biOut.biWidth) + paddingOut) * abs(biOut.biHeight);
    bfOut.bfSize = biOut.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bfOut, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&biOut, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        int lineIndex = 0;
        RGBTRIPLE pixelRow[biOut.biWidth];
        // iterate over pixels in scanline
        for (int j = 0; j < bi.biWidth; j++)
        {
            // temporary storage
            RGBTRIPLE triple;
            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
            for (int k = 0; k < n; k++)
            {
                pixelRow[lineIndex] = triple;
                lineIndex++;
            }
        }

        // skip over padding, if any
        fseek(inptr, paddingIn, SEEK_CUR);

        // write row and padding (if any) to outfile
        for (int j = 0; j < n; j ++)
        {
            fwrite(pixelRow, sizeof(pixelRow), 1, outptr);
            for (int m = 0; m < paddingOut; m++)
            {
                fputc(0x00, outptr);
            }
        }
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}