import pickle, random

valid_password_chars = tuple(range(32, 34)) + tuple(range(35, 39)) + tuple(range(40, 127)) # the ascii values of all valid characters that can be used in password (excludes ', ", and non-typeable characters)


def generatePassword():
    random_password = ""
    while True:
        random_password = "".join(chr(random.choice(valid_password_chars)) for i in range(20))
        has_lower = has_upper = has_digit = has_symbol = False
        for c in random_password:
            if c.islower():
                has_lower = True
            elif c.isupper():
                has_upper = True
            elif c.isdigit():
                has_digit = True
            elif ord(c) < 48 or ord(c) > 122:
                has_symbol = True
                
            if has_lower and has_upper and has_digit and has_symbol:
                return random_password

def generateKeyPattern():
    """
    Function to generate the sequence of integers used in modifying the characters in strings to be encrypted/decrypted.
    The sequence of integers is stored in a pickle file.
    
    No return value
    
    """
    
    sequence = tuple(random.randint(0, len(valid_password_chars)) for i in range(20))
    seq_file = open("seq.p", "wb")
    pickle.dump(sequence, seq_file)
    seq_file.close()

def encryptCharacter(character, offset):
    """
    Encrypts a character in a string by shifting its valid ascii bit value by the specified offset.
    If shifting by the offset exceeds the value allowed by ascii-valid characters, then decrease the value to "loop back" to the valid range of ascii characters.
    
    Returns the character after being encrypted
    
    """
    
    index = valid_password_chars.index(ord(character))
    if index + offset >= len(valid_password_chars):
        return chr(valid_password_chars[index + offset - len(valid_password_chars)])
    else:
        return chr(valid_password_chars[index + offset])

def decryptCharacter(character, offset):
    """
    Decrypts a character in a string by shifting its valid ascii bit value by the specified offset.
    If shifting by the offset exceeds the value allowed by ascii-valid characters, then increase the value to "loop back" to the valid range of ascii characters.
    
    Returns the character after being decrypted
    
    """
    
    index = valid_password_chars.index(ord(character))
    if index - offset < 0:
        return chr(valid_password_chars[index - offset + len(valid_password_chars)])
    else:
        return chr(valid_password_chars[index - offset])

def encrypt(message):
    """
    Function to encrypt the specified message in preparation for storing it in the database
    
    Returns the encrypted string
    
    """
    
    try: # check if there is a pickle file that has stored the integer sequence used for encryption/decryption, otherwise we have to create one
        seq_file = open("seq.p", "rb")
        sequence = pickle.load(seq_file)
        seq_file.close()
    except FileNotFoundError: # there is no sequence stored, which means we need to create one
        generateKeyPattern()
        seq_file = open("seq.p", "rb")
        sequence = pickle.load(seq_file)
        seq_file.close()
    
    message_enc = "" # the encrypted message to be returned
    count = 0 # keeps track of which integer in the sequence to use as an offset
    
    # iterate through every character in the inputted message; we will encrypt each character by changing its unicode value by the given offset
    for c in message:
        offset = sequence[count % 20]
        message_enc += encryptCharacter(c, offset)
        count += 1
    
    return message_enc

def decrypt(message):
    """
    Function to decrypt the specified message
    
    Returns the decrypted string
    
    """
    
    # first, we read the sequence of integers stored in the pickle file back when we initiated encryption (this will never run before encryption has occurred)
    seq_file = open("seq.p", "rb")
    sequence = pickle.load(seq_file)
    seq_file.close()
    
    message_dec = "" # the decrypted message to be returned
    count = 0 # keeps track of which integer in the sequence to use as an offset
    
    # iterate through every character in the inputted message; we will decrypt each character by changing its unicode value by the given offset
    for c in message:
        offset = sequence[count % 20]
        message_dec += decryptCharacter(c, offset)
        count += 1
    
    return message_dec