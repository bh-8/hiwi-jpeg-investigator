import sys, getopt
from pathlib import Path
import json
import subprocess

#https://help.accusoft.com/ImageGear/v18.8/Linux/IGDLL-10-05.html
#https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
#info kategoriesieren: info, warnings, errors, (stego-signatures?)
#parameter zum extrahieren von spezifischen segment types, evtl. weitere parameter..
#https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/

return_code = 1
_exifFound = 0
_xmpFound = 0
_photoshopData = 0
_photoshopDetails = None
_iccFound = 0

SEGMENT_TYPE_DICT = {
    192: { #FF C0
        "segTypeId": "SOF0",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Baseline DCT"
    },
    193: { #FF C1
        "segTypeId": "SOF1",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Extended sequential DCT"
    },
    194: { #FF C2
        "segTypeId": "SOF2",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Progressive DCT"
    },
    195: { #FF C3
        "segTypeId": "SOF3",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Lossless (sequential)"
    },
    196: { #FF C4
        "segTypeId": "DHT",
        "segTypeName": "Define Huffman Table",
        "segTypeDesc": "Huffman Table Definition"
    },
    197: { #FF C5
        "segTypeId": "SOF5",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential sequential DCT"
    },
    198: { #FF C6
        "segTypeId": "SOF6",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential progressive DCT"
    },
    199: { #FF C7
        "segTypeId": "SOF7",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential lossless (sequential)"
    },
    200: { #FF C8
        "segTypeId": "JPG",
        "segTypeName": "JPEG extension",
        "segTypeDesc": None
    },
    201: { #FF C9
        "segTypeId": "SOF9",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Extended sequential DCT, arithmetic coding"
    },
    202: { #FF CA
        "segTypeId": "SOF10",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Progressive DCT, arithmetic coding"
    },
    203: { #FF CB
        "segTypeId": "SOF11",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Lossless (sequential), arithmetic coding"
    },
    204: { #FF CC
        "segTypeId": "DAC",
        "segTypeName": "Define Arithmetic Coding",
        "segTypeDesc": "Arithmetic coding definition"
    },
    205: { #FF CD
        "segTypeId": "SOF13",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential sequential DCT"
    },
    206: { #FF CE
        "segTypeId": "SOF14",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential progressive DCT"
    },
    207: { #FF CF
        "segTypeId": "SOF15",
        "segTypeName": "Start Of Frame",
        "segTypeDesc": "Differential lossless (sequential)"
    },
    208: { #FF D0
        "segTypeId": "RST0",
        "segTypeName": "Restart Marker 0",
        "segTypeDesc": None
    },
    209: { #FF D1
        "segTypeId": "RST1",
        "segTypeName": "Restart Marker 1",
        "segTypeDesc": None
    },
    210: { #FF D2
        "segTypeId": "RST2",
        "segTypeName": "Restart Marker 2",
        "segTypeDesc": None
    },
    211: { #FF D3
        "segTypeId": "RST3",
        "segTypeName": "Restart Marker 3",
        "segTypeDesc": None
    },
    212: { #FF D4
        "segTypeId": "RST4",
        "segTypeName": "Restart Marker 4",
        "segTypeDesc": None
    },
    213: { #FF D5
        "segTypeId": "RST5",
        "segTypeName": "Restart Marker 5",
        "segTypeDesc": None
    },
    214: { #FF D6
        "segTypeId": "RST6",
        "segTypeName": "Restart Marker 6",
        "segTypeDesc": None
    },
    215: { #FF D7
        "segTypeId": "RST7",
        "segTypeName": "Restart Marker 7",
        "segTypeDesc": None
    },
    216: { #FF D8
        "segTypeId": "SOI",
        "segTypeName": "Start Of Image",
        "segTypeDesc": "Magic Number"
    },
    217: { #FF D9
        "segTypeId": "EOI",
        "segTypeName": "End of Image",
        "segTypeDesc": "End of JPEG image data"
    },
    218: { #FF DA
        "segTypeId": "SOS",
        "segTypeName": "Start Of Scan",
        "segTypeDesc": "Image data segment"
    },
    219: { #FF DB
        "segTypeId": "DQT",
        "segTypeName": "Define Quantization Tables",
        "segTypeDesc": "Quantization table definitions"
    },
    220: { #FF DC
        "segTypeId": "DNL",
        "segTypeName": "Define Number of Lines",
        "segTypeDesc": None
    },
    221: { #FF DD
        "segTypeId": "DRI",
        "segTypeName": "Define Restart Interval",
        "segTypeDesc": None
    },
    222: { #FF DE
        "segTypeId": "DHP",
        "segTypeName": "Define Hierarchical Progression",
        "segTypeDesc": None
    },
    223: { #FF DF
        "segTypeId": "EXP",
        "segTypeName": "Expand Reference Component",
        "segTypeDesc": None
    },
    224: { #FF E0
        "segTypeId": "APP0",
        "segTypeName": "Application Segment 0",
        "segTypeDesc": "JFIF-Tag"
    },
    225: { #FF E1
        "segTypeId": "APP1",
        "segTypeName": "Application Segment 1",
        "segTypeDesc": "Exif-Data/Thumbnail/Adobe XMP"
    },
    226: { #FF E2
        "segTypeId": "APP2",
        "segTypeName": "Application Segment 2",
        "segTypeDesc": "ICC color profile"
    },
    227: { #FF E3
        "segTypeId": "APP3",
        "segTypeName": "Application Segment 3",
        "segTypeDesc": "JPS-Tag for stereoscopic JPEG images"
    },
    228: { #FF E4
        "segTypeId": "APP4",
        "segTypeName": "Application Segment 4",
        "segTypeDesc": None
    },
    229: { #FF E5
        "segTypeId": "APP5",
        "segTypeName": "Application Segment 5",
        "segTypeDesc": None
    },
    230: { #FF E6
        "segTypeId": "APP6",
        "segTypeName": "Application Segment 6",
        "segTypeDesc": "NITF Lossles profile"
    },
    231: { #FF E7
        "segTypeId": "APP7",
        "segTypeName": "Application Segment 7",
        "segTypeDesc": None
    },
    232: { #FF E8
        "segTypeId": "APP8",
        "segTypeName": "Application Segment 8",
        "segTypeDesc": None
    },
    233: { #FF E9
        "segTypeId": "APP9",
        "segTypeName": "Application Segment 9",
        "segTypeDesc": None
    },
    234: { #FF EA
        "segTypeId": "APP10",
        "segTypeName": "Application Segment 10",
        "segTypeDesc": "ActiveObject"
    },
    235: { #FF EB
        "segTypeId": "APP11",
        "segTypeName": "Application Segment 11",
        "segTypeDesc": "HELIOS JPEG Resources (OPI Postscript)"
    },
    236: { #FF EC
        "segTypeId": "APP12",
        "segTypeName": "Application Segment 12",
        "segTypeDesc": "Photoshop: Ducky Tags/Picture Info"
    },
    237: { #FF ED
        "segTypeId": "APP13",
        "segTypeName": "Application Segment 13",
        "segTypeDesc": "Photoshop: IRB, 8BIM, IPTC"
    },
    238: { #FF EE
        "segTypeId": "APP14",
        "segTypeName": "Application Segment 14",
        "segTypeDesc": "Copyright"
    },
    239: { #FF EF
        "segTypeId": "APP15",
        "segTypeName": "Application Segment 15",
        "segTypeDesc": None
    },
    240: { #FF F0
        "segTypeId": "JPG0",
        "segTypeName": "JPEG Extension 0",
        "segTypeDesc": None
    },
    241: { #FF F1
        "segTypeId": "JPG1",
        "segTypeName": "JPEG Extension 1",
        "segTypeDesc": None
    },
    242: { #FF F2
        "segTypeId": "JPG2",
        "segTypeName": "JPEG Extension 2",
        "segTypeDesc": None
    },
    243: { #FF F3
        "segTypeId": "JPG3",
        "segTypeName": "JPEG Extension 3",
        "segTypeDesc": None
    },
    244: { #FF F4
        "segTypeId": "JPG4",
        "segTypeName": "JPEG Extension 4",
        "segTypeDesc": None
    },
    245: { #FF F5
        "segTypeId": "JPG5",
        "segTypeName": "JPEG Extension 5",
        "segTypeDesc": None
    },
    246: { #FF F6
        "segTypeId": "JPG6",
        "segTypeName": "JPEG Extension 6",
        "segTypeDesc": None
    },
    247: { #FF F7
        "segTypeId": "JPG7",
        "segTypeName": "JPEG Extension 7",
        "segTypeDesc": None
    },
    248: { #FF F8
        "segTypeId": "JPG8",
        "segTypeName": "JPEG Extension 8",
        "segTypeDesc": None
    },
    249: { #FF F9
        "segTypeId": "JPG9",
        "segTypeName": "JPEG Extension 9",
        "segTypeDesc": None
    },
    250: { #FF FA
        "segTypeId": "JPG10",
        "segTypeName": "JPEG Extension 10",
        "segTypeDesc": None
    },
    251: { #FF FB
        "segTypeId": "JPG11",
        "segTypeName": "JPEG Extension 11",
        "segTypeDesc": None
    },
    252: { #FF FC
        "segTypeId": "JPG12",
        "segTypeName": "JPEG Extension 12",
        "segTypeDesc": None
    },
    253: { #FF FD
        "segTypeId": "JPG13",
        "segTypeName": "JPEG Extension 13",
        "segTypeDesc": None
    },
    254: { #FF FE
        "segTypeId": "COM",
        "segTypeName": "Comments",
        "segTypeDesc": None
    }
}

