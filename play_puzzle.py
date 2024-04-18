from stockfish import Stockfish
import webbrowser
import utilities

play_again = "y"
counter = 0 #how many puzzles have been solved
filepath = ""
while(filepath == ""):
    choice = input("\n1. Mate in 3 with all the pieces\n2. Mate in 3 with only the necessary pieces\n3. Forks(without mate in 3)\n4. Underpromotion(without mate in 3)\n5. Underpromotion with mate in 2\nChoose puzzle category: \n")
    if choice == '1' :
        filepath = "data_v7/mate_in_3_final.txt"
    elif choice == '2' :
        filepath = "data_v7/mate_in_3_removed_v2.txt"
    elif choice == '3' :
        filepath = "data_v7/fork_v1.txt"
    elif choice == '4' :
        filepath = "data_v7/underpromotion_general.txt"
    elif choice == '5' :
        filepath = "data_v7/underpromotion_mate_2.txt"


    data_arr = utilities.load_puzzles(filepath)
    if(data_arr is False):
        print("\nSorry file not found\n")
        filepath == ""

while(play_again=='y' and (counter<len(data_arr))):
    stockfish = Stockfish(path="C:/Users/ArtemiosSemenoglou/Desktop/διπλωματική/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe") #initialize stockfish
    move =0 #moves made in game
    stockfish.set_fen_position(data_arr[counter]["fen"])
    for move in range(len(data_arr[counter]["next_moves"])) :
        if move%2== 0:
            fen=stockfish.get_fen_position()
            print("Spoiler! Next move is",data_arr[counter]["next_moves"][move])
            #who is playng 
            if (" b" in data_arr[counter]["fen"]):
                print("Black's turn(Lower case letters)")
            else:
                print("White's turn(Capital letters)")
            #print(stockfish.get_board_visual())
            webbrowser.open('https://fen2image.chessvision.ai/'+fen)
            input_move = input('Play:')
            while(input_move != data_arr[counter]["next_moves"][move]):
                    print("Wrong move, try again")
                    input_move = input('Try again:')
        else:
            input_move = data_arr[counter]["next_moves"][move]
            print("The opponent played: ",input_move)
        move = move +1
        stockfish.make_moves_from_current_position([input_move])
    counter = counter +1
    if(counter<len(data_arr)):
        print("Do you want to play one more puzzle(y/n)?")
        play_again = input()
    else:
        print("No more available puzzles. Goodbye!")
        quit()