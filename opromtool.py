#!/usr/bin/env python


from construct import *

""" PNP Oprom Expansion Header """
expansion_header = Struct("PNP_Expansion_Header",
    Magic("$PnP"),
    ULInt8("Revision"),
    ULInt8("Length_div_16"),
    ULInt16("NextHeaderOffset"),
    Padding(1),
    ULInt8("Checksum"),
    ULInt32("DeviceID"),
    ULInt8("ManufacturerStringOffset"),
    ULInt8("ProductNameStringOffset"),
    ULInt8("BaseTypeCode"),
    ULInt8("SubTypeCode"),
    ULInt8("IFTypeCode"),
    BitStruct("DeviceIndicators",
        Flag("Supports_Driver_Init_Model"),
        Flag("May_Be_Shadowed"),
        Flag("Read_Cacheable"),
        Flag("ROM_Only_Required_If_Selected_Boot_Device"),
        Padding(1),
        Flag("Initial_Program_Load_Device"),
        Flag("Input_Device"),
        Flag("Display_Device"),
        ),
    ULInt16("BootConnectionVector"),
    ULInt16("BootstrapEntryPoint"),
    Padding(2),
    ULInt16("StaticResourceInformationVector"),
    If(lambda ctx: ctx.NextHeaderOffset != 0x0000,
        Pointer(lambda ctx: ctx.NextHeaderOffset,
            LazyBound("next", lambda: expansion_header),
        ),
    ),
)

""" Legacy OpROM header """
oprom = Struct("OpRom",
    Magic("\x55\xaa"),
    ULInt8("RomLength_div_512"),
    ULInt32("InitVector"),
    Padding(0x13),
    ULInt16("ExpansionHeaderOffset"),
    If(lambda ctx: ctx.ExpansionHeaderOffset != 0x0000
            and (ctx.ExpansionHeaderOffset < ctx.RomLength_div_512 * 512),
        Pointer(
            lambda ctx: ctx.ExpansionHeaderOffset,
            expansion_header),
    ),
)

if __name__ == "__main__":
    fname = "techsource.rom"
    with open(fname, "rb") as rom:
        header = oprom.parse_stream(rom)
        print(header)
        print("Length = {}k".format(header.RomLength_div_512 / 2))


