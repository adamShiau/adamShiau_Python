/******************************************************************************

                            Online C Compiler.
                Code, Compile, Run and Debug C program online.
Write your code in this editor and press "Run" button to compile and execute it.

*******************************************************************************/

#include <stdio.h>
#include <stdint.h>

/*
 * The width of the CRC calculation and result.
 * Modify the typedef for a 16 or 32-bit CRC standard.
 */
typedef uint8_t crc;

#define WIDTH  (8 * sizeof(crc))
#define TOPBIT (1 << (WIDTH - 1))
#define POLYNOMIAL 0x07

crc crcSlow(uint8_t  [], int);

int main()
{
    crc crc_data;
    crc msg[16];
    
    msg[0] = 0x00;
    msg[1] = 0x02;
    msg[2] = 0x94;
    msg[3] = 0x49;
    msg[4] = 0x00;
    msg[5] = 0x00;
    msg[6] = 0x00;
    msg[7] = 0x00;
    msg[8] = 0x00;
    msg[9] = 0x00;
    msg[10] = 0x00;
    msg[11] = 0x00;
    msg[12] = 0x00;
    msg[13] = 0x00;
    msg[14] = 0x00;
    msg[15] = 0x5C;

    printf("Hello World\n");
    printf("WIDTH: %ld\n", WIDTH);
    crc_data = crcSlow(msg, 16);
    printf("%x\n", crc_data);

    return 0;
}


crc crcSlow(uint8_t  message[], int nBytes)
{
    crc  remainder = 0;	

    for(int i=; )
    printf("msg: %x\n", message);
    /*
     * Perform modulo-2 division, a byte at a time.
     */
    for (int byte = 0; byte < nBytes; ++byte)
    {
        /*
         * Bring the next byte into the remainder.
         */
        remainder ^= (message[byte] << (WIDTH - 8));
        
        printf("\nremainder start = %x\n",remainder );

        /*
         * Perform modulo-2 division, a bit at a time.
         */
        for (uint8_t bit = 8; bit > 0; --bit)
        {
            /*
             * Try to divide the current data bit.
             */
            printf("bit: %d, ", bit);
            printf("%x, ", remainder);
            if (remainder & TOPBIT)
            {
                remainder = (remainder << 1) ^ POLYNOMIAL;
            }
            else
            {
                remainder = (remainder << 1);
            }
            
            printf("%x\n", remainder);
        }
    }

    /*
     * The final remainder is the CRC result.
     */
    return (remainder);

}   /* crcSlow() */