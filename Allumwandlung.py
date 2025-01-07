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


def test_necessity(original_fen,moves,player_color):
    stockfish.set_fen_position(original_fen)
    for i in range(len(moves)):
        if len(moves[i]) == 5:
            if moves[i][4] == "q":
                return True
            else:
                break
        else:
            stockfish.make_moves_from_current_position([moves[i]])
    if len(moves[i]) == 5:
        new_move = moves[i][:4] + 'q'
        if stockfish.is_move_correct(new_move):
            temp_moves = []
            best_moves_arr = [{'Move': new_move}]
            while best_moves_arr:
                temp_moves.append(best_moves_arr[0]['Move'])
                stockfish.make_moves_from_current_position([best_moves_arr[0]['Move']])
                best_moves_arr = stockfish.get_top_moves(1)
                if len(moves) < len(temp_moves) + i:
                    return True
            board = chess.Board(stockfish.get_fen_position())
            if board.is_checkmate():
                if (player_color == "white" and " b" in board.fen()) or (player_color == "black" and " w" in board.fen()):
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True
    else:
        return False


def play_all_possible_games(original_fen,player_color):
    alt_games =  []
    stockfish.set_fen_position(original_fen)

    best_moves_arr = stockfish.get_top_moves()
    for i in range(len(best_moves_arr)):
        moves = []
        temp_best_moves_arr = [best_moves_arr[i]]
        stockfish.set_fen_position(original_fen)
        while(temp_best_moves_arr and len(moves) < 6 ):
            if len(moves) == 5:
                moves.append("fail")
                break
            best_move = temp_best_moves_arr[0]['Move']
            stockfish.make_moves_from_current_position([best_move])
            moves.append(best_move)
            temp_best_moves_arr = stockfish.get_top_moves()
        if len(moves) < 6 and test_necessity(original_fen,moves,player_color):
            alt_games.append(moves)
    return alt_games

def is_Allumwandlung(fen,game):
    promotions_dict = {"original_fen": fen,"q": False,"r": False,"b": False,"n": False}
    stockfish.set_fen_position(fen)
    for i in range(len(game)):
        move = game[i]
        if i == 0:
            fen_prev = fen
        else: 
            if len(move) > 4:
                possible_promotions = 0
                if " b" in fen_cur:
                    player_color = "black"
                else:
                    player_color = "white"
                alt_games_arr = play_all_possible_games(fen_prev,player_color)
                stockfish.set_fen_position(fen_cur)
                for alt_game in alt_games_arr:     
                    if len(alt_game[1]) == 5:
                        if alt_game[1][4] in promotions_dict.keys():
                            if promotions_dict[alt_game[1][4]] == False:
                                promotions_dict[alt_game[1][4]] = alt_game
                                possible_promotions = possible_promotions + 1
                    if possible_promotions == 4:
                        promotions_dict["fen"] = fen_prev
                        return promotions_dict
            fen_prev = stockfish.get_fen_position()
        stockfish.make_moves_from_current_position([move])
        fen_cur = stockfish.get_fen_position()
    return False

def test_saved_games():
    counter = 0
    counter_saved = 0
    games_arr = utilities.load_puzzles("data_final/mate_in_3.txt") #load the games

    for game_dict in games_arr: #for each game

        counter = counter+1
        print("game number:",counter)
        fen = game_dict["fen"]
        game = game_dict["next_moves"]
        result = is_Allumwandlung(fen,game)
        if result:
            file_path = 'data_final/Allumwandlung.txt'
            f=open(file_path,'a')
            f.write(str(result))
            f.close()
            counter_saved = counter_saved + 1
            print("saving game number ", counter_saved)


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
        in_moves = input("Type the next moves up until the promotion, separated with commas:\n")
        in_moves_arr = in_moves.split(",")
        stockfish.set_fen_position(fen)
        for move in in_moves_arr:
            if stockfish.is_move_correct(move.strip()):
                stockfish.make_moves_from_current_position([move.strip()])
            else:
                valid = False
                print("Move " + move +" not valid. Try again!\n")
                break
    for i in range(len(in_moves_arr)):
        in_moves_arr[i] = in_moves_arr[i].strip()

    result = is_Allumwandlung(fen,in_moves_arr)
    if result:
        print("It is an Allumwandlung!\n")
        print(result)
        print("\n")
    else:
        print("It is not an Allumwandlung\n")
    

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

#8/R7/4kPP1/3ppp2/3B1P2/1K1P1P2/8/8 w - - 0 68
#f6f7,e5e4,f7f8q