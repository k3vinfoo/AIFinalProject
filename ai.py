'''
    Kevin Foo
    CS 4613 - AI
    Final Project
    Mini Camelot
'''

from Tkinter import *
from tkMessageBox import *
import time

'''
***************************************
*    AI Move Functions                *
*    Includes:                        *
*        - eval_func()                *
*        - MaxValue                   *
*        - MinValue()                 *
(        - ai_turn(): Alpha Beta      *
***************************************     
'''

# Places utility value for each node
# Utilizes the distance formula
def eval_func(MyPiece, OppPiece, player_color, OppColor):
    # Evaluation function:
    # place weights on different aspects of game
    # 1. distance from castle
    # 2. amount of pieces remaining
    # want to maximize distance to goal castle and minimize distance from own castle

    white_castle_1 = (3,0)
    white_castle_2 = (4,0)
    black_castle_1 = (3,13)
    black_castle_2 = (4,13)

    playerPiecesSize = len(MyPiece)
    OppPiecesSize = len(OppPiece)
    global optimal
    global notOptimal

    close1 = 1
    close2 = 1
    away1 = 1
    away2 = 1

    for i in MyPiece:
        close1 += ((black_castle_2[0] - float(i[0])) ** 2 + (black_castle_2[1] - float(i[1])) ** 2) ** 0.5
        close2 += ((black_castle_1[0] - float(i[0])) ** 2 + (black_castle_1[1] - float(i[1])) ** 2) ** 0.5
    trueClose = max (close1, close2)
    nearVal = playerPiecesSize * (1000/ (trueClose * 20))
    for j in OppPiece:
        away1 += ((white_castle_2[0] - float(j[0])) ** 2 + (white_castle_2[1] - float(j[1])) ** 2) ** 0.5
        away2 += ((white_castle_1[0] - float(j[0])) ** 2 + (white_castle_1[1] - float(j[1])) ** 2) ** 0.5
    trueAway = min (away1, away2)
    awayVal = 1000 / (trueAway * 100 * OppPiecesSize)

    eval = nearVal + awayVal
    #print eval
    return eval
    #eval =  (4 * optimal) + 2*notOptimal + ((30 * max(close_1, close_2) * (close_1+close_2)) + (min(away_1, away_2) * 10 * abs(away_1-away_2)) - (maxSum - minSum))

# MaxValue is Max function of Alpha-beta algorithm
def MaxValue(x, y, cur_depth, a, b, color, ai_color):
    global NodeGen, PrunInMax, AIwin

    value_lst = []

    #checkForTerminal (x, y, color, ai_color, value_lst)
    # check for terminal states:
    if terminalState(x, color):
        value_lst.append(INF)
        value_lst.append(x)
        return value_lst

    if terminalState(y, ai_color):
        value_lst.append(-INF)
        value_lst.append(y)
        return value_lst

    #tree depth 0 reached (can just find utility value)
    if (cur_depth == 0):
        util = eval_func(x, y, color, ai_color)
        value_lst.append(util)
        value_lst.append(x)
        return value_lst

    v = -INF
    tmp_pos_lst = x[:]

    #consider capturing first
    for i in range(len(x)):
        CapMove = CapturingMove(x[i], y, x)
        if (CapMove):
            NodeGen += 1
            coord_lst = x[:]
            tmp_pos_lst = x[:]
            coord_lst[i] = CapMove[0]
            value_lst.append(INF)
            value_lst.append(coord_lst[:])
            value_lst.append(CapMove[1])
            return value_lst
        poss_moves_lst = possibleMoves(x[i], x, y)
        # print poss_moves_lst
        for j in range(len(poss_moves_lst)):
            NodeGen = NodeGen + 1
            coord_lst = x[:]
            coord_lst[i] = poss_moves_lst[j]

            k = MinValue(coord_lst, y, cur_depth - 1, a, b, ai_color, color)[0]
            if (k > v):
                v = k
                tmp_pos_lst = coord_lst[:]
            if (v >= b):
                PrunInMax += 1
                # print "Prunning"
                value_lst.append(v)
                value_lst.append(coord_lst[:])
                value_lst.append(0)  # Not Captured
                return value_lst
            if a < v:
                a = v

    value_lst.append(v)
    if tmp_pos_lst == x:
        value_lst.append(coord_lst)  # New list is appened which will be returned
    else:
        value_lst.append(tmp_pos_lst)
    value_lst.append(0)  # Not Captured

    return value_lst

