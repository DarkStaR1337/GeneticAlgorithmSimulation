

import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation
#import matplotlib.animation as animation
import pygame as pg
import seaborn as sns
import csv
import sys
import math
import random

pg.init()                                   #initializing pygame library as pg.

window = width, height = 1280, 720          # Setting up the screen placeholders and where the application would be displayed (1280x720 resolution).
FPS = 240
Screen = pg.display.set_mode(window)
pg.display.set_caption("Level Sim")
clock = pg.time.Clock()
defaultFont = pg.font.SysFont(None, 40)

timeLimit = 300                             # Time (in frames) for the objects to reach the target.
frameCounter = 0                            # Current frame until the timeLimit.
objCount = 200                              # Initialization of the objects.
genCount = 0                                # Initialization of the generation counter.
levelCounter = 1                            # Displays the level.
successCounter = 0                          # Counting the successful objects.
aliveBoxCount = objCount                    # Currently existing objects.

avgFitness = 0                              # Average fitness (score from 0 to 1) of the latest generation.
avgFitnessD = 0                             # The difference between the fitness score of the last and the current generation.
lowestTime = 0                              # Least time taken (fastest object to sucessCount = 1).
lowestTimeD = 0                             # Record holder (fastest object) from the latest generation.
successCounterD = 0                         # Difference of this gen's successful objects and the last one.

finished = False                            # Boolean for deciding when the generation is finished (def False)

walls = []                                  # List for obstacles.
genePool = []                               # Best objects have more place in the gene pool.

random.seed(random.randrange(10000000))     # Setting the random seed to a random value.

levelColor = [random.randrange(150) + 100, random.randrange(150) + 100, random.randrange(150) + 100]  # Random color for the 'level' text.



def ShowText(string, x, y, size = 40, color=(255, 255, 255)):                       # Quicker way to display text on the screen.
    strFont = pg.font.SysFont(None, size)
    Screen.blit(strFont.render(string, True, color), (x, y))


def Remapper(low1, high1, low2, high2, value):                                      # A mapping function needed for later.
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)                  # Used to remap a value that has an expected range of 'low1' to 'high1', into a target range of 'low2' to 'high2'.


def Distance(x1, x2, y1, y2):                                                       # Function to calculate the distance between two points.
    return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))


class Obstacle(object):                                                             # Instantiating 'obstacle' object.
    def __init__(self, x, y, width, height):                                        # Getting x-y coordinates of size and position. 
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.subsurface = pg.Surface((self.width, self.height))                          # Creating a pygame surface for detecting collision with objects.

        
    def Draw(self):
        pg.draw.rect(Screen, (150,150,150), (self.x, self.y, self.width, self.height))    # Drawing an invisible rectangle hitbox at the goal object's position.

class DNA(object):                                                                        # Creating a DNA object for genetic algorithm
    def __init__(self, genes=None):                                                       # If initialized with a gene already, won't
        self.array = []                                                                   # generate movement randomly.
        self.chain = pg.math.Vector2()                                                    # DNA chain represented by a 2D-Vector.
        if genes:
            self.array = genes
        else:
            for i in range(timeLimit):                                                    # Till the timeLimit, generates random movement for the objects.
                self.chain.xy = random.random()*2-1, random.random()*2-1
                self.array.append(self.chain.xy)

    def CrossOver(self, partner):                                                         # Gets a partner from the generated genes using floor function,
        newGenes = []                                                                     # choose a random point in the DNA chain to mix two genetic pairs
        middle = math.floor(random.randrange(len(self.array)))                            # and create a new array of motion for the object.
        
        for i in range(len(self.array)):                                                  # Creates a new DNA object, with the newly formed gene
                                                                                          # (crossover function).
            if i < middle:
                newGenes.append(partner.array[i])                                         # Single-point crossover performed.
            else:
                newGenes.append(self.array[i])

        return DNA(newGenes)                                                              # Returns the new gene object in DNA().


