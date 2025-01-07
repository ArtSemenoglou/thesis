from stockfish import Stockfish
import random
import chess
import time
import utilities

path_for_puzzles = "data_final/mate_in_3.txt"
original_path = utilities.get_path()
start=time.time()

stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish with the provided path
stockfish.set_elo_rating(3000)
stockfish.set_depth(10)
stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})

games_arr = utilities.load_puzzles(path_for_puzzles)
counter = 1

for game_dict in games_arr:
    print("puzzle number " + str(counter))
    original_fen = game_dict["fen"]
    temp_fen = game_dict["fen"]
    new_fen = game_dict["fen"]
    original_next_moves = game_dict["next_moves"]
    i = 0
    next_moves = original_next_moves
    while i < 64:
        board = chess.Board(new_fen)
        piece_map = board.piece_map()
        if i in piece_map:
            board.remove_piece_at(i)
            temp_fen = board.fen()
            if board.is_valid():
                stockfish.set_fen_position(temp_fen)
                temp_next_moves = []
                best_move_arr = stockfish.get_top_moves(1)
                while(best_move_arr):
                    stockfish.make_moves_from_current_position([best_move_arr[0]['Move']])
                    temp_next_moves.append(best_move_arr[0]['Move'])
                    if len(temp_next_moves) > 5:
                        break
                    best_move_arr = stockfish.get_top_moves(1)
                board = chess.Board(stockfish.get_fen_position())
                if (len(temp_next_moves) == 5 and board.is_checkmate()):
                    new_fen = temp_fen
                    next_moves = temp_next_moves
                    i = - 1
        i = i+1
    if original_fen != new_fen :
        utilities.register_puzzle([],next_moves,'data_final/mate_in_3_removed.txt',new_fen) # register the puzzle
    counter = counter + 1

print("Time to finish was "+ str((time.time()-start)/60) + "minutes")