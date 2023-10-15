SEGMENT_TYPES = {
    192: { #FF C0
        "abbreviation": "SOF0",
        "name": "Start Of Frame",
        "info": "Baseline DCT"
    },
    193: { #FF C1
        "abbreviation": "SOF1",
        "name": "Start Of Frame",
        "info": "Extended sequential DCT"
    },
    194: { #FF C2
        "abbreviation": "SOF2",
        "name": "Start Of Frame",
        "info": "Progressive DCT"
    },
    195: { #FF C3
        "abbreviation": "SOF3",
        "name": "Start Of Frame",
        "info": "Lossless (sequential)"
    },
    196: { #FF C4
        "abbreviation": "DHT",
        "name": "Define Huffman Table",
        "info": "Huffman Table Definition"
    },
    197: { #FF C5
        "abbreviation": "SOF5",
        "name": "Start Of Frame",
        "info": "Differential sequential DCT"
    },
    198: { #FF C6
        "abbreviation": "SOF6",
        "name": "Start Of Frame",
        "info": "Differential progressive DCT"
    },
    199: { #FF C7
        "abbreviation": "SOF7",
        "name": "Start Of Frame",
        "info": "Differential lossless (sequential)"
    },
    200: { #FF C8
        "abbreviation": "JPG",
        "name": "JPEG extension",
        "info": None
    },
    201: { #FF C9
        "abbreviation": "SOF9",
        "name": "Start Of Frame",
        "info": "Extended sequential DCT, arithmetic coding"
    },
    202: { #FF CA
        "abbreviation": "SOF10",
        "name": "Start Of Frame",
        "info": "Progressive DCT, arithmetic coding"
    },
    203: { #FF CB
        "abbreviation": "SOF11",
        "name": "Start Of Frame",
        "info": "Lossless (sequential), arithmetic coding"
    },
    204: { #FF CC
        "abbreviation": "DAC",
        "name": "Define Arithmetic Coding",
        "info": "Arithmetic coding definition"
    },
    205: { #FF CD
        "abbreviation": "SOF13",
        "name": "Start Of Frame",
        "info": "Differential sequential DCT"
    },
    206: { #FF CE
        "abbreviation": "SOF14",
        "name": "Start Of Frame",
        "info": "Differential progressive DCT"
    },
    207: { #FF CF
        "abbreviation": "SOF15",
        "name": "Start Of Frame",
        "info": "Differential lossless (sequential)"
    },
    208: { #FF D0
        "abbreviation": "RST0",
        "name": "Restart Marker 0",
        "info": None
    },
    209: { #FF D1
        "abbreviation": "RST1",
        "name": "Restart Marker 1",
        "info": None
    },
    210: { #FF D2
        "abbreviation": "RST2",
        "name": "Restart Marker 2",
        "info": None
    },
    211: { #FF D3
        "abbreviation": "RST3",
        "name": "Restart Marker 3",
        "info": None
    },
    212: { #FF D4
        "abbreviation": "RST4",
        "name": "Restart Marker 4",
        "info": None
    },
    213: { #FF D5
        "abbreviation": "RST5",
        "name": "Restart Marker 5",
        "info": None
    },
    214: { #FF D6
        "abbreviation": "RST6",
        "name": "Restart Marker 6",
        "info": None
    },
    215: { #FF D7
        "abbreviation": "RST7",
        "name": "Restart Marker 7",
        "info": None
    },
    216: { #FF D8
        "abbreviation": "SOI",
        "name": "Start Of Image",
        "info": "Magic Number"
    },
    217: { #FF D9
        "abbreviation": "EOI",
        "name": "End of Image",
        "info": "End of JPEG image data"
    },
    218: { #FF DA
        "abbreviation": "SOS",
        "name": "Start Of Scan",
        "info": "Image data segment"
    },
    219: { #FF DB
        "abbreviation": "DQT",
        "name": "Define Quantization Tables",
        "info": "Quantization table definitions"
    },
    220: { #FF DC
        "abbreviation": "DNL",
        "name": "Define Number of Lines",
        "info": None
    },
    221: { #FF DD
        "abbreviation": "DRI",
        "name": "Define Restart Interval",
        "info": None
    },
    222: { #FF DE
        "abbreviation": "DHP",
        "name": "Define Hierarchical Progression",
        "info": None
    },
    223: { #FF DF
        "abbreviation": "EXP",
        "name": "Expand Reference Component",
        "info": None
    },
    224: { #FF E0
        "abbreviation": "APP0",
        "name": "Application Segment 0",
        "info": "JFIF-Tag"
    },
    225: { #FF E1
        "abbreviation": "APP1",
        "name": "Application Segment 1",
        "info": "Commonly used for exif-data, thumbnails or Adobe XMP profiles"
    },
    226: { #FF E2
        "abbreviation": "APP2",
        "name": "Application Segment 2",
        "info": "Commonly used for ICC color profiles"
    },
    227: { #FF E3
        "abbreviation": "APP3",
        "name": "Application Segment 3",
        "info": "Commonly used as JPS-tag for stereoscopic JPEG images"
    },
    228: { #FF E4
        "abbreviation": "APP4",
        "name": "Application Segment 4",
        "info": None
    },
    229: { #FF E5
        "abbreviation": "APP5",
        "name": "Application Segment 5",
        "info": None
    },
    230: { #FF E6
        "abbreviation": "APP6",
        "name": "Application Segment 6",
        "info": "Commonly used for NITF lossles profiles"
    },
    231: { #FF E7
        "abbreviation": "APP7",
        "name": "Application Segment 7",
        "info": None
    },
    232: { #FF E8
        "abbreviation": "APP8",
        "name": "Application Segment 8",
        "info": None
    },
    233: { #FF E9
        "abbreviation": "APP9",
        "name": "Application Segment 9",
        "info": None
    },
    234: { #FF EA
        "abbreviation": "APP10",
        "name": "Application Segment 10",
        "info": "Commonly used to store ActiveObject"
    },
    235: { #FF EB
        "abbreviation": "APP11",
        "name": "Application Segment 11",
        "info": "Commonly used to store HELIOS JPEG resources (OPI Postscript)"
    },
    236: { #FF EC
        "abbreviation": "APP12",
        "name": "Application Segment 12",
        "info": "Commonly used by Photoshop to store Ducky tags or picture info"
    },
    237: { #FF ED
        "abbreviation": "APP13",
        "name": "Application Segment 13",
        "info": "Commonly used by Photoshop to store IRB, 8BIM or IPTC data"
    },
    238: { #FF EE
        "abbreviation": "APP14",
        "name": "Application Segment 14",
        "info": "Commonly used for copyright information"
    },
    239: { #FF EF
        "abbreviation": "APP15",
        "name": "Application Segment 15",
        "info": None
    },
    240: { #FF F0
        "abbreviation": "JPG0",
        "name": "JPEG Extension 0",
        "info": None
    },
    241: { #FF F1
        "abbreviation": "JPG1",
        "name": "JPEG Extension 1",
        "info": None
    },
    242: { #FF F2
        "abbreviation": "JPG2",
        "name": "JPEG Extension 2",
        "info": None
    },
    243: { #FF F3
        "abbreviation": "JPG3",
        "name": "JPEG Extension 3",
        "info": None
    },
    244: { #FF F4
        "abbreviation": "JPG4",
        "name": "JPEG Extension 4",
        "info": None
    },
    245: { #FF F5
        "abbreviation": "JPG5",
        "name": "JPEG Extension 5",
        "info": None
    },
    246: { #FF F6
        "abbreviation": "JPG6",
        "name": "JPEG Extension 6",
        "info": None
    },
    247: { #FF F7
        "abbreviation": "JPG7",
        "name": "JPEG Extension 7",
        "info": None
    },
    248: { #FF F8
        "abbreviation": "JPG8",
        "name": "JPEG Extension 8",
        "info": None
    },
    249: { #FF F9
        "abbreviation": "JPG9",
        "name": "JPEG Extension 9",
        "info": None
    },
    250: { #FF FA
        "abbreviation": "JPG10",
        "name": "JPEG Extension 10",
        "info": None
    },
    251: { #FF FB
        "abbreviation": "JPG11",
        "name": "JPEG Extension 11",
        "info": None
    },
    252: { #FF FC
        "abbreviation": "JPG12",
        "name": "JPEG Extension 12",
        "info": None
    },
    253: { #FF FD
        "abbreviation": "JPG13",
        "name": "JPEG Extension 13",
        "info": None
    },
    254: { #FF FE
        "abbreviation": "COM",
        "name": "Comments",
        "info": None
    }
}