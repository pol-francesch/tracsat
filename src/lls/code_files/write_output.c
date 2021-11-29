/* Include statements */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include "write_output.h"

/* Constants and global variables */

#define GPIO_BASE 0x00200000
#define TIMER_BASE 0x00003000
#define INT_BASE 0x0000B000

volatile unsigned *gpio,*gpset,*gpclr,*gpin,*timer,*intrupt,*intquad;
enum pitypes {NOTSET,ARM6,ARM7,PI4};
enum pitypes pitype = NOTSET;  // set by setup()  0=not set 1=ARMv6  2=ARMv7

unsigned int timend;
#define TIMERLOOP  while((((*timer)-timend) & 0x80000000) != 0)
#define TIMEOUT           (((*timer-timend) & 0x80000000) == 0)
#define NOTIMEOUT         (((*timer-timend) & 0x80000000) != 0)


#define GP2_HI *gpset = (1 << 2)  // GPIO 2 output hi
#define GP2_LO *gpclr = (1 << 2)  // GPIO 2 output lo 
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1 << (((g)%10)*3))
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7 << (((g)%10)*3))

/* Function definitions */

int main() {
    int arr[100000] = {0};
    write_data_test(arr, 100000);
    return 0;
}

void write_data_test(int *arr, int size) {
  printf("Setting up...\n");

  sleep(3);

  /* Run setup function */

  if(setup() == 0) {
      return;  
  }

  sleep(2);

  /* Set GPIO 2 as output */

  INP_GPIO(2);   // must do this first to zero control bits
  OUT_GPIO(2);   // set as output

  /* Disable interrupts */

  if(interrupts(0) == 0) {
      return;
  }

  /* Setup timer */
  timend = *timer;

  /* Send signal to tell other pi to start reading */

  timend += 2;    // microseconds
  TIMERLOOP;     
  GP2_HI;

  /* Write data and increment timer */

  for(int n = 0 ;  n < size  ; ++n)   {
      timend += 2;    // microseconds
      TIMERLOOP;     
      if (arr[n]) {
          GP2_HI;
      }
      else {
          GP2_LO;
      }
  }



  /* re-enable interrupts */

  interrupts(1);
}

/* interrupts */

/* interrupts(0)   disable interrupts
 * nterrupts(1)   re-enable interrupts

  * return 1 = OK
       0 = error with message print

  * Uses pitype and intrupt/intquad pointers set by setup()

  * Avoid calling immediately after keyboard input
  * or key strokes will not be dealt with properly
  */

int interrupts(int flag)
  {
  int n;
  unsigned int temp131;
  static unsigned int sav132 = 0;
  static unsigned int sav133 = 0;
  static unsigned int sav134 = 0;
  static unsigned int sav4 = 0;
  static unsigned int sav16 = 0;
  static unsigned int sav17 = 0;
  static unsigned int sav18 = 0;
  static unsigned int sav19 = 0;
  static unsigned int sav20 = 0;
  static unsigned int sav21 = 0;
  static unsigned int sav22 = 0;
  static unsigned int sav23 = 0;
  static int disflag = 0; 
  
   
  if(pitype == NOTSET)
    {
    printf("Setup not done\n");
    return(0);
    }
  
  if(flag == 0)    // disable
    {
    if(disflag != 0)
      {
      // Interrupts already disabled so avoid printf
      return(1);
      }

   // Note on register offsets
   // If a register is described in the documentation as offset 0x20C = 524 bytes
   // The pointers such as intrupt are 4 bytes long,
   // so intrupt+131 points to intrupt + 4x131 = offset 0x20C 

           // save current interrupt settings  

    if(pitype == ARM7)   // Pi3 only
      {
      sav4 = *(intquad+4);     // Performance Monitor Interrupts set  register 0x0010
      sav16 = *(intquad+16);   // Core0 timers Interrupt control  register 0x0040 
      sav17 = *(intquad+17);   // Core1 timers Interrupt control  register 0x0044
      sav18 = *(intquad+18);   // Core2 timers Interrupt control  register 0x0048
      sav19 = *(intquad+19);   // Core3 timers Interrupt control  register 0x004C
             // the Mailbox interrupts are probably disabled anyway - but to be safe:
      sav20 = *(intquad+20);   // Core0 Mailbox Interrupt control  register 0x0050 
      sav21 = *(intquad+21);   // Core1 Mailbox Interrupt control  register 0x0054
      sav22 = *(intquad+22);   // Core2 Mailbox Interrupt control  register 0x0058
      sav23 = *(intquad+23);   // Core3 Mailbox Interrupt control  register 0x005C
      }
  
    if(pitype == PI4)
      {
      sav4 = *(intrupt);               // GICD_CTLR register
      *(intrupt) = sav4 & 0xFFFFFFFE;  // clear bit 0 enable forwarding to CPU
      }
    else
      {                      
      sav134 = *(intrupt+134);  // Enable basic IRQs register 0x218
      sav132 = *(intrupt+132);  // Enable IRQs 1 register 0x210
      sav133 = *(intrupt+133);  // Enable IRQs 2 register 0x214

           // Wait for pending interrupts to clear
           // Seems to work OK without this, but it does no harm
           // Limit to 100 tries to avoid infinite loop
      n = 0;
      while( (*(intrupt+128) | *(intrupt+129) | *(intrupt+130)) != 0 && n < 100)
        ++n;
      } 
         // disable all interrupts

    if(pitype == ARM7)   // Pi3 only
      {
      *(intquad+5) = sav4;   // disable via Performance Monitor Interrupts clear  register 0x0014
      *(intquad+16) = 0;     // disable by direct write
      *(intquad+17) = 0;
      *(intquad+18) = 0;
      *(intquad+19) = 0;
      *(intquad+20) = 0;
      *(intquad+21) = 0;
      *(intquad+22) = 0;
      *(intquad+23) = 0;
      }
       
    if(pitype != PI4)
      {
      temp131 = *(intrupt+131);  // read FIQ control register 0x20C 
      temp131 &= ~(1 << 7);      // zero FIQ enable bit 7
      *(intrupt+131) = temp131;  // write back to register
                               // attempting to clear bit 7 of *(intrupt+131) directly
                               // will crash the system 

      *(intrupt+135) = sav132; 
              // disable by writing to Disable IRQs 1 register 0x21C
      *(intrupt+136) = sav133;  
             // disable by writing to Disable IRQs 2 register 0x220
      *(intrupt+137) = sav134; 
             // disable by writing to Disable basic IRQs register 0x224
      }
            
    disflag = 1;   // interrupts disabled
    }
  else            // flag = 1 enable
    {
    if(disflag == 0)
      {
      // Interrupts are enabled
      return(1);
      }

             // restore all saved interrupts
    if(pitype == PI4)
      {
      *(intrupt) = sav4;  // set bit 0
      }
    else
      {
      *(intrupt+134) = sav134;
      *(intrupt+133) = sav133;
      *(intrupt+132) = sav132;    

      temp131 = *(intrupt+131);     // read FIQ control register 0x20C
      temp131 |= (1 << 7);          // set FIQ enable bit
      *(intrupt+131) = temp131;     // write back to register
      }
      
    if(pitype == ARM7)  // Pi3 only
      {  
      *(intquad+4) = sav4;
      *(intquad+16) = sav16;
      *(intquad+17) = sav17;
      *(intquad+18) = sav18;
      *(intquad+19) = sav19;
      *(intquad+20) = sav20;
      *(intquad+21) = sav21;
      *(intquad+22) = sav22;
      *(intquad+23) = sav23;
      }
    
    disflag = 0;         // indicates interrupts enabled
    }
  return(1);
  }

