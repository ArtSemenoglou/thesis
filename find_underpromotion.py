import utilities
from stockfish import Stockfish
import time 
import chess

start=time.time()
original_path = utilities.get_path()
stockfish = Stockfish(path= original_path + 'stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe') #initialize stockfish
stockfish.set_elo_rating(3000)
stockfish.set_depth(10)
# stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})

def test_necessity(original_fen,moves):
    stockfish.set_fen_position(original_fen)
    if len(moves[0]) == 5:
        if " b" in original_fen:
            player_color = "black"
        else:
            player_color = "white"
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


data_arr = utilities.get_games() #get games
for game in data_arr: #for each game
    for i in range(len(game)):
        if len(game[i]) == 5 : # if the move is a promotion 
            if game[i][4] != 'q': #and the promotion is not to a queen
                moves = [i,i+1,i+2]
                if utilities.check_valid_puzzle(game,moves): #if the moves made are the best available

                    #make the promotion to a queen and check if the outcome was the same or better from the underpromotion
                    stockfish.set_fen_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
                    stockfish.make_moves_from_current_position(game[:i])
                    fen = stockfish.get_fen_position()
                    

                    if test_necessity(fen,game[i:]): # if the outcome is better with the underpromotion save the puzzle
                        next_moves = []
                        for move in moves:
                            if len(game)> move:
                                next_moves.append(game[move])
                        utilities.register_puzzle(game[:i],next_moves,'data_v7/underpromotion_general.txt')
                        print('found one')
end=time.time()
print('Time that elapsed: ',(end - start)/60,'m' )