class IntegrityHandler:
    def __init__(self, dataToCover):
        self.dataToCover = dataToCover
        self.coverageList = []
        self.reportList = []
        self.eoiBroken = False
        self.app0found = False
    def setEoiBroken(self, state):
        self.eoiBroken = state
    def isEoiBroken(self):
        return self.eoiBroken
    def setApp0Found(self, state):
        self.app0found = state
    def isApp0Found(self):
        return self.app0found
    def addCoverage(self, p, pl, l):
        self.coverageList.append((p, pl + l))
    def addReport(self, rtType, rtSource, rtIdentifier, rtMessage):
        self.reportList.append({
            "type": rtType,     #report type
            "src": rtSource,    #report source
            "id": rtIdentifier, #report id
            "msg": rtMessage    #report message
        })
    def getUncoveredData(self, integrityHandler):
        uncoveredDataList = []

        t = 0
        tElement = 0
        while t < len(self.coverageList):
            tupel = self.coverageList[t]

            #check for gap
            if tElement != tupel[0]:
                #report segment
                _from = tElement
                _to = tupel[0]
                uncoveredDataList.append({
                    "region": (_from, _to),
                    "data": str(self.dataToCover[_from:_to])
                })

            tElement = tupel[1]
            t = t + 1

        #check if last is not eof yet
        if tElement != len(self.dataToCover):
            #get missing data to eof
            _from = tElement
            _to = len(self.dataToCover)
            _data = str(self.dataToCover[_from:_to])

            #check if last frame is actually broken
            if _from > _to:
                _from, _to = _to, _from
                _data = None
                integrityHandler.addReport("WARNING", "CoverageError", "LastSegmentBroken", f"Last segment is broken.")
            else:
                if not integrityHandler.isEoiBroken():
                    integrityHandler.addReport("WARNING", "CoverageError", "UnidentifiedDataAtEof", f"Found {_to - _from} unidentified bytes appended to the file.")

            #append last segment
            uncoveredDataList.append({
                "region": (_from, _to),
                "data": _data
            })
        return {
            "unidentified": uncoveredDataList,
            "data": self.coverageList
        }
    def getReportData(self):
        return self.reportList
    def hasErrors(self):
        from functools import reduce
        return reduce(lambda x, y: x and y, [i["type"] != "INFO" for i in self.reportList], False)

