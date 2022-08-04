#!\usr\bin\env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 09:08:30 2019
@author: carolinebevalot
"""


#%% DEFINE PATHS 

from Configurations import  define_paths, add_language_paths, define_specific_config
import pandas as pd
import os
import sys
import argparse
import os.path as op
import expyriment
import glob
import random
import shutil
from BatteryScript.BayesianBatteryFunctions_T1T2MEG import *
from BatteryScript.BayesianBatteryVariables_COMPUTERMEG import *

computer = 'caroline-Latitude-5300' #''os.name.nodename #'MEG_computer' #
no_meg=True if computer == 'caroline-Latitude-5300' else False

parser = argparse.ArgumentParser(description='Task2 Bayesian Battery in implicit context ')
parser.add_argument('--no-meg', action='store_true', default=no_meg, help='Tells to write the trigger onto a file instead of sending to parallel port')
parser.add_argument('--computer', type=str, default=computer, help='Define on which computer the script is run to adapt paths')
parser.add_argument('--is_eyelink', action='store_true', default=False, help='Record eye tracking')
parser.add_argument('--nb_of_lists', type=int, default=1, help='Number of lists of 600 trials the subject is presented with')
parser.add_argument('--language', type=str, default='Fr', help='Define in which language the instructions will be shown')
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Debugging mode')
parser.add_argument('-n', '--exp-name', type=str, default='Task1BayesianBattery', help='Experiment name')
parser.add_argument('--do-not-ask-for-keys', action='store_true', default=False, help='Do not ask for the response keys. In case we already know the correct keys.')
parser.add_argument('--empty-room', action='store_true', default=False, help='Do not wait at any time, just show all stims. To check triggers at the MEG')
args = parser.parse_args()
print(args)


CONFIG = define_paths(args.computer, 'MEG_data')
define_specific_config(CONFIG, 'exp3', args.language, no_meg=args.no_meg)
add_language_paths(CONFIG)
NB_OF_LISTS_TO_PRESENT = args.nb_of_lists
STIMULUS_EVIDENCE_LEVELS \
    = pd.read_csv(op.join(CONFIG['PathRoot'],'BatteryAnnex', 
                          'morphs_evidence_level_eight_quantiles.csv'),
                  index_col=[0], engine='python')

#%% IMPORT FUNCTIONS AND VARIABLES

INTRO_BLOCK_TXT = INTRO_BLOCK_TXT_EXP3[CONFIG['LANGUAGE']]
#%% INITIALIZE EXPERIMENT AND CREATE DATA FOLDER
exp = expyriment.design.Experiment(name="Third Experiment",
                                   background_colour=DARK_GRAY_B,
                                   foreground_colour=BLACK)
expyriment.control.initialize(exp)
expyriment.control.start(skip_ready_screen=True)
subject = exp.subject
timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
CONFIG['data_dir'] = op.join(CONFIG['DataPathRoot'], "Task2",f"subject{subject}",f"{subject}_{timestamp}")
CONFIG['fake_triggers_filename'] = op.join(CONFIG['data_dir'], f"{subject}_{timestamp}_fake_triggers.csv")

os.makedirs(CONFIG['data_dir'], exist_ok=True)

#%% INITIALISE EYETRACKER FILE
if args.is_eyelink:
    tracker, edfFileName = init_eyelink(exp)
    start_recording()

#%% INITIALIZE RESPONSE OBJECT VIA PORTS IF MEG, KEYBOARD OTHERWISE
trigger_port = init_port(args, CONFIG['fake_triggers_filename'])
# Get response object
if args.no_meg:
    print("\n#############\nUSING KEYBOARD FOR RESPONSES \n#############")
    resp_object = exp.keyboard
else:
    print('define response button')
    resp_object = ResponseFromPort(args, exp, ADDRESS_ANSWER_PORT_1, 
                                   ADDRESS_ANSWER_PORT_2, ADDRESS_ANSWER_PORT_3, 
                                   CONTROL_KEYS)

# RESPONSE_KEYS = dict(**RESPONSE_KEYS[CONFIG['OPTION']], **CONTROL_KEYS) 
   
#%% PREPARE EXPERIMENT : LOAD STIMULI, INSTRUCTIONS, SCREENS AND BUILD BLOCKS
# Define response mapping for the demo and the first part     
nb_of_presented_parts = 0
define_stimulus_response_mapping_from_part_nb \
    = {**{even_key : 'HouseLeft' for even_key in [0,2,4,6,8,10,12]},
       **{odd_key : 'FaceLeft' for odd_key in [1,3,5,7,9,11]}}
    
stimulus_response_mapping = define_stimulus_response_mapping_from_part_nb[nb_of_presented_parts]

if stimulus_response_mapping=='HouseLeft':
     key_response_mapping = {'left': 'house', 'right': 'face'}
else:
     key_response_mapping = {'left': 'face', 'right':'house'}
     
# Load instructions 
# LIST_OF_INSTRUCTIONS = pd.read_csv(f"{CONFIG['InstructionsPath']}\InstructionsDataFrames\{CONFIG['LANGUAGE']}NtVol{stimulus_response_mapping}.csv")['Instructions']
 
# Select a demo dataframe
ALL_DEMO_FILES = [file for file in glob.glob(op.join(CONFIG['DemoFiles'],"*")) if CONFIG['EXP_ID'] in file]
DEMO_FILE = random.choice(ALL_DEMO_FILES)
DEMO_MORPHS = pd.read_csv(DEMO_FILE, index_col=0, engine='python')
  
# Create every screens 
screens = create_screens(exp, CONFIG)

# Create variable names
exp.data.add_variable_names(['block_nb', 'trial_nb', 'trial_id',
                             'time_morph_pst', 'response', 'rt', 'absolute_rt',
                             'explicit_report', 'explicit_report_rt'])

# Add stimuli of the demo to the experiment
demo_block = expyriment.design.Block(name='demo')
add_pictures_to_block(demo_block, DEMO_MORPHS['MorphsList'].dropna(), CONFIG)
exp.add_block(demo_block)

# Add stimuli of the experiment : for one subject, several prepared lists can be used for a longer experiment in MEG
exp_blocks = {}
for list_nb in range(subject, subject+NB_OF_LISTS_TO_PRESENT) :
    MORPHS_FILE = op.join(CONFIG['SimDataFiles'], f"subject{list_nb}", f"subject{list_nb}_notone_exp3.csv")
 
    MORPHS_FRAME = pd.read_csv(MORPHS_FILE, index_col=0, engine='python')
    block_nbs_in_exp = [f'block{n+(list_nb-subject)*NB_OF_BLOCKS_EXP3}' for n in range(1, NB_OF_BLOCKS_EXP3+1)]
    for i, block_nb_in_list in enumerate(MORPHS_FRAME['block_nb'].unique()):
        block = expyriment.design.Block(name=block_nbs_in_exp[i])
        block_morphs_frame = MORPHS_FRAME[MORPHS_FRAME['block_nb']==block_nb_in_list]
        add_pictures_to_block(block, block_morphs_frame['trial_id'], CONFIG)
        exp.add_block(block)
        exp_blocks[block_nbs_in_exp[i]] = block

#%% BEGIN EXPERIMENT : PRESENT INSTRUCTIONS, INTRODUCE EACH BLOCK AND RUN TRIALS
# Present instructions, introduce each block and run trials
# show_instructions(exp, CONFIG['InstructionsPicturesPath'], LIST_OF_INSTRUCTIONS)
# introduce_session(exp, INTRO_DEMO_TXT, CONFIG)

# send trigger to  edf file
if args.is_eyelink:
    getEYELINK().sendMessage("T0received")
    print("got thru T0 message\n")

#reset timer for trial timing
exp.clock.reset_stopwatch()
# get the start time for checking total session duration
exp_start_time = exp.clock.stopwatch_time


# run_trials_of_block_exp3(exp, screens, demo_block, resp_object, stimulus_response_mapping, key_response_mapping,
                         # trigger_port, STIMULUS_EVIDENCE_LEVELS, CONFIG, args, is_demo=True)
# explicit_report, explicit_report_rt = rate_confidence(exp, resp_object, EXPLICIT_REPORT_KEYS, CONFIG, is_demo=True)        
# exp.data.add(['None']*7 + [explicit_report, explicit_report_rt])
idx_of_blocks_ending_part_in_one_list = [block_nbs_in_part[-1] for block_nbs_in_part in EXP_STRUCTURE]
idx_of_blocks_ending_part_in_exp = [block_nb + n*15 for n in range(NB_OF_LISTS_TO_PRESENT)
                                    for block_nb in idx_of_blocks_ending_part_in_one_list]

introduce_session(exp, INTRO_BLOCK_TXT['Begin'], CONFIG)         
time_from_explicit_report = 0                     
for i, block in enumerate(exp_blocks.values()): 
    if stimulus_response_mapping=='HouseLeft':
         key_response_mapping = {'left': 'house', 'right': 'face'}
    else:
         key_response_mapping = {'left': 'face', 'right':'house'}
         
    time_from_explicit_report = \
        run_trials_of_block_exp3(exp, screens, block, resp_object, 
                                 stimulus_response_mapping, key_response_mapping,
                                 trigger_port, STIMULUS_EVIDENCE_LEVELS, CONFIG, 
                                 args, is_demo=False,
                                 time_from_explicit_report=time_from_explicit_report)

    if i in idx_of_blocks_ending_part_in_exp[:-1]: # End (not pause) the experiment if it is the last part
        nb_of_presented_parts +=1
        introduce_session(exp, INTRO_BLOCK_TXT['Break'], CONFIG)
        stimulus_response_mapping = define_stimulus_response_mapping_from_part_nb[nb_of_presented_parts]
            
# show_instructions(exp, 'Epilogue')
expyriment.control.end()
new_path = op.join(CONFIG['data_dir'], exp.data.filename[exp.data.filename.find('Bay'):])
shutil.move(exp.data.fullpath, new_path) 
print(new_path)
