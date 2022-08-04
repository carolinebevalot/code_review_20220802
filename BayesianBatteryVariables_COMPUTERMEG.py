#!/usr\bin\env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 12:13:21 2019

@author: carolinebevalot
"""
import numpy as np


#%% MEG port adresses

ADDRESS_TRIGGER_PORT = 0x0378
ADDRESS_ANSWER_PORT_1, ADDRESS_ANSWER_PORT_2, ADDRESS_ANSWER_PORT_3 =  '0x0379', '0xCCC9', '0x0CCD9'

#%% Times

TRIGGER_DURATION = 20 # length a trigger in ms

#%% Sizes of the stimuli
SCALE_ANSWER_PICTURES =  {'MEG' : 0.2, 'no_MEG': 0.5}
SCALE_MORPH = {'MEG' : 0.35, 'no_MEG': 0.7} # morph measuring 9 * 9 cm on videoprojector screen
SCALE_HOURGLASS = {'MEG' : 0.15, 'no_MEG': 0.35}
DOT_RADIUS = {'MEG' : 1.5, 'no_MEG': 3}
CIRCLE_RADIUS= {'MEG' : 4, 'no_MEG': 8}

# Positions of the stimuli
LEFT_POS = {'MEG' : (-15, 0), 'no_MEG': (-40, 0)}
RIGHT_POS = {'MEG' : (15, 0), 'no_MEG': (40, 0)}
PLAY_POS = {'MEG' : (20, -40), 'no_MEG': (20, -70)}

# Modifications on the validation screen
BLUR_LEVEL = {'MEG' : 3, 'no_MEG': 3}

TRIGGER_DURATION = 20 # length a trigger in ms

#%% RESPONSE KEYS
NEXT_KEY = 275 # -> right arrow
PREVIOUS_KEY = 276 # <- left arrow
NEXT_BLOCK_KEY = 110 # n
PAUSE_KEY = 32 # space

CONTROL_KEYS = {'next':NEXT_KEY, 
                'previous':PREVIOUS_KEY, 
                'next_block':NEXT_BLOCK_KEY,
                'pause':PAUSE_KEY} # on keyboard : ->, <-, n

RESPONSE_KEYS = {'MEG': dict(**{'left' : 'port1_16', 'right': 'port2_32'}, **CONTROL_KEYS), # response boxes are reversed 
                 'no_MEG': dict(**{'left' : 101, 'right': 112}, **CONTROL_KEYS)} # e and p
    
EXPLICIT_REPORT_KEYS = \
    {'MEG': {'L1': 'port2_8', 'L2':'port1_64' , 'L3': 'port1_32', 'L4': 'port1_16',
             'L5': 'port2_32', 'L6': 'port2_64', 'L7': 'port3_-128', 'L8': 'port3_64'},
     'no_MEG': {'L1': 282, 'L2': 283, 'L3': 284, 'L4': 285, #F1 to F8
                'L5': 286, 'L6': 287, 'L7': 288, 'L8': 289} }
     


#%% Times

SELECTED_RESPONSE_TIME = 150
VALIDATION_EXPLICIT_REPORT_TIME = 80
MORPH_PRESENTATION_TIME = 150
RESPONSE_TIME = 800
MAXIMUM_RESPONSE_TIME = 800
BB_INTER_TRIALS_TIME = 600
LOCALIZER_TOTAL_STIM_PRESENTATION_TIME = 150
LOCALIZER_INTER_TRIALS_TIME = 600
LOCALIZER_REPETITION_FREQUENCY = 30


#%% RESPONSE KEYS


#%%
EXPLICIT_REPORT_RECURRENCE = 15 # can be 30, 60 (different from the block length : 36 to 44)
EXP_STRUCTURE = [0, 1, 2, 3, 4], [5, 6, 7, 8, 9, 10], [11, 12, 13, 14]
# Block names
NB_OF_BLOCKS_EXP3 = 15
EV_GROUP_NAMES = ['ob_faces', 'amb_faces', 'amb_houses', 'ob_houses']
                

#%% SIZES AND POSITION OF STIMULI

BACKGROUND_SCALE = 0.7

#% DIODE
DIODE_SCALE = 0.08
DIODE_BAND_SIZE = (1000,50)
DIODE_BAND_POS = (0, -280)
DIODE_SQUARE_SIZE = (50,50)
DIODE_SQUARE_POS = (-380, -280)
DIODE_TIME = 10
DIODE_MARGIN = 100

# Positions on screens
INTRO_BLOCK_POS1 = (0, 90)
INTRO_BLOCK_POS2 = (0, 55)
INTRO_BLOCK_POS3 = (0, 30)
NO_ANSWER_POS = (0, 0)

#%% Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_B = (119, 136, 153)
DARK_GRAY_B = (119/2, 136/2, 153/2)#(117, 131, 190)#, 255)

#%% INTRUCTIONS AND COMMENTS 
# Instructions text

INTRO_BLOCK_TXT_EXP3 = {'Fr' :{'Begin' :["DEBUT", "Début de la tâche !","",],
                               'Break':["PAUSE", "Prenez quelques instants avant de poursuivre", 
                                        "Attention, les boutons 'MAISON' et 'VISAGE' changent de côté"]},
                        'En': {'Begin' :["BEGINNING", "Let's begin the task !","",],
                               'Break':["BREAK", "Take a moment before continuing", 
                                         "Be careful, 'HOUSE and 'FACE' button' change sides"]}}
LOCALIZER_TXT = {'Fr' : ['Début de la seconde tâche',
                         'Cliquez sur le bouton DROIT ou GAUCHE', 'si une image est répétée'],
                 'En': ["Let's begin the second task 1",
                        'Click on the RIGHT or LEFT button', 'if a picture is repeated']}

EXPLICIT_REPORT_QUESTION_DEMO = {'Fr':{'exp3': 'A votre avis, dans ce quartier, quelle est la proportion de maisons ?',
                              'exp1':'Pouvez-vous nous rappeler à quelle proportion de maisons ce pictogramme correspond?',
                              'exp5':"A votre avis, à quel point le son est-il prédictif d'une catégorie dans ce quartier ?"},
                        'En':{'exp3': 'In your opinion, what is the proportion of houses in this district ?',
                              'exp1':'Can you remind us what proportion of houses this pictogram correspond to?',
                              'exp5':' In your opinion, how predictive is the tone of a category in this district ? '}}


EXPLICIT_REPORT_QUESTION = {'Fr':{'exp3': 'proportion de maisons ?',
                              'exp1':'Pouvez-vous nous rappeler à quelle proportion de maisons ce pictogramme correspond?',
                              'exp5':"association son - catégorie ?"},
                        'En':{'exp3': 'proportion of houses ?',
                              'exp1':'Can you remind us what proportion of houses this pictogram correspond to?',
                              'exp5':'tone - category association ? '}}

TRIGGER_DICT = {'baseline': 0,
                'localizer_face': 100,
                'localizer_house': 200,
                'found_key': 99,
                'FLeft': 77,
                'HLeft': 88,
                'part_nb': 1, #[1;6]
                'block_nb':101, #[101 ; 130]
                'trial_nb': 200} #[200 ; 256]
               
# Text
TXT_SIZE = 20
FONT = 'freesans' # '.\fonts\PT_Sans\PT\Sans-Regular.ttf' # 'helvetica'
FONTSIZE = 20
TXT_COLOR = BLACK

# Ask explicit report 
EXPLICIT_REPORT_Q_AREA = (500, 100)
POSITION_BAR_EXPLICIT_REPORT = (0, 0)  # bar for confidence rating
LEFT_POS_EXPLICIT_REPORT = -300
RIGHT_POS_EXPLICIT_REPORT = 300
SCALE_PICTO_EXPLICIT_REPORT = 0.7
EXPLICIT_REPORT_BUTTON_POSITIONS = [(horiz_pos, 0) for horiz_pos in np.linspace(-150,150,8)]
EXPLICIT_REPORT_BUTTON_SIZE = (30,10)
EXPLICIT_REPORT_BUTTON_VALIDATION_SIZE = (30,30)