def printHelp():
    print("jpegheader.py -i <inputFile> -o <outputFile>")
def inBoundsCheck(imageData, index):
    return index >= 0 and index < len(imageData)
def getPayloadLength(imageData, payloadPosition):
    if not inBoundsCheck(imageData, payloadPosition) or not inBoundsCheck(imageData, payloadPosition + 1):
        return 0
    if imageData[payloadPosition] == 255:
        return 0
    
    s1 = imageData[payloadPosition]
    s2 = imageData[payloadPosition + 1]

    payloadLen = 256 * s1 + s2

    if payloadPosition + payloadLen > len(imageData):
        return len(imageData) - payloadPosition

    return payloadLen
def getPayloadData(imageData, payloadPosition, payloadLength):
    if payloadLength == 0:
        return b""
    return imageData[payloadPosition:payloadPosition + payloadLength]
def getSegmentHexId(imageData, searchPosition):
    if not inBoundsCheck(imageData, searchPosition + 1):
        return None
    return "0x" + str(imageData[searchPosition:searchPosition + 2])[2:10].replace("\\x", "")
def isExifSegment(imageData, position):
    return imageData[position + 2:position + 8] == b"Exif\x00\x00"
def isXMPProfile(imageData, position):
    return imageData[position + 2:position + 31] == b"XMP\x00://ns.adobe.com/xap/1.0/\x00"
