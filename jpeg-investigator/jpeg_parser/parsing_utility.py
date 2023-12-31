EXIF_SIGNATURE = b"Exif\x00\x00"
XMPPROFILE_SIGNATURE = b"XMP\x00://ns.adobe.com/xap/1.0/\x00"
ICCPROFILE_SIGNATURE = b"ICC_PROFILE\x00"
PHOTOSHOP_SIGNATURE = b"Photoshop 3.0\x00"

def check_signature(signature: str):
    return lambda b, p : b[p + 2:p + 2 + len(signature)] == signature

def check_exif_signature(jpeg_bytes: bytes, payload_position: int) -> bool:
    return check_signature(EXIF_SIGNATURE)(jpeg_bytes, payload_position)

def check_xmp_profile_signature(jpeg_bytes: bytes, payload_position: int) -> bool:
    return check_signature(XMPPROFILE_SIGNATURE)(jpeg_bytes, payload_position)

def check_icc_profile_signature(jpeg_bytes: bytes, payload_position: int) -> bool:
    return check_signature(ICCPROFILE_SIGNATURE)(jpeg_bytes, payload_position)

def check_photoshop_signature(jpeg_bytes: bytes, payload_position: int) -> bool:
    return check_signature(PHOTOSHOP_SIGNATURE)(jpeg_bytes, payload_position)

def calculate_default_payload_length(jpeg_bytes: bytes, payload_position: int) -> int:
    if not payload_position + 1 < len(jpeg_bytes):
        return 0
    calculated_length = 256 * jpeg_bytes[payload_position] + jpeg_bytes[payload_position + 1]
    if payload_position + calculated_length > len(jpeg_bytes):
        return len(jpeg_bytes) - payload_position
    return calculated_length

def extract_segment_header(jpeg_bytes: bytes, ff_position: int, default_length_info: bool = True) -> bytes:
    return jpeg_bytes[ff_position:ff_position + 2 + (2 if default_length_info else 0)]

def extract_payload_data(jpeg_bytes: bytes, ff_position: int, payload_length: int) -> bytes:
    return jpeg_bytes[ff_position + 2:ff_position + 2 + payload_length]
