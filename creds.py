
def get_credentials():
    return get_data('./secrets.txt')

def get_data(file_name):
    result = {}
    with open(file_name) as file:
        for line in file:
            _l = line.split("=")
            result[_l[0]] = _l[1][0:-1] # removes /n for new line
    return result
def get_winning_block():
    with open("./winningblock.log") as file:
        result = []
        for line in file:
            result = line.split(":")
        return result
def write_winning_block(jackpot,morbtime):

    with open("./winningblock.log", 'w') as file:
       
            file.write(f"{jackpot}:{morbtime}")

def get_last_previous_block():
    return get_winning_block() 

def update_credentials():
    get_credentials()