def isICCProfile(imageData, position):
    return imageData[position + 2:position + 14] == b"ICC_PROFILE\x00"
def isPhotoshopSegment(imageData, position):
    return imageData[position + 2:position + 16] == b"Photoshop 3.0\x00"
def segmentIntegrityCheck(integrityHandler, n, intId, position, payloadLength, payloadData):
    #check if first segment is magic number
    if n == 0 and not (intId == 216 and position == 0):
        integrityHandler.addReport("ERROR", "SOISegment", "MagicNumberError", f"Magic Number could not be verified: Found {intId} on pos {position}, but expected 216 on pos 0!")
    
    match(intId):
        #TODO: add more integrity checks per segment type here
        case 219: #DQT
            #f5 signature
            if position == 20 and payloadLength == 132:
                if payloadData[82:132] == b"(" * 50:
                    integrityHandler.addReport("WARNING", "DQTSegment", "SuspiciousQuantizationTable", f"Found a suspicious quantization table, which indicates a 'f5'-manipulation!")
            #outguess signature
            if position == 89 and payloadLength == 67:
                if payloadData[17:67] == b"2" * 50:
                    integrityHandler.addReport("WARNING", "DQTSegment", "SuspiciousQuantizationTable", f"Found a suspicious quantization table, which indicates a 'outguess'-manipulation!")
        case 224: #APP0
            #jsteg signature
            integrityHandler.setApp0Found(True)
            if payloadLength != 16:
                integrityHandler.addReport("WARNING", "APP0Segment", "UnexpectedJFIFTagSize", f"JFIF tag should be 16 bytes long, but instead is {payloadLength}!")
        case _:
            pass

