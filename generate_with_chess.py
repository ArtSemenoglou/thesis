from stockfish import Stockfish
import random
import chess
import time
import utilities

number_of_games = 100

#find the path of the folder
original_path = utilities.get_path()

#Global variables
board = chess.Board() # Creating a chess board object
total_games=0 # Counter for total number of games


#Main code
start=time.time()
stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish with the provided path
stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})
i=0 #counter for games that ended with a checkmate
while(i<number_of_games):
    board.reset() # Resetting the chess board
    flag = 0 # flag that checks if the game is stalemate
    stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") #reseting the board on stockfish
    moves = [] #the list that the moves are saved in
    
    # playes a random first move
    first_moves = stockfish.get_top_moves(20)
    next_move = first_moves[random.randint(0,19)]["Move"]
    moves.append(next_move)
    stockfish.make_moves_from_current_position([next_move])
    board.push(chess.Move.from_uci(next_move))

    # play the game
    stockfish.set_elo_rating(3000)

    #for the first 20 moves give a disadvantage to one of the players
    if(i%2==0):
        depth_White=6
        depth_Black=10
    else:
        depth_White=10
        depth_Black=6
    
    best_move_arr = stockfish.get_top_moves(2)
    while(best_move_arr): #while there is a legal move to be made
        if(len(moves)<20):
            if(len(moves)%2==0):
                stockfish.set_depth(depth_White)
            else:
                stockfish.set_depth(depth_Black)
            best_moves = stockfish.get_top_moves(5)
            next_move = best_moves[random.randint(0,len(best_moves)-1)]["Move"] #choose one move from the best five
        else:
            if(len(moves)==20): #reset the engine parameters
                stockfish.reset_engine_parameters()
                stockfish.set_elo_rating(3000)
                stockfish.set_depth(10)
                stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})
            next_move = best_move_arr[0]['Move']

            
        board.push(chess.Move.from_uci(next_move))

        #check if it's stalemate
        if(board.can_claim_threefold_repetition() or board.can_claim_fifty_moves() or board.is_insufficient_material()):
            #choose the second best move if it is not affecting the three last moves of the game

            if(len(best_move_arr)==2):
                if ('Mate' in best_move_arr[0].keys()) and ('Mate' in best_move_arr[1].keys()):
                    if (best_move_arr[0]['Mate'] is not None) and (best_move_arr[1]['Mate'] is not None):
                        if (abs(best_move_arr[0]['Mate']) <=3) or (abs(best_move_arr[1]['Mate']) <=3) : 
                            flag = 1
                            break  
                    elif (best_move_arr[0]['Mate'] is not None):
                        if (abs(best_move_arr[0]['Mate']) <=3): 
                            flag = 1
                            break  
                    elif (best_move_arr[1]['Mate'] is not None):
                        if (abs(best_move_arr[1]['Mate']) <=3): 
                            flag = 1
                            break  
            else:
                flag = 1
                break 

            board.pop()
            next_move = best_move_arr[1]["Move"]
            board.push(chess.Move.from_uci(next_move))
            if(board.can_claim_threefold_repetition() or board.can_claim_fifty_moves() or board.is_insufficient_material()): #if it's still a stalemate end the game
                moves.append(next_move)
                stockfish.make_moves_from_current_position([next_move])
                flag = 1
                break

        moves.append(next_move)
        stockfish.make_moves_from_current_position([next_move])
        best_move_arr = stockfish.get_top_moves(2)

#print result of the game and save it. if it's a checkmate save the puzzle too

    total_games+=1
    print("Game  finished ", total_games)

    if(flag ==0):
        i = i+1
        print("Completed games:", i, "\nNon draw ratio: ", i/total_games * 100,"number of moves",len(moves), "*******************************************\n\n")
        if(board.is_checkmate()):
            #save the game
            f=open('data_vtemp/games_v1.txt','a')
            f.write(",".join(moves))
            if i<number_of_games:
                f.write("@")
            f.close()
end=time.time()
print("Time that elapsed: ",(end - start)/60,"m" )