class Object(object):                                                    # Creating our object.
    
    def __init__(self, dna=None):                                        # If initialized with a DNA, use that dna, else, create new.
        self.alive = True                                                # Bool to see if it's alive.
        self.crashed = False                                             # Bool to see if it's crashed.
        self.won = False                                                 # Bool to see if it's won.
        self.wonTime = 0                                                 # To save the time that the object has won ( faster get more places in the pool).
        
        if dna:
            self.gene = DNA(dna)
        else:
            self.gene = DNA()

        self.x, self.y = 10, height//2                                    # Some initializations of variables:
        self.size = 10                                                    # position, size, acceleration, velocity, velocity limit,
        self.acc = pg.math.Vector2()                                      # burst color, burst size, fitness function.
        self.acc.xy = 0, 0
        self.vel = pg.math.Vector2()
        self.vel.xy = 0, 0
        self.velLimit = 6
        self.burstColor = pg.Color("red")
        self.burstSize = 10
        self.fitness = 0
        self.subsurface = pg.Surface((self.size, self.size))             # Creating a surface to check for collisions.
        self.subsurface.fill((50, 215, 240))
        self.subsurface.set_alpha(128)

    def CheckCollision(self, arr):                                       # Checking if this object collides with the obstacles OR window frame.
        global aliveBoxCount
        if self.x + self.size > width or self.x < 0 or self.y < 0 or self.y + self.size > height:
            self.crashed = True
        for item in arr:
            if self.subsurface.get_rect(topleft=(self.x, self.y)).colliderect(item.subsurface.get_rect(topleft=(item.x, item.y))):
                self.crashed = True
        if self.crashed:
            self.alive = False
            aliveBoxCount -= 1                                           # If it's crashed, declare the object 'not alive'.

    def CalculateFitness(self):                                          # The closer it is, the better it's fitness is.
        dist = Distance(self.x, finish.x, self.y, finish.y)
        self.fitness = Remapper(0, width, 1, 0, dist)                    # Remapping the distance. If it's far, fitness apporaches '0'.
        
                                                                         # If it wins, fitness is assigned '1'.
                                                        
    def Update(self):                                                    # Updates the object every frame.
        if self.crashed:
            self.subsurface.fill((128, 0, 0))                            # If crashed, turn object color to red.
        if self.alive:
            self.acc = self.gene.array[frameCounter]
            if self.subsurface.get_rect(topleft=(self.x, self.y)).colliderect(winRect) and not self.won:
                self.won = True
                self.wonTime = frameCounter
            if self.won:
                self.x, self.y = finish.x, finish.y
                self.vel.xy = 0, 0
                self.acc.xy = 0, 0
                self.alive = False

        self.vel += self.acc                                     # Adding accel. to velocity, and changing the position according to the velocity.
        if self.vel.x > self.velLimit and self.acc.x > 0:
            self.vel.x = self.velLimit
        if self.vel.x < -self.velLimit and self.acc.x < 0:
            self.vel.x = -self.velLimit
        if self.vel.y > self.velLimit and self.acc.y > 0:
            self.vel.y = self.velLimit
        if self.vel.y < -self.velLimit and self.acc.y < 0:
            self.vel.y = -self.velLimit
        self.x += self.vel.x
        self.y += self.vel.y

    def Draw(self):                                              # If object is 'alive', every 5 frames change the burst size and color.
        if self.alive:
            if frameCounter % 5 == 0:
                self.burstColor = pg.Color("red")
                self.burstSize = 5
            else:
                self.burstColor = pg.Color("orange")
                self.burstSize = 10

            if math.fabs(self.vel.x) > math.fabs(self.vel.y):       # Deciding where to draw the thrust.
                if self.vel.x > 0:
                    pg.draw.rect(Screen, self.burstColor, (self.x - 5, self.y + 3, self.burstSize, 3))
                else:
                    pg.draw.rect(Screen, self.burstColor, (self.x + 10, self.y + 3, self.burstSize, 3))
            else:
                if self.vel.y > 0:
                    pg.draw.rect(Screen, self.burstColor, (self.x + 3, self.y - 5, 3, self.burstSize))
                else:
                    pg.draw.rect(Screen, self.burstColor, (self.x + 3, self.y + 10, 3, self.burstSize))
        Screen.blit(self.subsurface, (self.x, self.y))

        
finish = pg.math.Vector2()                                              # Setting
finish.xy = width-50, height//2                                             # up
                                                                            # the
winSurface = pg.Surface((80, 80))                                           # end
winRect = winSurface.get_rect(topleft=(finish.x-40, finish.y-40))           # goal and an invisible 'rect' object to check for collision.

squares = []                                                                # Array to hold the objects.
for i in range(objCount):
    squares.append(Object())


