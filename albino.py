import utilities
from stockfish import Stockfish
import time 
import chess


start=time.time()
original_path = utilities.get_path()
stockfish = Stockfish(path= original_path + 'stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe') #initialize stockfish
stockfish.set_elo_rating(3000)
stockfish.set_depth(10)
stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})

def is_necessary(fen,original_move,starting_square,game):
    board = chess.Board(fen)
    stockfish.set_fen_position(fen)
    legal_moves_list = list(board.legal_moves)
    moves_with_pawn = []
    for move in legal_moves_list:
        temp_move = board.uci(move)
        if stockfish.is_move_correct(temp_move) and temp_move != original_move and temp_move[:2] == starting_square:
            moves_with_pawn.append(temp_move)

    for alt_move in moves_with_pawn:
        stockfish.set_fen_position(fen)
        if stockfish.is_move_correct(alt_move):
            stockfish.make_moves_from_current_position([alt_move])
            best_moves_arr = stockfish.get_top_moves(1)
            temp_moves = [alt_move]
            while best_moves_arr :
                temp_moves.append(best_moves_arr[0]["Move"])
                stockfish.make_moves_from_current_position([best_moves_arr[0]["Move"]])
                if len(temp_moves) + 1 > len(game):
                    break
                best_moves_arr = stockfish.get_top_moves(1)
            board = chess.Board(stockfish.get_fen_position())
            if temp_moves:
                if ((len(temp_moves) + 1 <= len(game)) and board.is_checkmate() and (" b" in stockfish.get_fen_position())):
                    return False
    return True

def all_available_moves(fen):
    stockfish.set_fen_position(fen)
    board = chess.Board(fen)
    valid_moves = []
    legal_moves_list = list(board.legal_moves)
    for move in legal_moves_list:
        temp_move = board.uci(move)
        if stockfish.is_move_correct(temp_move):
            valid_moves.append(temp_move)
    return valid_moves

def determine_move(move):
    if move[0] == move[2]:
        if abs(int(move[1]) - int(move[3])) == 1:
            return "forward_one"
        elif abs(int(move[1]) - int(move[3])) == 2:
            return "forward_two"
        else:
            return "error"
    elif move[0] < move[2]:
        if abs(int(move[1]) - int(move[3])) == 1:
            return "capture_right"
        else:
            return "error"
    elif move[0] > move[2]:
        if abs(int(move[1]) - int(move[3])) == 1:
            return "capture_left"
        else:
            return "error"    
    else:
        return "error"

def albino_tries(fen):
    second_row = ["a2","b2","c2","d2","e2","f2","g2","h2"]
    stockfish.set_fen_position(fen)
    for square in second_row[1:-1]:
        if (stockfish.get_what_is_on_square(square) is Stockfish.Piece.WHITE_PAWN) :
            starting_square = square[:2]
            forward_one = starting_square + square[0] + "3"
            forward_two = starting_square + square[0] + "4"
            left_col = second_row[second_row.index(starting_square) - 1][0]
            right_col = second_row[second_row.index(starting_square) + 1][0]            
            capture_left = starting_square + left_col + "3"
            capture_right = starting_square + right_col + "3"
            if stockfish.is_move_correct(forward_one) and stockfish.is_move_correct(forward_two) and stockfish.is_move_correct(capture_left) and stockfish.is_move_correct(capture_right):
                return [forward_one,forward_two,capture_left,capture_right]
    return False


def play_all_possible_games(original_fen,original_starting_square):
    alt_games =  []
    best_moves_arr = all_available_moves(original_fen)
    stockfish.set_fen_position(original_fen)
    best_moves_stockfish = stockfish.get_top_moves()
    temp_arr = []
    for move in best_moves_stockfish:
        if move["Move"] in best_moves_arr:
            best_moves_arr.remove(move["Move"])
        temp_arr.append(move["Move"])
    best_moves_arr = temp_arr + best_moves_arr
    
    for i in range(len(best_moves_arr)):
        moves = []
        temp_best_moves_arr = [{'Move': best_moves_arr[i]}]
        stockfish.set_fen_position(original_fen)
        valid = True
        while(temp_best_moves_arr and len(moves) < 6 ):
            best_move = temp_best_moves_arr[0]['Move']
            if len(moves) == 1:
                starting_square = best_move[:2]
                if not ((stockfish.get_what_is_on_square(starting_square) is Stockfish.Piece.WHITE_PAWN) and (original_starting_square == starting_square )): 
                    valid = False
                    break
                before_pawn_move_fen = stockfish.get_fen_position()
            stockfish.make_moves_from_current_position([best_move])
            moves.append(best_move)
            temp_best_moves_arr = stockfish.get_top_moves()
        temp_fen = stockfish.get_fen_position()
        board = chess.Board(temp_fen)
        if (valid and board.is_checkmate() and (" b" in temp_fen)):
            if is_necessary(before_pawn_move_fen,moves[1],starting_square,moves):
                alt_games.append(moves)
    return alt_games


