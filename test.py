import bcrypt

print(bcrypt.checkpw("abcdefgh".encode(), "$2b$12$XwK3/NHAP3inWg9jyBETxubWiAPkWQqiXjb6oSryBCOaSWBu0Z99S".encode()))