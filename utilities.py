from stockfish import Stockfish
import pathlib
import re
import json
import os.path

def get_path():
    original_path = str(pathlib.Path(__file__).parent.resolve())
    original_path = re.sub('code',"",original_path)
    original_path.replace("\\","/")
    return original_path

def get_games(): #load all the games
    f=open('data_v8/games_v1.txt','r') #file to load the games from
    data=f.read()
    f.close()
    data=data.split("@")
    for i in range(len(data)):
       moves=data[i].split(',')
       data[i]=moves
    print("games loaded:",len(data))
    return data

def check_valid_puzzle(game,indexes,fen=False): # check if the moves are the best available
    valid = True
    original_path = get_path()
    stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish
    stockfish.reset_engine_parameters()
    stockfish.set_elo_rating(3000)
    stockfish.set_depth(10)
    stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})

    if fen:
        stockfish.set_fen_position(fen)
    if indexes[0] > 0:
        stockfish.make_moves_from_current_position(game[:indexes[0]])
        
    for move in indexes:
        if len(game) > move:
            tempMoveArrDict = stockfish.get_top_moves(10)
            if tempMoveArrDict[0]['Move'] != game[move]:
                valid = False
                gameMoveDict = None
                for tempMoveDict in tempMoveArrDict:
                    if tempMoveDict['Move'] == game[move]:
                        gameMoveDict = tempMoveDict
                        break
                if gameMoveDict:
                    if ('Mate' in gameMoveDict.keys()) and ('Mate' in tempMoveArrDict[0].keys()):
                        if gameMoveDict['Mate'] == tempMoveArrDict[0]['Mate']:
                            valid = True
                if not valid:
                    break
            stockfish.make_moves_from_current_position([game[move]])
    return valid

def register_puzzle(played_moves,next_moves,file_path,fen=False): #save puzzles
    original_path = get_path()
    stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish
    if fen :
        stockfish.set_fen_position(fen)
    else:
        stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    stockfish.make_moves_from_current_position(played_moves)
    fen = stockfish.get_fen_position()
    puzzle = '{"fen": "'+ str(fen) + '" ,"next_moves": "' + str(next_moves) + '"}'
    f=open(file_path,'a')
    f.write(puzzle)
    f.close()


def get_score(fen): #get the score of the game
    dict = {"P": 1, "p": -1, "N": 3, "n": -3, "B": 3, "b": -3, "R": 5, "r": -5, "Q": 9, "q": -9}
    score = 0
    fen = fen.split(" ")[0]
    for i in fen:
        if ((not i.isdigit()) and(i not in "/kK")):
            score = score + dict[i]
    return score

def get_value(piece): #get the value of a piece
    dict = {"P": 1, "p": 1, "N": 3, "n": 3, "B": 3, "b": 3, "R": 5, "r": 5, "Q": 9, "q": 9, "K": 10000, "k": 10000}
    return dict[piece]

def remove_piece(fen,square): # removes a piece from the board. Not used currently
    dict = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}
    fen_arr = fen.split(' ')
    fen_arr_board = fen_arr[0].split("/")
    row = 8-int(square[1])
    col = dict[square[0]]
    row_arr = list(fen_arr_board[row])
    if col == 1 :
        if row_arr[1].isdigit():
            row_arr[1] = str(int(row_arr[1])+1)
            row_arr[0] = ""
        else:
            row_arr[0] = "1"
    else:
        count = 1
        for i in range(len(row_arr)):

            if count == col:
                if len(row_arr) > i+1:
                    if row_arr[i-1].isdigit() and row_arr[i+1].isdigit():
                        row_arr[i] = str(int(row_arr[i-1])+int(row_arr[i+1]) + 1)
                        row_arr[i-1] = ''
                        row_arr[i+1] = ''
                    elif row_arr[i-1].isdigit():
                        row_arr[i-1] = str(int(row_arr[i-1])+1)
                        row_arr[i] = ''
                    elif row_arr[i+1].isdigit():
                        row_arr[i+1] = str(int(row_arr[i+1])+1)
                        row_arr[i] = ''
                    else:
                        row_arr[i] = '1'
                else:
                    if row_arr[i-1].isdigit():
                        row_arr[i-1] = str(int(row_arr[i-1])+1)
                        row_arr[i] = ''
                    else:
                        row_arr[i] = '1'
                break

            if row_arr[i].isdigit():
                count = count + int(row_arr[i])
            else:
                count = count + 1

    fen_arr_board[row] = ''.join(row_arr)
    fen_arr_board = '/'.join(fen_arr_board)
    fen_arr[0] = fen_arr_board
    new_fen=' '.join(fen_arr)
    return new_fen


def load_puzzles(file_path):#loads all the available puzzles
    if(not os.path.isfile(file_path)):
        return False
    f = open(file_path,'r')
    data = f.read()
    data_arr = data.split('}')
    data_arr.pop()
    for i in range (len(data_arr)) :
        data_arr[i] = data_arr[i] + "}"
        data_arr[i] = json.loads(data_arr[i]) #convert to  string to dictionary
        #convert string to list 
        data_arr[i]["next_moves"].replace("\\","")
        data_arr[i]["next_moves"] = data_arr[i]["next_moves"].strip('][').replace("'",'').split(', ')
    print(len(data_arr),"puzzles loaded")
    f.close()
    return data_arr