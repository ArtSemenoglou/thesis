import utilities
import time

start=time.time()

games = utilities.get_games() #load the games
counter = 1
for game in games: #for each game
    if( utilities.check_valid_puzzle(game,list(range(len(game)-5,len(game))))):
        utilities.register_puzzle(game[:-5],game[len(game)-5:],'data_final/mate_in_3.txt') # register the puzzle
        print("game saved: ",counter)
        counter = counter + 1
    else:
        print("found a wrong one......................")
end=time.time()
print("Time that elapsed: ",(end - start),"s" )