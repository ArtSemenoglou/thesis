import utilities
import time

start=time.time()

games = utilities.get_games() #load the games

for game in games: #for each game
    utilities.register_puzzle(game[:-5],game[len(game)-5:],'data_v7/mate_in_3_final.txt') # register the puzzle
end=time.time()
print("Time that elapsed: ",(end - start),"s" )