def MinValue(x, y, cur_depth, a, b, ai_color, color):
    global NodeGen
    global PrunInMin, AIwin
    value_lst = []

    # checking for terminal state
    if terminalState(y, ai_color):
        value_lst.append(-INF)
        value_lst.append(y)
        return value_lst

    if terminalState(x, color):
        value_lst.append(INF)
        value_lst.append(x)
        return value_lst

    if cur_depth == 0:
        util = eval_func(y, x, ai_color, color)
        value_lst.append(util)
        value_lst.append(y)
        return value_lst

    v = INF
    tmp_pos_lst = y[:]  # Initial piece position

    # check for capturing
    for i in range(len(y)):
        CapMove = CapturingMove(y[i], x, y)

        if (CapMove):
            NodeGen += 1
            coord_lst = y[:]
            coord_lst[i] = CapMove[0]
            value_lst.append(-INF)
            # coordinates for the capture move appended into list
            value_lst.append(coord_lst[:])
            return value_lst
        poss_moves_lst = possibleMoves(y[i], y, x)

        for j in range(len(poss_moves_lst)):
            NodeGen = NodeGen + 1
            coord_lst = y[:]

            coord_lst[i] = poss_moves_lst[j]
            k = MaxValue(x, coord_lst, cur_depth - 1, a, b, color, ai_color)[0]
            if (k < v):
                v = k
                tmp_pos_lst = coord_lst[:]
            if (v <= a):
                #print("pruning in min")
                PrunInMin += 1
                value_lst.append(v)
                value_lst.append(coord_lst[:])
                return value_lst
            if (b > v):
                # v gets defined
                b = v

    value_lst.append(v)
    if tmp_pos_lst == x:
        value_lst.append(coord_lst)
    else:
        value_lst.append(tmp_pos_lst)
    return value_lst

# Start of AB algorithm
def ai_turn():
    global x,y, NodeGen, PrunInMin, PrunInMax, AIwin, ai_color, player_color, PLYRwin

    checkGameStats()

    print "\n********** AI Turn **********"

    # Defining time below:

    # Time when search began
    start_time = time.time()

    # Time when search is expected to stop (10 seconds)
    end_time = start_time + 10
    #print'Start Time:', time.asctime( time.localtime(start_time) )

    # AB algo uses IDS to a defined depth and search stops there
    # Calls MaxValue function then and returns best possible move based on utility_function
    for i in range(MaxDepth + 1):
        NodeGen = 1
        state = MaxValue(x, y, i, -INF, INF, ai_color, plyr_color)
        return_time = time.time() # time returned from MinMax

        if state[0] == INF or state[0] == -INF:
            terminalNodeTime = time.time()
            print'Terminal Node reached! Time(s):', terminalNodeTime - start_time
            checkGameStats()
            break

        if (time.time() > end_time): # search exceeded 10 seconds
            time_over = time.time()
            print '10 seconds -- cutting off search. Time(s):', time_over - start_time
            break

        if AIwin:
            checkGameStats()
    print "========== SEARCH STATS =========="
    print "Depth Searched:", i
    print "Total Nodes Generated:", NodeGen
    print "Number of Prunning in Max: ", PrunInMax
    print "Number of Prunning in Min: ", PrunInMin
    print "Time to Traverse Tree(s): ",return_time - start_time
    print "==================================\n"

    if (len(x) == len(state[1])):
        for i in range(len(x)):
            if x[i] != state[1][i]:
                x_0 = x[i][0] * SqSize + SqSize/2
                x_1 = x[i][1] * SqSize + SqSize/2
                sqID_board = gui_canvas.find_overlapping(x_0, x_1, x_0, x_1)
                gui_canvas.delete(sqID_board[1])
                make_pieces(state[1][i], piece_offset, ai_color)
                break
    x = state[1]
    CapPiece = state[2]

    if CapPiece:
        print '========== White', "Piece:", CapPiece, " Captured =========="
        y.remove(CapPiece)
        capPiece_0 = CapPiece[0] * SqSize + SqSize/2
        capPiece_1 = CapPiece[1] * SqSize + SqSize/2
        sqID_board = gui_canvas.find_overlapping(capPiece_0, capPiece_1, capPiece_0, capPiece_1)
        gui_canvas.delete(sqID_board[1])
    # check for winner
    checkGameStats()