def parseMarkerSegments(imageData, integrityHandler):
    segmentList = []
    lastSegment = False
    searchOffset = 0
    n = 0

    nullSegmentPositions = [] #store positions of NullSegments (0xff00) aka. parsing errors

    while not lastSegment:
        #search for next FF appearance
        _searchPosition = imageData.find(b"\xff", searchOffset)

        #check if something was found
        if _searchPosition == -1:
            lastSegment = True
            continue

        #check if byte following searchPosition is still available
        if not inBoundsCheck(imageData, _searchPosition + 1):
            lastSegment = True
            continue
        
        #skip segments b"\xff\x00" and b"\xff\xff"
        if imageData[_searchPosition:_searchPosition + 2] == b"\xff\x00" or imageData[_searchPosition:_searchPosition + 2] == b"\xff\xff":
            nullSegmentPositions.append(_searchPosition)
            searchOffset = _searchPosition + 2
            continue

        #skip eoi marker
        if imageData[_searchPosition:_searchPosition + 2] == b"\xff\xd9":
            searchOffset = _searchPosition + 2
            integrityHandler.addCoverage(_searchPosition, _searchPosition + 2, 0)
            segmentList.append({
                "intId": imageData[_searchPosition + 1],
                "hexId": getSegmentHexId(imageData, _searchPosition),
                "markerPos": _searchPosition,
                "payloadPos": _searchPosition + 2,
                "payloadLength": 0,
                "segmentInfo": SEGMENT_TYPE_DICT.get(imageData[_searchPosition + 1], None)
            })
            continue

        _intId = imageData[_searchPosition + 1]
        _hexId = getSegmentHexId(imageData, _searchPosition)
        _payloadPosition = _searchPosition + 2
        _payloadLength = getPayloadLength(imageData, _payloadPosition)
        if _intId == 218: #SOS
            eoiPosition = imageData.find(b"\xff\xd9", _payloadPosition)
            if eoiPosition != -1:
                _payloadLength = eoiPosition - _payloadPosition
            else:
                integrityHandler.addReport("ERROR", "EOISegment", "EndOfImageNotFound", f"Could not find EOI segment after SOS marker, which indicates a potential 'jsteg'-manipulation.")
                integrityHandler.setEoiBroken(True)
        elif _intId == 225: #APP1 (XMP/Exif)
            if isExifSegment(imageData, _payloadPosition):
                global _exifFound
                _exifFound = _exifFound + 1
            elif isXMPProfile(imageData, _payloadPosition):
                endToken = b"<?xpacket end=\"w\"?>"
                xmpEnd = imageData.find(endToken, _payloadPosition)
                if xmpEnd > 0:
                    _payloadLength = xmpEnd + len(endToken) - _payloadPosition
                    global _xmpFound
                    _xmpFound = _xmpFound + 1
        elif _intId == 226: #APP2 (ICC)
            if isICCProfile(imageData, _payloadPosition):
                global _iccFound
                _iccFound = _iccFound + 1

                profile = imageData[_payloadPosition + 14:_payloadPosition + 16]
                _currentChunk = profile[0]
                _totalChunks = profile[1]

                if _currentChunk < _totalChunks:
                    #subtract maximum profile size if not last chunk
                    _payloadLength = 65535
        elif _intId == 237: #APP13 (IPTC/Photoshop)
            if isPhotoshopSegment(imageData, _payloadPosition):
                global _photoshopData, _photoshopDetails
                _photoshopData = _photoshopData + 1

                psSignaturePos = _payloadPosition + 16
                psSignatureText = imageData[psSignaturePos:psSignaturePos + 4].decode(errors = "ignore")

                _photoshopDetails = psSignatureText

                match(psSignatureText):
                    case "8BIM": #TODO: match different photoshop segments, see https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/
                        pass
                    case _:
                        pass
        integrityHandler.addCoverage(_searchPosition, _payloadPosition, _payloadLength)

        _payloadData = getPayloadData(imageData, _payloadPosition, _payloadLength)
        segmentIntegrityCheck(integrityHandler, n, _intId, _searchPosition, _payloadLength, _payloadData)

        dictEntry = SEGMENT_TYPE_DICT.get(_intId, "Unknown Segment Type")

        if str(dictEntry) == "Unknown Segment Type":
            integrityHandler.addReport("WARNING", "UnknownSegment", "UnknownSegmentType", f"Found unknown segment identifier {imageData[_searchPosition:_searchPosition + 2]} on pos {_searchPosition}!")
        else:
            if not (dictEntry["segTypeId"] == "SOS" or dictEntry["segTypeId"] == "SOI"):
                dictEntry["segPayloadData"] = str(_payloadData)

        segmentList.append({
            "intId": _intId,
            "hexId": _hexId,
            "markerPos": _searchPosition,
            "payloadPos": _payloadPosition,
            "payloadLength": _payloadLength,
            "segmentInfo": dictEntry
        })

        n = n + 1
        searchOffset = _payloadPosition + _payloadLength
    
    if len(nullSegmentPositions) != 0:
        integrityHandler.addReport("WARNING", "InvalidSegment", "InvalidSegmentsFound", f"Found 0xff00/0xffff on {len(nullSegmentPositions)} different positions; this should not happen on a valid jpeg file and is caused by parsing errors!")

    return segmentList
