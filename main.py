from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import struct

def decrypt_sql_server_blob(blob: bytes, aes_key: bytes) -> str:
  # KeyGUID: bytes 0-15 (pula)
  # Version: bytes 16-17 (pula)
  # Flags:   bytes 18-19 (pula)
  
  iv = blob[20:36]           # 16 bytes de IV
  encrypted_data = blob[36:] # 32 bytes — múltiplo de 16 ✅

  cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
  decryptor = cipher.decryptor()
  decrypted = decryptor.update(encrypted_data) + decryptor.finalize()

  # Parseia InnerMessage
  # MagicNumber(4) + IntegrityBytesLen(2) + PlaintextLen(2) + Plaintext
  import struct
  magic = struct.unpack_from('<I', decrypted, 0)[0]
  print(f"Magic number: {magic} (esperado: 3131961357)")

  integrity_len = struct.unpack_from('<H', decrypted, 4)[0]
  plaintext_len = struct.unpack_from('<H', decrypted, 6)[0]
  print(f"integrity_len={integrity_len}, plaintext_len={plaintext_len}")

  plaintext_start = 8 + integrity_len
  plaintext = decrypted[plaintext_start:plaintext_start + plaintext_len]

  # Tenta UTF-16-LE primeiro (nvarchar), depois UTF-8 (varchar)
  try:
    return plaintext.decode('utf-16-le')
  except:
    return plaintext.decode('utf-8')

# Uso:
import hashlib
aes_key = hashlib.sha256("MiskaMuskaMickeyMouse2026!".encode('utf-8')).digest()
blob = bytes.fromhex('00B19273DE8D7FCCFFFB2351312D1A530200000051E4C5BB7CD8FA84357FCE59DD70D2C0ADA621A2AF8917513EF81056F37ADD301BE082F12A2292B75C25DBC31F4ABCF4')

# texto = decrypt_sql_server_blob(blob, aes_key)
# print(texto)

# Testa se o magic number muda com chave diferente
chave_errada = bytes(16)  # 16 zeros, só pra testar
iv = blob[20:36]
encrypted_data = blob[36:]

cipher = Cipher(algorithms.AES(chave_errada), modes.CBC(iv))
dec = cipher.decryptor()
decrypted = dec.update(encrypted_data) + dec.finalize()

import struct
print(f"Magic com chave zeros: {struct.unpack_from('<I', decrypted, 0)[0]}")
print(f"Magic esperado:        3131961357")
print(f"\nSe magic != esperado = chave errada. Confirma!")