def FinishGeneration():     # A function for resetting process.

    global finished, avgFitness, timeLimit, walls, successCounter           # Getting all the global variables.
    global genCount, frameCounter, levelCounter, lowestTime
    global levelColor, avgFitnessD, lowestTimeD, successCounterD, aliveBoxCount

    tempLowestTime = lowestTime         # Setting up some values.
    tempAvgFitness = avgFitness
    tempSuccessCounter = successCounter
    genePool.clear()
    maxFit = 0
    lowestTime = timeLimit
    lowestIndex = 0
    successCounter = 0
    avgFitnessSum = 0
    maxFitIndex = 0
    for sq in squares:
        sq.CalculateFitness()                                      # Start definition of the fiteness function here; if the value comes
        avgFitnessSum += sq.fitness                                # out to be equal to or higher than 1, count it as a success and
        if sq.fitness >= 1.0:                                      # increase the counter.
            successCounter += 1                                   
        if sq.fitness > maxFit:                                    # Defines a max fitness score to compare from past ones.
            maxFit = sq.fitness
            maxFitIndex = squares.index(sq)
    successCounterD = successCounter - tempSuccessCounter
    avgFitness = avgFitnessSum / len(squares)
    avgFitnessD = avgFitness - tempAvgFitness

    for i, sq in enumerate(squares):
        if sq.won:
            if sq.wonTime < lowestTime:
                lowestTime = sq.wonTime
                lowestIndex = i
    lowestTimeD = lowestTime - tempLowestTime

    
    
    
    for i, sq in enumerate(squares):
        n = int((sq.fitness ** 2) * 100)
        if i == maxFitIndex:
            print("Fitness:", sq.fitness)                              # Prints the fitness value,
            print("Successful objects:", successCounter)               # no. of successful objects and
            print("Generation:", genCount)                             # the respective generation to the console.
            
     
    
            rows = [successCounter, genCount, avgFitness]  
            
            with open('data.csv', 'a+') as csvfile:         # Stores latest recorded data
                writer = csv.writer(csvfile)                # to a csv file named data.csv.
                writer.writerow(rows)

            #def animate(i):
                #plt.cla()
                #data = pd.read_csv('data.csv')
                #x = data['Generation']
                #y = data['Average Fitness']
                
                #plt.plot(x, y)
                #plt.xlabel('Generation')
                #plt.ylabel('Average Fitness')
               # plt.title('Gen vs. Fitness')
            #plt.tight_layout()
           # plt.show()
           # ani = FuncAnimation(plt.gcf(), animate, interval = 1000, frames = 500, repeat = True)
            #f = r"C:/Users/shash/Desktop/ai/output/fitness.gif" 
            #writer = animation.PillowWriter(fps=30) 
            #ani.save(f, writer=writer)
              
            def prettyPlotGraph():
                df = pd.read_csv('data.csv')
                sns.set_theme(style = "darkgrid")
                sns.lineplot(data = df, x = 'Generation', y = 'Successful Objects')
                sns.scatterplot(data = df, x = 'Generation', y = 'Successful Objects')
                plt.show()

            def prettyPlotGraph1():
                df = pd.read_csv('data.csv')
                sns.set_theme(style = "darkgrid")
                sns.lineplot(data = df, x = 'Generation', y = 'Average Fitness')
                sns.scatterplot(data = df, x = 'Generation', y = 'Average Fitness')
                plt.show()
                
            prettyPlotGraph()
            prettyPlotGraph1()
            
                
            if successCounter < 2:
                n = int((sq.fitness ** 2) * 150)            # Squared the fitness value to make sure
                                                            # the furthest ones get much more place in the gene pool.
        if i == lowestIndex and successCounter> 1:
            n = int((sq.fitness ** 2) * 500)                # If it's the first one to finish when there are more boxes
                                                            # finishing the level, get much much more places in the pool.
        for j in range(n):
            genePool.append(squares[i])
            
            
    if successCounter >= len(squares)//2:                   #Controls the required amount of successful objects to proceed to next level (for all objects to clear the stage, remove floor division [//2]).
        levelCounter += 1

        
        
        if levelCounter == 1:                                # Set the levelCounter accordingly.
                timeLimit = 300     
                walls = [

                ]
            
        elif levelCounter == 2:                              # Obstacles for level 2.
            timeLimit = 350
            walls = [
                Obstacle(500, 0, 20, 420),
                Obstacle(800, 300, 20, 420)
            ]
            
        elif levelCounter == 3:                              # Obstacles for level 3.
            timeLimit = 400
            walls = [
                Obstacle(350, 200, 20, 320),
                Obstacle(750, 200, 20, 320),
                Obstacle(550, 250, 20, 200),
                Obstacle(550, 0, 20, 200),
                Obstacle(550, 520, 20, 200)
            ]
            
        elif levelCounter == 4:                              # Obstacles for level 4.
            timeLimit = 400
            walls = [                            
                Obstacle(300, 0, 20, 400),
                Obstacle(500, 420, 20, 300),
                Obstacle(410, 250, 200, 20),
                Obstacle(650, 0, 20, 200),
                Obstacle(650, 670, 20, 50),
                Obstacle(670, 0, 20, 300),
                Obstacle(670, 570, 20, 150),
                Obstacle(690, 0, 20, 400),
                Obstacle(690, 470, 20, 250),
                Obstacle(710, 0, 20, 400),
                Obstacle(710, 470, 20, 250),
                Obstacle(730, 0, 20, 400),
                Obstacle(730, 470, 20, 250),
                Obstacle(800, 460, 20, 260),
                Obstacle(800, 0, 20, 200),
                Obstacle(800, 280, 20, 100),
                Obstacle(800, 270, 200, 20),
                Obstacle(800, 370, 200, 20)
            ]
            
        elif levelCounter == 5:                              # Obstacles for level 5.
            timeLimit = 450
            walls = [
                Obstacle(200, 0, 20, 620),
                Obstacle(500, 0, 20, 380),
                Obstacle(500, 530, 20, 190),
                Obstacle(800, 300, 20, 420),
                Obstacle(800, 0, 20, 200),
                Obstacle(1100, 0, 20, 350),
                Obstacle(1100, 500, 20, 270),
            ]

        squares.clear()
        genCount = 0
        for i in range(objCount):
            squares.append(Object())
    else:
        for i, sq in enumerate(squares):                         # For every object, create a child object using the crossover function.
            randomIndex = random.randint(0, len(genePool) - 1)
            parentA = genePool[randomIndex].gene
            randomIndex = random.randint(0, len(genePool) - 1)
            parentB = genePool[randomIndex].gene
            child = parentA.CrossOver(parentB)
            squares[i] = Object(child.array)
        genCount += 1
    frameCounter = 0
    aliveBoxCount = objCount
    finished = False


