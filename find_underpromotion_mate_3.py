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


def test_necessity(original_fen,moves):
    stockfish.set_fen_position(original_fen)
    if " b" in original_fen:
        player_color = "black"
    else:
        player_color = "white"    
    if len(moves[0]) == 5:
        new_move = moves[0][:4] + 'q'
        if stockfish.is_move_correct(new_move):
            temp_moves = []
            best_moves_arr = [{'Move': new_move}]
            while best_moves_arr:
                temp_moves.append(best_moves_arr[0]['Move'])
                stockfish.make_moves_from_current_position([best_moves_arr[0]['Move']])
                best_moves_arr = stockfish.get_top_moves(1)
                if len(moves) < len(temp_moves):
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


games_arr = utilities.load_puzzles("data_v7/mate_in_3_final.txt") #load the games
for game_dict in games_arr: #for each game

    original_fen = game_dict["fen"]
    game = game_dict["next_moves"]

    for i in range(len(game)):
        if len(game[i]) == 5 : # if the move is a promotion 
            if game[i][4] != 'q': #and the promotion is not to a queen
                #make the promotion to a queen and check if the outcome was the same or better from the underpromotion
                stockfish.set_fen_position(original_fen)
                stockfish.make_moves_from_current_position(game[:i])
                fen = stockfish.get_fen_position()
                next_moves = game[i:]

                if test_necessity(fen,next_moves): # if the outcome is better with the underpromotion save the puzzle
                    if len(next_moves) == 5:
                        utilities.register_puzzle(game[:i],next_moves,'data_v7/underpromotion_mate_3.txt',game_dict["fen"])
                    elif len(next_moves) == 3:
                        utilities.register_puzzle(game[:i],next_moves,'data_v7/underpromotion_mate_2.txt',game_dict["fen"])
                    print('found one')
end=time.time()
print('Time that elapsed: ',(end - start),'s' )