'''
******************************
*    Player Move Functions   *
*    Includes:               *
*        - checkValidity     *
*        - terminalState     *
*        - CapturingMove     *
*        - PossibleMoves     *
*        - checkGameStats    *
*        - piece_select      *
*        - position_select   *
******************************
'''


# Check the coord selected is valid board position
def checkValidity(str, axis):
    if (str[0] < 0 or str[0] > 7 or str[1] < 0 or str[1] > 13):
        return -1
    # coords is set of invalid positions (outside the board)
    coords = ((0,0), (1,0), (2,0), (0,1), (1,1), (0,2), (5,0), (6,0), (7,0), (6,1), (7,1), \
           (7,2), (0,11), (0,12), (1,12), (0,13), (1,13), (2,13), (7,11), (6,12), (7,12), (5,13),\
               (6,13), (7,13))
    if str in coords:
        return -1
    if str in axis:
        return 0
    return 1

# Define and check for terminal states - two pieces from piece_lst must be in terminal state
def terminalState(pieces_lst, color):
    global AIwin, PLYRwin
    win_white1 = (3,13)
    win_white2 = (4,13)
    win_black1 = (3,0)
    win_black2 = (4,0)

    if color == 'white':
        if (win_white1 in pieces_lst) and (win_white2 in pieces_lst):
            print'========== Human win =========='
            # PLYRwin = 1
            return 1
        # elif (win_white1 in pieces_lst) or (win_white2 in pieces_lst):
        #     print 'one white piece in terminal state'

    if color == "black":
        if (win_black1 in pieces_lst) and (win_black2 in pieces_lst):
            print '========== AI win ========='
            # AIwin = 1
            return 1
        # elif (win_black1 in pieces_lst) or (win_black2 in pieces_lst):
        #     print 'one black piece in terminal state'

def CapturingMove (str, x, y):
    cap_lst = []
    #print("capturing move")
    for i in range(-1, 2):
        for j in range(-1, 2):
            tup_be = (str[0] + j, str[1] + i)
            if (not checkValidity(tup_be, x) ):

                index_i = 0
                index_j = 0

                if (j == -1):
                    index_j = -2
                if (j == 1):
                    index_j = 2
                if (i == -1):
                    index_i = -2
                if (i == 1):
                    index_i = 2
                tup_af = (str[0] + index_j, str[1] + index_i)

                if checkValidity(tup_af, x) == 1 and checkValidity(tup_af, y) == 1:
                    cap_lst.append(tup_af)
                    cap_lst.append(tup_be)
                    return cap_lst

# Check all moves possible and returns a list of them for a given user and the move that is desired
def possibleMoves(str, x, y):
    lst = []
    '''
        -2 -> 2
        Pieces can move at most two spaces left and right.
        -2,2: spot after immediate square 
        -1,1: immediate square beyond piece's square
    
    '''
    for i in range(-1,2):
        for j in range(-1,2):
            tup = (str[0]+j, str[1]+i)
            if checkValidity(tup, x) == 1 and checkValidity(tup, y):
                lst.append(tup)
            else:
                index_i = 0
                index_j = 0

                if (j == -1):
                    index_j = -2
                if (j == 1):
                    index_j = 2
                if (i == -1):
                    index_i = -2
                if (i == 1):
                    index_i = 2
                tup = (str[0] + index_j, str[1] + index_i)

                if checkValidity(tup, x) == 1 and checkValidity(tup, y) == 1:
                    lst.append(tup)
    return lst

