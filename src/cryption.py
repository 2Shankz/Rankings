import ctypes
import re

# Load the DLL
libc = ctypes.cdll.LoadLibrary("./src/bisque/BisquseDLL.dll")

# Function type declarations
libc.CreateFromKey.argtypes = [ctypes.c_char_p]
libc.CreateFromKey.restype = ctypes.c_void_p
libc.Decrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
libc.Decrypt.restype = ctypes.c_int
libc.Encrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
libc.Encrypt.restype = ctypes.c_char_p
libc.ReleaseBuffer.argtypes = [ctypes.c_char_p]
libc.ReleaseInst.argtypes = [ctypes.c_void_p]
libc.DecryptNTY.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_bool]
libc.DecryptNTY.restype = ctypes.c_int

def create_from_key(key):
    """
    Return a pointer to a MD159 ("inst" used in all functions below)
    """
    try:
        return libc.CreateFromKey(key.encode('utf-8'))
    except Exception as e:
        print(f"Error in create_from_key: {e}")
        return None

def decrypt(key, data_to_decrypt):
    """
    Decrypt the given data using the provided key.
    """
    try:
        decrypted = ctypes.c_char_p()
        libc.Decrypt(key, data_to_decrypt.encode('utf-8'),  ctypes.byref(decrypted))
        
        return decrypted
    except Exception as e:
        print(f"Error in decrypt: {e}")
        return None
    finally:
        if decrypted:
            release_buffer(decrypted)

def encrypt(key, data_to_encrypt):
    """
    Encrypt the given data using the provided key.
    """
    try:
        data_to_encrypt_utf8 = data_to_encrypt.encode('utf-8')
        encrypted = libc.Encrypt(key, data_to_encrypt.encode('utf-8'), len(data_to_encrypt_utf8))
        return encrypted
    except Exception as e:
        print(f"Error in encrypt: {e}")
        return None

def release_buffer(buffer):
    """
    Release the buffer given by the Decrypt or Encrypt function.
    """
    try:
        libc.ReleaseBuffer(buffer)
    except Exception as e:
        print(f"Error in release_buffer: {e}")

def release_key(key):
    """
    Release an MD159 instance when it is no longer needed.
    """
    try:
        libc.ReleaseInst(key)
    except Exception as e:
        print(f"Error in release_key: {e}")

def nty_decryptor(key, filename, extension=None, is_text=True):
    """
    Decrypt an NTY file and save the decrypted data.
    """
    decrypted = None
    decryptedLength = -1  # reset

    try:
        with open(f"./{filename}", "rb") as file:
            encrypted = file.read()
        encryptedLength = len(encrypted)

        decrypted = ctypes.c_char_p(None)
        decryptedLength = libc.DecryptNTY(key, encrypted, encryptedLength, ctypes.byref(decrypted), is_text)

        print(f"[DEBUG] Decrypted Size: {decryptedLength}")

        if decryptedLength <= 0:
            print(f"Decryption Failed: {filename}")
            return None

        name = f"{filename}{extension}" if extension else filename
        output_file_path = f"./{name}"
        with open(output_file_path, "wb") as output_file:
            output_file.write(ctypes.string_at(decrypted, decryptedLength))

        return name
    
    except Exception as e:
        print(f"Error in nty_decryptor: {e}")
        return None
    
    finally:
        if decrypted:
            release_buffer(decrypted)

def extract_start_number(filename):
    """
    Extract 9000 from filename, such as character_face_9000_9099-2.nty.
    9000
    """
    match = re.search(r'character_face_(\d+)_\d+-', filename)
    if match:
        return int(match.group(1))
    return None

def remove_slice(data, start, end):
    return data[:start] + data[end:]

def find_signature_offsets(data, signature_bytes):
    """
    Return all offsets where the signature_bytes pattern appears within the binary.
    """
    positions = []
    i = 0
    while i <= len(data) - len(signature_bytes):
        if data[i:i+len(signature_bytes)] == signature_bytes:
            positions.append(i)
        i += 1
    return positions

def patch_block_size(full_block, size_diff):
    """
    Set 6-7 bytes of the full_block header to size_diff.
    """
    b = bytearray(full_block)
    size_bytes = size_diff.to_bytes(4, "big")
    b[4] = size_bytes[0]
    b[5] = size_bytes[1]
    b[6] = size_bytes[2]
    b[7] = size_bytes[3]
    return bytes(b)

def nty_decryptor_multi(key, filename, signature_hex, is_text=False):
    """
    Based on the signature_hex pattern in the NTY file,
    repeatedly extract while removing the 16 to Base_nth_image range.
    """
    decrypted = None
    decryptedLength = -1

    try:
        # 1️⃣ Open File
        with open(f"./{filename}", "rb") as file:
            encrypted = file.read()
        encryptedLength = len(encrypted)
        print(f"[DEBUG] Encrypted Size: {encryptedLength}")

        # 2️⃣ Signature Pattern Bytes
        signature_bytes = bytes.fromhex(signature_hex)

        # 3️⃣ Find Signature Location
        offsets = find_signature_offsets(encrypted, signature_bytes)
        if not offsets:
            print("❌ Signature not found.")
            return None

        print(f"✅ Discovered signature offsets: {offsets}")

        size_diffs = []
        for i in range(len(offsets) - 1):
            size_diffs.append(offsets[i+1] - offsets[i])

        # Estimating the size of the last block
        size_diffs.append(len(encrypted) - offsets[-1])
        print(f"✅ Block size estimate: {size_diffs}")

        # 5️⃣ Repeat processing
        start_num = extract_start_number(filename)
        if start_num is None:
            print(f"⚠️ Failed to extract start number from name. Using default value 0.")
            start_num = 0

        for idx, Base_nth_image in enumerate(offsets):
            print(f"\n⭐️ [{idx+1}] Base_nth_image offset = {Base_nth_image}")
            
            # 6️⃣ 16 ~ Remove Base_nth_image
            full_block = remove_slice(encrypted, 16, Base_nth_image)
            print(f"  ➜ full_block length (before patch): {len(full_block)}")

            # 7️⃣ Header size field patch
            size_diff = size_diffs[idx]
            full_block = patch_block_size(full_block, size_diff)
            print(f"  ➜ Patched size_diff: {size_diff}")
            
            # 8️⃣ Decrypt
            decrypted = ctypes.c_char_p(None)
            decryptedLength = libc.DecryptNTY(key, full_block, len(full_block), ctypes.byref(decrypted), is_text)
            print(f"  ➜ Decrypted size: {decryptedLength}")

            if decryptedLength <= 0:
                print("❌ Decryption failed")
                continue

            # 9️⃣ Save the result file
            final_number = start_num + (idx + 1)
            out_name = f"{filename}-{final_number}.png"
            output_file_path = out_name
            with open(output_file_path, "wb") as output_file:
                output_file.write(ctypes.string_at(decrypted, decryptedLength))

            #print(f"✅ Saving complete: {output_file_path}")

            # 1️⃣0️⃣ Release Buffer
            release_buffer(decrypted)

        print("\n✅ All images extracted!")

        return True

    except Exception as e:
        print(f"❌ Error in nty_decryptor_multi: {e}")