if levelCounter == 1:       # If something went wrong, restart and check the stage equals'1' and
    timeLimit = 300         # the framelimit is 300, with obstacles removed.
    walls = [
        
    ]
    
    
fields = ["Successful Objects", "Generation", "Average Fitness"]
with open('data.csv', 'w+') as csvfile:         
    writer = csv.writer(csvfile)                # saves data obtained to a csv file named data.csv.
    writer.writerow(fields)
csvfile.close()  



while True:                             # To keep the window open.
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:       # If X button is pressed, close the screen and exit the program.
            pg.quit()
            sys.exit()

    counterText = "Frame: " + str(frameCounter)       # Set the frame count text.
    counterLimitText = " / " + str(timeLimit)

    Screen.fill((0, 0, 0))                           # Fill the screen with the color (0,0,0)
    for wall in walls:                               # Draw every wall.
        wall.Draw()

    for sq in squares:                                # Draw, check collision, and update for every object.
        sq.Draw()
        if sq.alive:
            sq.CheckCollision(walls)
            sq.Update()


##################################################### Various functions for displaying data on the screen. #####################################################
    
    ShowText("Stage " + str(levelCounter), 1050, 20, 80, levelColor)                                       # Shows the current Stage.

    ShowText(counterText, 10, 30)                                                                          # Generates the frame counter.
    ShowText(counterLimitText, 160, 33, 30)
    
    ShowText("Gen. Counter: " + str(genCount), 10, 80)                                                     # Generation Counter.
    ShowText("Objects Alive: " + str(aliveBoxCount), 10, 110, 30, pg.Color("magenta"))                     # Alive Counter.
    ShowText("Latest generation: ", 10, 550, 45)                                                            # Current Generation.
    ShowText("Total Objects Spawned:     " + str(len(squares)), 30, 590, 25, pg.Color("cyan"))             # Total objects.
    
    
    ShowText("Successful Objects: " + str(successCounter), 30, 610, 25)                                    # 'Succesful objects' counter.
    if successCounterD > 0:                                                  
        ShowText("+" + str(successCounterD), 250, 610, 25, pg.Color("green"))
    else:
        ShowText("-" + str(-successCounterD), 250, 610, 25, pg.Color("red"))

        
    ShowText("Average Fitness: " + str(round(avgFitness, 3)), 30, 630, 25)                                 # 'Average Fitness' counter.
    if avgFitnessD > 0:
        ShowText("+" + str(round(avgFitnessD, 3)), 250, 630, 25, pg.Color("green"))
    else:
        ShowText("-" + str(round(-avgFitnessD, 3)), 250, 630, 25, pg.Color("red"))
        

    ShowText("Time : " + str(lowestTime), 30, 650, 25)                                                     # 'Latest best time' counter.                
    if lowestTimeD > 0:
        ShowText("+" + str(lowestTimeD), 250, 650, 25, pg.Color("red"))
    else:
        ShowText("-" + str(-lowestTimeD), 250, 650, 25, pg.Color("green"))
    
    
    
    pg.draw.circle(Screen, pg.Color("red"), (int(finish.x), int(finish.y)), 20)       # Finally, generates the goal object (red circle).
    pg.display.update()     # Update the display of the screen every frame
    
    if (frameCounter >= timeLimit-1 and levelCounter < 6) or aliveBoxCount <= 0:    # Generation ends if level number exceeds 5 or no objects remain on the screen.
        frameCounter = timeLimit-1
        finished = True
    else:                                                                           
        frameCounter += 1     # Adds to the frame count every frame.
    
    if finished:
        FinishGeneration()  # Start the resetting process.
pg.quit()
sys.quit()