/***************** SETUP ****************
Determines Pi type ARMv6 or ARMv7:
  pitype
Sets timer, gpio and interrupt pointers:
  timer,gpio,gpset,gpclr,gpin,intrupt,intquad  
Does not disable interrupts
return 1 = OK
       0 = error with message print
************************************/

int setup()
  {
  int memfd;
  void *gpio_map,*timer_map,*int_map,*quad_map;
  unsigned int baseadd;
  FILE *stream;
  int n,c,getout;

       // read file /proc/cpuinfo to determine PI type
       // look for "ARMv6" or "ARMv7"

  pitype = NOTSET;  // in case fails
          
  baseadd = 0;
  
  stream = fopen("/proc/device-tree/soc/ranges","rb");
            
  if(stream == NULL)
    {
    printf("Failed to open /proc/device-tree/soc/ranges\n");
    return(0);
    }
   
  getout = 0;
  n = 0;
  do
    {
    c = getc(stream);
    if(c == EOF)
      {
      baseadd = 0;
      getout = 1;    
      }      
    else if(n > 3)
      baseadd = (baseadd << 8) + c;
    ++n;
    if(n == 8 && baseadd == 0)
      n = 4;  // read third 4 bytes 
    }
  while(getout == 0 && n < 8);  
  fclose(stream);
  

  if(baseadd == 0x20000000)
    {
    pitype = ARM6;   // Pi2
    printf("Pi type = ARMv6\n");
    }
  else if(baseadd == 0x3F000000)
    {
    pitype = ARM7;  // 3B+
    printf("Pi type = ARMv7\n");
    }
  else if(baseadd == 0xFE000000)
    {
    pitype = PI4;
    printf("Pi type = Pi4\n");
    }
  else
    {
    printf("Failed to determine Pi type\n");
    return(0);
    }
 
  

  memfd = open("/dev/mem",O_RDWR|O_SYNC);
  if(memfd < 0)
    {
    printf("Mem open error\n");
    pitype = NOTSET;
    return(0);
    }

  gpio_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                  MAP_SHARED,memfd,baseadd+GPIO_BASE);

  timer_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                  MAP_SHARED,memfd,baseadd+TIMER_BASE);

  if(pitype == PI4)
    int_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                  MAP_SHARED,memfd,0xFF841000);  // GIC distributor
  else    
    int_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                  MAP_SHARED,memfd,baseadd+INT_BASE);
  
  if(pitype == ARM7)  // Pi3
    quad_map = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                  MAP_SHARED,memfd,0x40000000);
  else
    quad_map = MAP_FAILED;
 
  close(memfd);

  if(gpio_map == MAP_FAILED ||
     timer_map == MAP_FAILED ||
     int_map == MAP_FAILED ||
     (pitype == ARM7 && quad_map == MAP_FAILED) )
    {
    printf("Map failed\n");
    pitype = NOTSET;
    return(0);
    }

  if(pitype == ARM7)
    intquad = (volatile unsigned *)quad_map;
  
              // interrupt pointer
  intrupt = (volatile unsigned *)int_map;
              // timer pointer
  timer = (volatile unsigned *)timer_map;
  ++timer;    // timer lo 4 bytes
              // timer hi 4 bytes available via *(timer+1)

              // GPIO pointers
  gpio = (volatile unsigned *)gpio_map;
  gpset = gpio + 7;     // set bit register offset 28
  gpclr = gpio + 10;    // clr bit register
  gpin = gpio + 13;     // read all bits register
  return(1);
  }