def piece_select(event):
    global piece_clicked, src_coord, square_id, piece_id, x, y
    # redraw boxed borders
    if piece_clicked:
    #    print("piece_clicked")
        print square_id
        gui_canvas.itemconfig(square_id, outline="black", width=1)
    src_coord= (event.x/SqSize, event.y/SqSize)
   #print ('events:', event.x, event.y)
    #print("src_coord:", src_coord)
    square_id, piece_id = gui_canvas.find_overlapping(event.x, event.y, event.x, event.y)
    if src_coord in y:
        print "Source:", (src_coord)
        gui_canvas.itemconfig(square_id, outline="red", width=2)
        piece_clicked = 1
    else:
        print "Bad Move"

# Checks for win from either player AI or Human based on length of player piece lst or
# boolean variables
def checkGameStats():
    global AIwin, PLYRwin, x, y
    # print "checkGameStats"
    # print"AIwin", AIwin
    # print"PLYRwin", PLYRwin
    # print"len(y)", len(y)

    # AI or Human won, but either did not retain 2 pieces
    if ((AIwin or len(y) == 0) and len(x) < 2 and goal_left_AI == 0) or (
            (PLYRwin or len(x) == 0) and len(y) < 2 and goal_left_MY == 0):
        showinfo("Game Over", message="Reached End of Game, however 2 pieces on either side was not left over")
        print"==========GAME OVER=========="
        print"2 pieces were not left over!"
    # draw
    if len(x) == 1 and len(y) == 1:
        showinfo("Game Over", message="DRAW!")
        print"==========GAME OVER=========="
        print"DRAW"
    # AI wins: through castle, depleting humans's pieces
    elif (AIwin or len(y) == 0) and len(x) >= 2:
        showinfo("Game Over", message="AI WINS!")
        print"==========GAME OVER=========="
        print"AI has won"
    # Human wins: through castle, depleting AI's pieces
    elif (PLYRwin or len(x) == 0) and len(y) >= 2:
        showinfo("Game Over", message="YOU WIN!")
        print"==========GAME OVER=========="
        print"Human Player has won"

# When a square is clicked - determine position
# Also whether there is a capturing move that must be taken
# Determines if move desired to be made is legal
def position_select (event):
    global AIwin, PLYRwin
    global goal_left_MY
    global goal_left_AI
    global piece_clicked

    checkGameStats()

    if piece_clicked:
        try:
            index = y.index(src_coord)
        except ValueError:
            print "Not a valid piece to move!"
        poss_moves_lst = possibleMoves(src_coord, y, x)
        dest_coord = (event.x/SqSize, event.y/SqSize)

        print"Destination:", dest_coord

        #capturing move
        for i in range(len(y)):
            capMove = CapturingMove(y[i], x, y)
            # print "Cap Move? ", capMove
            if (capMove):
                break

        if capMove and dest_coord in poss_moves_lst:
            capX = 0
            capY = 0

            # print ('capMove and dest_coord in moves_lst')
            # print "dest_coord", dest_coord
            # print "src_coord", src_coord


            if abs(dest_coord[0] - src_coord[0]) == 2 and abs(dest_coord[1] - src_coord[1]) == 2:
                capX = (src_coord[0] + dest_coord[0])/2
                capY = (src_coord[1] + dest_coord[1])/2
            if abs(dest_coord[0] - src_coord[0]) == 2 and abs(dest_coord[1] - src_coord[1]) == 0:
                capX = (src_coord[0] + dest_coord[0]) / 2
                capY = dest_coord[1]
            if abs(dest_coord[0] - src_coord[0]) == 0 and abs(dest_coord[1] - src_coord[1]) == 2:
                capX = dest_coord[0]
                capY = (src_coord[1] + dest_coord[1]) / 2

            # print"capX, capY:", capX, capY

            if (capX or capY):
                capCoord = (capX, capY)
                print("capture coord",capCoord)
                if capCoord in x:
                    print '==========', 'AI piece captured', capCoord, '=========='
                    x.remove(capCoord)
                    # remove piece from board
                    # redrawBoard(capX, capY, SqSize)

                    x_board = capX * SqSize + SqSize / 2
                    y_board = capY * SqSize + SqSize / 2

                    sqId_on_board = gui_canvas.find_overlapping(x_board, y_board, x_board, y_board)
                    gui_canvas.delete(sqId_on_board[1])
                    gui_canvas.delete(piece_id)

                    # indicate in lst that piece has moved by giving new coord.
                    y[index] = dest_coord
                    make_pieces(dest_coord, piece_offset, plyr_color)
                    # print 'y', y
                    if terminalState(y, plyr_color):
                        # terminal_pieces.append(y)
                        #goal_left_MY -=1
                        #if goal_left_MY == 0:
                        PLYRwin = 1
                    ai_turn()
                    return
            print"There's a capturing move. You must capture.\n"

        # No Capturing Move, just a normal move

        print"Possible Moves for Source Piece", poss_moves_lst
        if not capMove and dest_coord in poss_moves_lst:
            gui_canvas.delete(piece_id)
            y[index] = dest_coord
            make_pieces(dest_coord, piece_offset, plyr_color)
            #gui_canvas.itemconfig(square_id, outline="black", width=1)

            if terminalState(y, plyr_color):
                # first piece reached goal state
                #goal_left_MY -= 1
                #print 'Goal State Reached. Pieces Left =', goal_left_MY
                #if goal_left_MY == 0:
                    #both reached -- win
                PLYRwin = 1
            ai_turn()
        else:
            print "Invalid Position -- Try again"

    # Human player has no more pieces; Lost
    if(len(x) == 0):
        return 1

