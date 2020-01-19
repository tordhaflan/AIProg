import pygame

def initBoard(layers = 4, diamond=False):
    pygame.init()
    surface = pygame.display.set_mode((640,640))
    clock = pygame.time.Clock()

    col = int(640/(2*layers-1))
    num_cols = layers
    padding = 30

    if (diamond):
        layers = 2*layers-1

    row = int(640/layers)

    #Loop to dispaly board, can be used to initialize coordinates for peg-objects
    for i in range(layers):
        k = 0
        if (diamond):
            #top part of diamond
            if (i < num_cols):
                for j in range(num_cols-i-1):
                    k += 1
                for j in range(i+1):
                    pygame.draw.circle(surface, (0, 255, 0), ((col*k)+padding, row*i+padding), 30)
                    k += 2
            #lower part of diamond
            else:
                for j in range(i-num_cols+1, 0, -1):
                    k += 1
                for j in range(layers-i):
                    pygame.draw.circle(surface, (0, 255, 0), ((col*k)+padding, row*i+padding), 30)
                    k += 2
        else:
            for j in range(layers-i-1):
                k += 1
            for j in range(i+1):
                r = pygame.draw.circle(surface, (0, 255, 0), ((col*k)+padding, row*i+padding), 30)
                k += 2


    crashed = False

    #Terminate window if red-x is pushed
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    quit()


initBoard(layers=6)