def jpegheader(infile, outfile):
    global return_code

    imageData = None
    markerSegments = None
    with open(infile, "rb") as f:
        imageData = f.read()
    unidentifiedData = None
    if imageData != None:
        integrityHandler = IntegrityHandler(imageData)

        markerSegments = parseMarkerSegments(imageData, integrityHandler)

        unidentifiedData = integrityHandler.getUncoveredData(integrityHandler)
        if len(unidentifiedData["unidentified"]) != 0:
            integrityHandler.addReport("WARNING", "CoverageError", "UnidentifiedData", f"Encountered {len(unidentifiedData['unidentified'])} unidentified data segments in file.")

        if not integrityHandler.isApp0Found():
            integrityHandler.addReport("WARNING", "APP0Segment", "JFIFTagNotFound", f"JFIF tag could not be found at expected position, which indicates a potential 'jsteg'-manipulation!")

    if not integrityHandler.hasErrors():
        return_code = 0
        integrityHandler.addReport("INFO", "JpegIntegrity", "AllOk", f"File seems to be valid.")

    global _exifFound, _xmpFound, _iccFound, _photoshopData, _photoshopDetails
    if _exifFound > 0:
        integrityHandler.addReport("INFO", "APP1Segment", "ExifInfo", f"Found exif data segment ({_exifFound}x).")
    if _xmpFound > 0:
        integrityHandler.addReport("INFO", "APP1Segment", "XMPProfile", f"Found xmp profile ({_xmpFound}x).")
    if _iccFound > 0:
        integrityHandler.addReport("INFO", "APP2Segment", "ICCProfile", f"Found icc profile ({_iccFound}x).")
    if _photoshopData > 0:
        integrityHandler.addReport("INFO", "APP13Segment", "PhotoshopData", f"Found Photoshop data ({_photoshopData}x): '{_photoshopDetails}'.")
    outfilePath = Path(outfile).resolve()

    #thumbnail extraction using exiftool
    exifexec = [
        "exiftool",
        "-a",
        "-b",
        "-W",
        f"{str(outfilePath.parent / outfilePath.stem)}.%t%c.%s",
        "-preview:all",
        str(infile)
    ]
    exifResultStr = subprocess.check_output(exifexec).strip(b"\x20\n").decode(errors = "ignore")#, stderr = subprocess.STDOUT)
    exifThumbnailNum = exifResultStr.split(" ")[0]
    print(exifResultStr)

    return_dict = {
        "file": Path(infile).name,
        "size": 0 if imageData == None else len(imageData),
        "generalInfo": integrityHandler.getReportData(),
        "markerSegments": markerSegments,
        "thumbnails": int(exifThumbnailNum),
        "unidentifiedData": unidentifiedData
    }
    return return_dict
def main(argv):
    global return_code
    inputfile = ""
    outputfile = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", [])
    except getopt.GetoptError:
        printHelp()
        sys.exit(99)
    for opt, arg in opts:
        if opt == "-h":
            printHelp()
            sys.exit(99)
        elif opt in ("-i"):
            inputfile = arg
        elif opt in ("-o"):
            outputfile = arg
    if len(inputfile) == 0 or len(outputfile) == 0:
        printHelp()
        sys.exit(99)

    print("Input file is:", inputfile)
    print("Output file is:", outputfile)
    
    outDict = jpegheader(inputfile, outputfile)

    #print("json:", json.dumps(outDict, indent = 4))

    with open(outputfile, "w") as f:
        json.dump(outDict, f)

    sys.exit(return_code)
if __name__ == "__main__":
   main(sys.argv[1:])