'''
**********************************
*    Game UI functions           *
*    Includes:                   *
*        - toggle_entry          *
*        - combinedFuncs         *
*        - make_squares          *
*        - make_pieces           *
*        - manage_colors         *
*        - set_layout            *
*        - select_difficulty     *
**********************************
'''
# User play functionality to select modes
def toggle_entry():
    #print'toggle_entry'
    global hidden
    if hidden:
        text.grid()
        lbb.grid()
        rb1.grid()
        rb2.grid()
        rb3.grid()
    else:
        text.grid_remove()
        lbb.grid_remove()
        rb1.grid_remove()
        rb2.grid_remove()
        rb3.grid_remove()

    hidden = not hidden

# Called when difficulty level is chosen -- sets up rest of game
def combinedFuncs():
    gui_canvas.grid(row=4, column=0)
    toggle_entry()
    SelectDifficulty()
    ManageColors()

# Building Mini Camelot board
def make_squares(gui_canvas, color, SqSize):
    length = 14
    width = 8
    for j in range(length):
        for i in range(width):
            # in-bounds legal board spaces
            gui_canvas.create_rectangle(i * SqSize, j * SqSize, (i + 1) * SqSize, (j + 1) * SqSize, fill=color, tag="Square")

            # Fill in the corners, to distinguish game space (out-of bounds)
            if j == 0 or j == 13:
                if i <= 2 or i >= 5:
                    gui_canvas.create_rectangle(i * SqSize, j * SqSize, (i + 1) * SqSize, (j + 1) * SqSize, fill="white", tag="Square")
                    # gui_canvas.itemconfig(square_id, outline="black", width=1)

            if j == 1 or j == 12:
                if i <= 1 or i >= 6:
                    gui_canvas.create_rectangle(i * SqSize, j * SqSize, (i + 1) * SqSize, (j + 1) * SqSize, fill="white", tag="Square")
            if j == 2 or j == 11:
                if i <= 0 or i >= 7:
                    gui_canvas.create_rectangle(i * SqSize, j * SqSize, (i + 1) * SqSize, (j + 1) * SqSize, fill="white", tag="Square")

# Build pieces for board using piece_offset
def make_pieces(x, piece_offset, color):
    i = x[0]
    j = x[1]
    i_sq = i * SqSize + piece_offset
    j_sq = j * SqSize + piece_offset
    i_next_sq = (i + 1) * SqSize - piece_offset
    j_next_sq = (j + 1) * SqSize - piece_offset
    t = gui_canvas.create_oval(i_sq, j_sq, i_next_sq, j_next_sq, fill=color, tag="Piece")
    return t

