from stockfish import Stockfish
import chess
import utilities
import time

start=time.time()

board = chess.Board()
counter = 0
counter_saved = 0
games_arr = utilities.load_puzzles("data_v7/mate_in_3_final.txt") #load the games
original_path = utilities.get_path()
stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish

for game_dict in games_arr: #for each game

    counter = counter+1
    print("game number:",counter)
    board.reset()
    fork_points = []
    board = chess.Board(game_dict["fen"])
    game = game_dict["next_moves"]

    for i in range(len(game)):
        #check if the move after this one(of the same color(i+2)) is a capture and if the starting square was the same as the target square of this move(i)
        if len(game)>= i+3:
            if game[i][2:4] == game[i+2][:2] : 
            #get all the moves from the target square and check if there are at least two possible captures
                
                #change fen to flip who is playing, so the player that made the i move is to make a move again 
                original_fen = board.fen()
                starting_score = utilities.get_score(original_fen) # get the score before the fork
                board.push(chess.Move.from_uci(game[i]))
                attacker_value = utilities.get_value(str(board.piece_at(chess.parse_square(game[i][2:4]))))
                temp_fen = board.fen().split(' ')
                if temp_fen[1]=='b':
                    temp_fen[1]='w'
                else:
                    temp_fen[1]='b'
                temp_fen=' '.join(temp_fen)

                #change who is playing
                board= chess.Board(temp_fen)

                if chess.Move.from_uci(game[i+2]) in board.legal_moves:
                    if board.is_capture(chess.Move.from_uci(game[i+2])):#if the target square of the i+2 move had an opponent piece from the i move
                        if attacker_value < utilities.get_value(str(board.piece_at(chess.parse_square(game[i+2][2:4])))): #the target piece is higher value than the attacking piece
                            
                            #save in the list move, the legal moves from the fork square

                            starting_square = game[i+2][:2]
                            moves =[]
                            list_moves= list(board.legal_moves)
                            for move in list_moves:
                                move_uci= move.uci()
                                if starting_square in move_uci:
                                    moves.append(move_uci)
                            
                            for move in moves:
                                #check if the legal move from fork square is also a capture
                                if (board.is_capture(chess.Move.from_uci(move))) and (game[i+2][:4] not in move) and (i not in fork_points): #game[i+2][:4] in case the move is a promotion
                                    if attacker_value < utilities.get_value(str(board.piece_at(chess.parse_square(move[2:4])))):#the target piece is higher value than the attacking piece
                                        stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                                        stockfish.make_moves_from_current_position(game[:i+4])
                                        after_fork_score = utilities.get_score(stockfish.get_fen_position()) #get the score after the fork
                                        #if the player gained an advantage add it to the fork points
                                        if " b" in original_fen:
                                            if after_fork_score < starting_score:
                                                fork_points.append(i)
                                        else:
                                            if after_fork_score > starting_score:
                                                fork_points.append(i)
            
                #reverse fen to the original
                board= chess.Board(original_fen)

        #play next move
        board.push(chess.Move.from_uci(game[i]))

    for fork in fork_points:
        if utilities.check_valid_puzzle(game,[fork,fork+1,fork+2,fork+3],game_dict["fen"]):#check if the moves were the best possible
            counter_saved = counter_saved + 1
            print("saving fork number:",counter_saved)
            utilities.register_puzzle(game[:fork],[game[fork],game[fork+1],game[fork+2]],'data_v7/fork_mate_3.txt')#register the puzzle

end=time.time()
print("Time that elapsed: ",(end - start),"s" )