def is_Albino(original_fen,moves):
    stockfish.set_fen_position(original_fen)
    tries_result = albino_tries(original_fen)
    albino_dict = {"original_fen": original_fen, "forward_one": False, "forward_two": False, "capture_left": False, "capture_right": False}
    if tries_result:
        for i in range(4):
            stockfish.set_fen_position(original_fen)
            stockfish.make_moves_from_current_position([tries_result[i]])
            counter_move_arr = stockfish.get_top_moves(1)
            if counter_move_arr:
                tries_result[i] = [tries_result[i],counter_move_arr[0]['Move']]
        return {"type": "tries", "fen": original_fen, "forward_one": tries_result[0], "forward_two": tries_result[1], "capture_left": tries_result[2], "capture_right": tries_result[3]}
        
    for i in range(len(moves)):
        if i == 0:
            fen_prev = original_fen
        else: 
            starting_square = moves[i][:2]
            if starting_square[1] == "2":
                if ((stockfish.get_what_is_on_square(starting_square) is Stockfish.Piece.WHITE_PAWN) and (len(moves[i:])%2 == 1)) :
                    kind_of_move = determine_move(moves[i])
                    if kind_of_move in albino_dict.keys():
                        possible_moves = 1
                        albino_dict[kind_of_move] = moves[i-1:]
                        alt_games_arr = play_all_possible_games(fen_prev,starting_square)
                        stockfish.set_fen_position(fen_cur)
                        for alt_game in alt_games_arr:
                            if len(alt_game) > 1:
                                kind_of_move = determine_move(alt_game[1])
                                if kind_of_move in albino_dict.keys():
                                    if albino_dict[kind_of_move] == False:
                                        albino_dict[kind_of_move] = alt_game
                                        possible_moves = possible_moves + 1
                                if possible_moves == 4:
                                    albino_dict["fen"] = fen_prev
                                    return albino_dict
            tries_result = albino_tries(fen_cur)
            if tries_result:
                for i in range(4):
                    stockfish.set_fen_position(fen_cur)
                    stockfish.make_moves_from_current_position([tries_result[i]])
                    counter_move_arr = stockfish.get_top_moves(1)
                    if counter_move_arr:
                        tries_result[i] = [tries_result[i],counter_move_arr[0]['Move']]
                return {"type": "tries", "fen": fen_cur, "forward_one": tries_result[0], "forward_two": tries_result[1], "capture_left": tries_result[2], "capture_right": tries_result[3]}
            fen_prev = stockfish.get_fen_position()            
        stockfish.make_moves_from_current_position([moves[i]])
        fen_cur = stockfish.get_fen_position()
    return False

def test_custom_game():
    valid = False
    while(not valid):
        fen = input("Type fen to check:\n")
        if(stockfish.is_fen_valid(fen)):
            valid = True
        else:
            print("Fen is not valid. Try again.\n")
    valid = False

    while(not valid):
        valid = True
        in_moves = input("Type the next moves up until the first pawn move, separated with commas.\nYou can leave it blank if you are only looking for tries:\n")
        in_moves_arr = in_moves.split(",")
        stockfish.set_fen_position(fen)
        for move in in_moves_arr:
            if stockfish.is_move_correct(move.strip()):
                stockfish.make_moves_from_current_position([move.strip()])
            else:
                valid = False
                print("Move " + move +" not valid. Try again!\n")
                break
    print("Working....")
    for i in range(len(in_moves_arr)):
        in_moves_arr[i] = in_moves_arr[i].strip()

    result = is_Albino(fen,in_moves_arr)
    if result:
        print("It is an Albino!\n")
        print(result)
        print("\n")
    else:
        print("It is not an Albino\n")

def test_saved_games():
    counter = 0
    counter_saved = 0
    games_arr = utilities.load_puzzles("data_final/mate_in_3.txt") #load the games

    for game_dict in games_arr: #for each game

        counter = counter+1
        print("game number:",counter)
        fen = game_dict["fen"]
        game = game_dict["next_moves"]
        result = is_Albino(fen,game)
        if result:
            file_path = 'data_final/Albino.txt'
            f=open(file_path,'a')
            f.write(str(result))
            f.close()
            counter_saved = counter_saved + 1
            print("saving game number ", counter_saved)

while(True):
    choice = input("\n1. Test saved games\n2. Test custom game\n3. Exit\nChoose what to test: \n")
    if choice == '1' :
        test_saved_games()
    elif choice == '2':
        test_custom_game()
    elif choice == '3':
        break
    else:
        print("Wrong input!")
print("Goodbye!\n")



#8/8/1Q6/8/k1b5/N4R2/2P5/3B3K w - - 0 41
#a3b1,c4b3,c2b3


#8/K3RbpP/4pN1R/2B1k3/6Qp/2Nr1n2/3nP3/1B1r4 w - - 0 41