# Define colors and begin to start game by calling SetLayout()
def ManageColors():
    global ai_color, plyr_color

    # human player is white piece, ai will play as black piece

    print "Your Color: ", 'white'
    plyr_color = 'white'  # Human Color
    ai_color = 'black'  # Computer Color
    print "Computer Color: ", 'black\n'
    print "========== GAME START =========="
    SetLayout()

# Distinguishes 6 pieces for each player, makes game board, and makes pieces
def SetLayout():
    global x, y, ai_color, plyr_color

    x = [b1, b2, b3, b4, b5, b6]
    y = [w1, w2, w3, w4, w5, w6]

    make_squares(gui_canvas, "Yellow", SqSize)

    for i in x:
        AIids.append(make_pieces(i, piece_offset, ai_color))
    for i in y:
        Myids.append(make_pieces(i, piece_offset, plyr_color))

# Sets the difficulty level of game, which in turns determines the depth of tree Iterative Deepening
# Search (IDS) will search
def SelectDifficulty():
    global MaxDepth
    if v.get() == 1:
        MaxDepth = 2
    if v.get() == 2:
        MaxDepth = 3
    if v.get() == 3:
        MaxDepth = 4
    print 'AI Difficulty: ', v.get()


'''
End of game UI functions
'''


''' 
**********************************************************
*  Pre-set board configuration/ Pre-defined variables    *
**********************************************************
'''

INF = 10000

w1 = (3, 5)
w2 = (4, 5)
w3 = (2, 4)
w4 = (3, 4)
w5 = (4, 4)
w6 = (5, 4)
b1 = (3, 8)
b2 = (4, 8)
b3 = (2, 9)
b4 = (3, 9)
b5 = (4, 9)
b6 = (5, 9)

state = [0]

AIwin = 0
PLYRwin = 0
# goal_left_AI = 2
# goal_left_MY = 2
plyr_color = ''
ai_color = ''

NodeGen = 1 # root node always
PrunInMax = 0
PrunInMin = 0

piece_clicked = 0
MaxDepth = 0  # Default value

SqSize = 40  # Square Size on the GUI
PIECE_DIAMETER = 37  # Piece Diameter on the GUI
piece_offset = (SqSize - PIECE_DIAMETER)

MainGUI = Tk()
hidden = False
v = IntVar()

MainGUI.title("Mini Camelot")
h = SqSize * 14
w = SqSize * 8
gui_canvas= Canvas(MainGUI, height=h, width=w)

x = [] # coord lists
y = []

AIids = []  # stores piece ids from game board
Myids = []
terminal_pieces = []

square_id = ()  # stores clicked square ids
piece_id = ()  # stores clicked piece ids
src_coord = ()  # set of piece clicked coord

'''
*******************************
*     TKinter Items           *
*******************************
'''

# Creating radio buttons to choose difficulty level
# On click call the cominedFuncs() function

text = Label(MainGUI, text="Mini Camelot", justify=LEFT, padx=20)
lbb = Label(MainGUI, text="Choose Difficulty ", justify=LEFT, padx=20)
rb1 = Radiobutton(MainGUI, text="Level 1", padx=10, variable=v, value=1, command=combinedFuncs)
rb2 = Radiobutton(MainGUI, text="Level 2", padx=10, variable=v, value=2, command=combinedFuncs)
rb3 = Radiobutton(MainGUI, text="Level 3", padx=10, variable=v, value=3, command=combinedFuncs)
text.grid(row=0, column=1, columnspan=3)
lbb.grid(row=1, column=1, columnspan=3)

rb1.grid(row=2, column=1, columnspan=1)
rb2.grid(row=2, column=2, columnspan=1)
rb3.grid(row=2, column=3, columnspan=1)

# piece click calls piece_select() and square clicks calls position_select()
gui_canvas.tag_bind("Piece", "<1>", piece_select)
gui_canvas.tag_bind("Square", "<1>", position_select)

MainGUI.mainloop()