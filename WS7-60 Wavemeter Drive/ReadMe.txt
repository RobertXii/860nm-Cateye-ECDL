**************************************************************************
*                                                                        *
*             USB device installation and program setup                  *
*                                                                        *
*                                 for                                    *
*                                                                        *
*                    HighFinesse Wavelength Meter                        *
*                 HighFinesse Laser Spectrum Analyzer                    *
*            HighFinesse High Definition Spectrum Analyzer               *
*                 HighFinesse Spectrum Analyzer WS/F                     *
*                                                             2024-03-12 *
**************************************************************************


Contents

1. Requirements
2. Installation procedure


**************************************************************************


1. Requirements
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
  For the USB device and Software installation you need:

    - IBM PC compatible computer with MS Windows XP Service Pack 3, Vista or Windows 7 Service Pack 2, Windows 10, or Windows 11 installed
    - 200 MB of free hard disk space
    - 1 free USB slot (ideally of a powered USB hub)
    - 1 free PCIe x1 slot (for PID option)
    - Administrator rights


2. Installation procedure
¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
  Note: In case you are installing a system which includes an additional
        PCIe DAC board used for a Laser Control or PID regulation option,
        assemble the PCIe DAC board after starting the Setup.exe. The Setup will then automatically install the drivers.

  2.1 Wavelength Meter or Spectrum Analyzer
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
  1. Start the setup program '<USB flash drive>:\Setup.exe'.
     This process then registers the necessary drivers in your system 
     and installs the control software.
  2. Connect the Wavelength Meter/Spectrum Analyzer with your computer
     using the included standard USB cable.

  2.2 PCIe DAC board for PID regulation (PID option)
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    1. Switch off the computer and remove the power supply.
    2. Insert the PCIe DAC board to a free PCIe slot on your mainboard,
       docking station or PCIe card extender. (Note: The components of this 
       board are sensitive. Please care for being grounded to avoid the
       risk of destroying the board by electrostic discharge.)
    3. Plug the BNC adapter cable to the D-Sub female of the DAC
       board and fix it tightened with the screws.
    4. Close the housing, reestablish the net power supply and switch on
       your computer.
    5. Start the wavelength meter software

In case you still have a PCI(e) card by Meilhaus the following note applies:

    Note: When the computer is powered and the D/A channels ±15 V power
          supply is connected and active, the D/A channels conditionally 
          can immediately be on -10 V! If so, this only is set back to zero
          when the HighFinesse control software is started. So, to protect
          your electronic equipment, please ensure to either do not supply
          the D/A channels with power (±15 V; only with externally powered 
          DAC boards with separate grounds) or do not attach your equipment
          to the D/A channels outputs before the HighFinesse control
          software is started.

Now, drivers and programs are ready for work.



************************   End of ReadMe.txt   **************************