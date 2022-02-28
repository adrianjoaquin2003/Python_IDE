from hash_dict import hash_dict


class Note:
    def __init__(self, path):
        self.path = path
        self._check_password = False


    #function hashes text file based on hash_dict
    def hash(self):


        #splits each word by character
        def split(word):
            return [char for char in word]

        character_sets = []

        with open(self.path, 'r+', encoding = "utf-8") as _f:
            #split the file by all words
            words = _f.read().split(" ")
            
            #split words by characters and add it to character sets list for encrypting / decrypting
            for i in range(len(words)):
                character_sets.append(split(words[i]))

            #hash all characters, leave if character is punctuation of whitespace
            for n in range(len(character_sets)):
                for m in range(len(character_sets[n])):
                    try:
                        character_sets[n][m] = hash_dict[character_sets[n][m]]
                    except KeyError:
                        continue

            #clear file and save
            _f.truncate(0)
            _f.close()

        #open in write mode to write encrypted file data
        with open(self.path, 'w', encoding = "utf-8",) as _f:

            hashed_words = []
            #put the second dimension of character_sets together as strings and store them in a list with spaces between
            for i in range(len(character_sets)):
                for j in range(len(character_sets[i])):
                    hashed_words.append(''.join(character_sets[i][j]))
                hashed_words.append(" ")

            #construct the final string by adding the elements of the hashed_words together as a string
            final_string = ""
            for i in range(len(hashed_words)):
                final_string = final_string + hashed_words[i]

            #write the final string to the file and save
            _f.write(final_string)
            _f.close()

   
    #allow access only if password is correct
    @property
    def check_password(self):
        #returns true if provided by the setter function
        return self._check_password

    #!!THIS RUNS BEFORE THE PROPERTY!! runs when check password is attempted to be set within the program
    @check_password.setter
    def check_password(self, val):
        #if set is supposed to be true ask for password
        if val:
            password = input("Password: ")
            #if password is correct return true to the property function
            if password == "none":
                print("ACCESS GRANTED\n")
                self._check_password = val
            else:
                exit(2)
