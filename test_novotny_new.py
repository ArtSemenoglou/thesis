import utilities
import time
from stockfish import Stockfish
import chess


original_path = utilities.get_path()
stockfish = Stockfish(path= original_path + "stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish

def make_alternative_move(sacrifice_move,alternative_move,fen):
    # input: the sacrifice move, the move that was not played by opponent,and the starting fen
    # output: if the move is legal(it's not a pinned piece that moves for example), return the moves of the alternative game. else return False 
    
    new_game = [sacrifice_move,alternative_move]
    stockfish.set_fen_position(fen)
    stockfish.make_moves_from_current_position([sacrifice_move])
    if stockfish.is_move_correct(alternative_move):
        stockfish.make_moves_from_current_position([alternative_move])
        best_move = stockfish.get_top_moves(1)[0]['Move']
        while best_move:
            new_game.append(best_move)
            stockfish.make_moves_from_current_position([best_move])
            best_move_arr = stockfish.get_top_moves(1)
            if not best_move_arr:
                break
            best_move = best_move_arr[0]['Move']
        stockfish.set_fen_position(fen)
        return new_game
    else:
        return False
    
def play_from_fen(sacrifice_move,alternative_move,fen):
    #The same with make alternative_move but without checking if the move is correct because we know the correct move
    stockfish.set_elo_rating(3000)
    
    new_game = [sacrifice_move,alternative_move]
    stockfish.make_moves_from_current_position(new_game)
    best_move = stockfish.get_top_moves(1)[0]['Move']
    while best_move:
        new_game.append(best_move)
        stockfish.make_moves_from_current_position([best_move])
        best_move_arr = stockfish.get_top_moves(1)
        if not best_move_arr:
            break
        best_move = best_move_arr[0]['Move']
    stockfish.set_fen_position(fen)
    return new_game



def is_novotny(game,i,board,starting_fen,second_attacker,attacker_color,first_time=True):
    #input: list of the moves, index of the move to check if it's the sacrifice one, the fen before the move, the attacker that is not capturing in the next move, the color of the side capturing the sacrifice, an optional variable to check if the function was called from the same function(is_novotny) or from the main program
    #output: True if it is novotny starting from the sacrifice in the i move. False if it is not
    reset_fen = board.fen()
    board = chess.Board(starting_fen)#set fen before the sacrifice move(i)
    second_moves = board.attacks(chess.parse_square(second_attacker))#returns the available moves of the second attacker before the sacrifice move
    board = chess.Board(reset_fen)# set fen to the one after the sacrifice move was played(i move)

    if(len(game)<i+3):
        return False
    #if the i move is not a trade, but a sacrifice
    if (game[i][2:4] != game[i+2][2:4]):
        board.push(chess.Move.from_uci(game[i+1]))
        flag_pinned = False
        second_moves_after = board.attacks(chess.parse_square(second_attacker))
       
        #find the squares that were reachable by the second attacker before the sacrifice move and now they are not reachable
        different_squares = []
        for square in second_moves:
            if square not in second_moves_after:
                different_squares.append(square)

        #if in the different squares is piece that is pinned the flag_pinned becomes True
        for j in range(len(different_squares)):
            if board.piece_at(different_squares[j]):
                temp_fen = board.fen()
                if attacker_color is chess.BLACK:
                    player_color = chess.WHITE
                else:
                    player_color = chess.BLACK
                board = chess.Board(starting_fen)
                if board.is_pinned(player_color,different_squares[j]):
                    flag_pinned = True
                    board = chess.Board(temp_fen)
                    break
                board = chess.Board(temp_fen)
        
        #if the landing square of the move i+2 was reachable by the second attacker before the sacrifice move and now it's not reachable, or the flag_pinned is True

        if ((chess.parse_square(game[i+2][2:4]) in second_moves) and (chess.parse_square(game[i+2][2:4]) not in second_moves_after)) or flag_pinned:
            if first_time:#if the function was called from the main program create an alternative game were the second attacker is capturing the sacrifice square and call the is_novotny again and return the result
                stockfish.set_fen_position(starting_fen)
                board= chess.Board(starting_fen)
                new_game = make_alternative_move(game[i],second_attacker + game[i][2:4],starting_fen)
                if new_game:
                    return is_novotny(new_game,0,board,starting_fen,game[i+1][:2],attacker_color,False)
                else:
                    return False#if the second attacker cannot capture the sacrifice square, return false
            else:#if the is_novotny called the function return true
                return True
    return False

#main program
#'c8g4','h5g4',"2q5/ppr3k1/3p4/P1pPp1bB/2P4n/1P5P/3Q1P1K/6R1 b - - 3 37"
#'a4b2','a1b2',"8/8/1Q1B4/4pp2/N4k1K/3P4/r5P1/b7 w - - 3 37"
def test_novotny():

    start=time.time()
    stockfish.set_elo_rating(3000)
    stockfish.set_depth(10)
    stockfish.update_engine_parameters({"Hash": 25600, "Threads": 10})
    board = chess.Board()
    novotny_points = []
    novotny_fen = []

    user_fen = input("Enter fen to test:")
    while(not stockfish.is_fen_valid(user_fen)):
        print("Not a valid fen.Try again.\n")
        user_fen = input("Enter fen to test:")

    stockfish.set_fen_position(user_fen) #create game from the given fen
    board= chess.Board(user_fen)

    user_sacrifice_move = input("Enter the sacrifice move:")
    while(not stockfish.is_move_correct(user_sacrifice_move)):
        print("Not a valid move.Try again.\n")
        user_sacrifice_move = input("Enter the sacrifice move:")

    stockfish.make_moves_from_current_position([user_sacrifice_move])
    user_opponent_move = input("Enter opponent's move:")
    while(not stockfish.is_move_correct(user_opponent_move)):
        print("Not a valid move.Try again.\n")
        user_opponent_move = input("Enter opponent's move:")


    stockfish.set_fen_position(user_fen)
    game = play_from_fen(user_sacrifice_move,user_opponent_move,user_fen)
    for i in range(len(game)):

        if len(game) >= i+3:
            if (game[i][2:4] == game[i+1][2:4]) and (game[i][2:4] != game[i+2][2:4]) : #if the move of the opponent captures the piece that just moves and it's not a trade on the same square
                
                original_fen = board.fen()

                board.push(chess.Move.from_uci(game[i]))            

                attacker_fen =  board.fen()#fen after the sacrifice move was made
                sacrifice_square = chess.parse_square(game[i][2:4])
                #get the color of the attacker
                if ' b' in attacker_fen:
                    attacker_color = chess.BLACK
                else:
                    attacker_color = chess.WHITE
                
                bishop_square = ''
                rook_square = ''    
                #get who is attacking the sacrifice square
                attackers = board.attackers(attacker_color,sacrifice_square)
                attackers_list = attackers.tolist()
                
                # if there are at least two pieces attacking the square that the sacrifice will take place

                if(attackers_list.count(True) >= 2): # if there are at least two pieces attacking the square that the sacrifice will take place
                    #find the squares of the bishop and the rook(to have a novotny you need these to pieces)
                    for j in range(len(attackers_list)):
                        if attackers_list[j] :
                            if board.piece_at(j).piece_type is chess.ROOK:
                                rook_square = chess.square_name(j)
                            elif board.piece_at(j).piece_type is chess.BISHOP:
                                bishop_square = chess.square_name(j)

                    #if both a rook and a bishop are attacking the sacrifice square
                    if rook_square and bishop_square:
                        game_to_check = game
                        index = i       
                        if game[i+1][:2] == rook_square:
                            second_attacker = bishop_square
                        elif game[i+1][:2] == bishop_square:
                            second_attacker = rook_square
                        else:#if the captures happens with another piece other than the bishop and the rook creat an alternative game with the capture being made by the rook and the second attacker to be the bishop
                            board = chess.Board(original_fen)
                            game_to_check = make_alternative_move(game[i],rook_square + chess.square_name(sacrifice_square),original_fen)
                            index = 0
                        if game_to_check:
                            if is_novotny(game_to_check,index,board,original_fen,second_attacker,attacker_color):
                                novotny_points.append(i)
                                novotny_fen.append(original_fen)
                    board = chess.Board(original_fen)
                    board.push(chess.Move.from_uci(game[i]))
            else:
                board.push(chess.Move.from_uci(game[i]))
        else:
            board.push(chess.Move.from_uci(game[i]))               

    #for every novotny point in each game
    for j in range(len(novotny_points)):
        flag_finished = False
        flag_register = False
        board = chess.Board(novotny_fen[j])
        #find the side that makes the sacrifice
        if ' b' in novotny_fen[j]:
            novotny_color = chess.BLACK
        else:
            novotny_color = chess.WHITE
        #get the score before the sacrifice
        starting_score = utilities.get_score(novotny_fen[j])
        #play three moves(for each player) and get the new score
        for k in range(5):
            if novotny_points[j] + k < len(game):
                board.push(chess.Move.from_uci(game[novotny_points[j] + k]))
            else:
                flag_finished = True
                break

        #if the game finished before those 3 moves and the side that made the sacrifice won, register the puzzle
        if flag_finished:
            if board.is_checkmate() and board.outcome().winner is novotny_color:
                flag_register = True
        else:# if the game did not finish, check if the side that made the sacrifice was benefited by that move after 3 moves and if so register the puzzle
            flag_register = True
            finish_score = utilities.get_score(board.fen())
            if novotny_color is chess.WHITE:
                if finish_score > starting_score:
                    flag_register = True
            else:
                if finish_score < starting_score:
                    flag_register = True

        if flag_register:
            print("It is novotny!\n")
        else:
            print("It's not a novotny.\n")

    end=time.time()
    print("Time that elapsed: ",(end - start)/60,"m" )
    user_choice = input("Do you want to check another game(y/n)?:")
    if user_choice == "y":
        test_novotny()
    else:
        print("\nGoodbye!\n")



test_novotny()