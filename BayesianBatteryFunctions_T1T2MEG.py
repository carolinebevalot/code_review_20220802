#!\usr\bin\env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:31:45 2019

@author: carolinebevalot
"""
from expyriment import design, control, stimuli, io, misc

import random
import numpy as np
# import simpleaudio as sa
import pickle
import glob
import os
import csv
import datetime
from itertools import accumulate
from expyriment.misc._timer import get_time
from psychopy import parallel
import os.path as op
from BatteryScript.BayesianBatteryVariables_COMPUTERMEG import*


def translate_stimulus_features_into_stimulus_trigger(stimulus_category, evidence_level,
                                                      stimulus_response_mapping):
    """This function translates the task conditions into a binary code
    which will be converted into a decimal to be send as a trigger 
    when a stimulus is presented. 
    The first bit codes for a stimulus trigger (='0' for a response trigger)
    The second bit codes for the stimulus-response mapping 
    (='0' when left button corresponds to face and ='1' when left button corresponds to house)
    The third bit of a stimulus trigger codes for the category of the stimulus 
    (='0' for a a face and ='1' for a house)
    The fourth and the fifth bit of the stimulus trigger 
    code for the level of evidence of the stimulus
    ('00' : very ambiguous, '01' : ambiguous, '10':obvious, '11':very_obvious)
    """
    evidence_level_to_binary_code = {'very_ambiguous': '00',
                                      'ambiguous':'01',
                                      'obvious': '10',
                                      'very_obvious': '11'}

    binary_stimulus_trigger = ['0']*4
    binary_stimulus_trigger[0] = '1' 
    binary_stimulus_trigger[1] = '0' if stimulus_response_mapping =='FaceLeft' else '1' 
    binary_stimulus_trigger[2] = '0' if stimulus_category =='face' else '1' 
    binary_stimulus_trigger[3] = evidence_level_to_binary_code[evidence_level] 

    binary_stimulus_trigger = ''.join(binary_stimulus_trigger)
    if len(binary_stimulus_trigger) != 5:
        print(f'WARNING : ERROR IN THE BINARY CODE (length={len(binary_stimulus_trigger)})')
    
    decimal_stimulus_trigger =  int(binary_stimulus_trigger, 2) 
    
    # print(f'bin : {binary_stimulus_trigger}; dec : {decimal_stimulus_trigger}')
    return decimal_stimulus_trigger
    


def translate_trigger_into_stimulus_or_response_features(decimal_trigger):
    """This function translates the task conditions into a binary code
    which will be converted into a decimal to be send as a trigger 
    when a stimulus is presented. 
    The first bit codes for a stimulus trigger (='0' for a response trigger)
    The second bit codes for a response trigger (='0' for a stimulus trigger)
    The third bit of a stimulus trigger codes for the category of the stimulus 
    (='0' for a a face and ='1' for a house)
    The fourth and the fifth bit of the stimulus trigger 
    code for the level of evidence of the stimulus
    ('00' : very ambiguous, '01' : ambiguous, '10':obvious, '11':very_obvious)
    """
    task_features = {}
    binary_trigger = bin(decimal_trigger)
    binary_trigger = binary_trigger[binary_trigger.find('b')+1:]
    
    if binary_trigger[0] == '1':
        task_features['trigger_type'] = 'stimulus_trigger'
    else : 
        print('ERROR : trigger is neither a response trigger nor a stimulus trigger')
    
    if task_features['trigger_type'] == 'stimulus_trigger':
        binary_code_to_evidence_level = {'00' : 'very_ambiguous',
                                         '01' : 'ambiguous',
                                         '10' : 'obvious',
                                         '11' : 'very_obvious'}
        task_features['stimulus_response_mapping'] = 'FaceLeft' if binary_stimulus_trigger[1] == '0' else 'HouseLeft'  
        task_features['stimulus_category'] = 'face' if binary_trigger[2]=='0' else 'house'
        task_features['evidence_level'] = binary_code_to_evidence_level[binary_trigger[3:]]
    
    elif task_features['trigger_type'] == 'response_trigger':
        task_features['response_presence'] = False if binary_trigger[2] == '0' else True
        task_features['subject_response'] = 'left' if binary_trigger[3] == '0' else 'right'
        task_features['stimulus_response_mapping'] = 'FaceLeft' if binary_trigger[4] == '0' else 'HouseLeft'
        task_features['response_category'] \
            = 'face' if ((task_features['stimulus_response_mapping']=='FaceLeft' 
                          and task_features['subject_response']=='left')
                         or (task_features['stimulus_response_mapping']=='HouseLeft' 
                             and task_features['subject_response']=='right'))\
                else 'house'

    return task_features
    

def draw_pictures_for_response(stimulus_response_mapping, CONFIG):
    """Prepare pictograms for response screen and
    inverse left\right side between subjects."""
    if stimulus_response_mapping == 'HouseLeft':
        pos1 = LEFT_POS[CONFIG['OPTION']]
        pos2 = RIGHT_POS[CONFIG['OPTION']]
    else:
        pos1 = RIGHT_POS[CONFIG['OPTION']]
        pos2 = LEFT_POS[CONFIG['OPTION']]

    house = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "House.png"),
                                       position=pos1)
    face = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "Face.png"),
                                      position=pos2)
    house.scale(SCALE_ANSWER_PICTURES[CONFIG['OPTION']])
    face.scale(SCALE_ANSWER_PICTURES[CONFIG['OPTION']])
    
    return house, face


def create_screens(exp, CONFIG):
    """Create te different screens : one to plo morphs, one for answers,
    one fixation screen with the target plotted."""
    screens = {}
    for screen in ['morph', 'fixation', 'introduce_session']:
        b_screen = stimuli.BlankScreen()
        if screen !='introduce_session':
            plot_target(b_screen, CONFIG)
            plot_diode_band(exp, b_screen)
        screens[screen] = b_screen

    for stimulus_response_mapping in ['HouseLeft', 'FaceLeft']:
        picto_house, picto_face = draw_pictures_for_response(stimulus_response_mapping, CONFIG)

        response_screens = {screen : stimuli.BlankScreen()
                            for screen in ['left', 'right', 'left_right', 'no_answer']}
        if stimulus_response_mapping=='HouseLeft':
            stim_resp_screen = {'left': picto_house, 'right': picto_face}
            key_response_mapping = {'left': 'house', 'right': 'face'}
        else:
            stim_resp_screen = {'left': picto_face, 'right': picto_house}
            key_response_mapping = {'left': 'face', 'right':'house'}
            
        for side in ['left', 'right']:
            other_side = [other_side for other_side in ['left', 'right'] if other_side !=side][0]
            stim_resp_screen[other_side].plot(response_screens[side])
            stim_resp_screen[side].plot(response_screens['left_right'])
        
        for side in ['left', 'right']:
            blurred_stim = stim_resp_screen[side]
            blurred_stim.blur(BLUR_LEVEL[CONFIG['OPTION']])
            blurred_stim.plot(response_screens[side])
            

        for screen in response_screens.keys():
            plot_target(response_screens[screen],CONFIG)
            plot_diode_band(exp, response_screens[screen])
        
        hourglass = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "Hourglass.png"),
                                      position=NO_ANSWER_POS)
        hourglass.scale(SCALE_HOURGLASS[CONFIG['OPTION']])
        hourglass.plot(response_screens['no_answer'])

        screens[stimulus_response_mapping]=response_screens
        screens[f'Demo{stimulus_response_mapping}']=response_screens

    return screens


def add_pictures_to_block(block, block_images, CONFIG, localizer=False):
    """ Function which selects pictures for one block and saves each as a
    stimulus of one block trial. It saves the name of the picture.
    The {easy_pic_nb} first pictures are easier to enhance prior learning.
    diff level is the level of difficulty (likelihood) of these first pictures.
    It should be between 0 and 1.
    For example for diff_level = 0.3, the function select houses with
    likelihood > 0.7 or faces with likelihood <0.3."""

    # Add every image as stimulus of one trial and add them to the block
    scale = SCALE_MORPH[CONFIG['OPTION']]
    picture_path = CONFIG['LocalizerStimPath'] if localizer else CONFIG['MorphsPath']
    for image in block_images:
        trial = design.Trial()
        morph = stimuli.Picture(op.join(picture_path, image))
        morph.scale(scale)
        morph.preload()
        trial.add_stimulus(morph)
        # save picture name without path
        trial.set_factor('name', image)
        block.add_trial(trial)




def introduce_session(exp, interblocks_txt, CONFIG, background=True):
    """Function which show the map in background, introduce the session,
    explaining if necessary change of priors and wait for button press
    to begin"""
    screen = stimuli.BlankScreen()
    
    title = stimuli.TextLine(interblocks_txt[0], position=INTRO_BLOCK_POS1,
                             text_bold=True, text_size=TXT_SIZE, text_colour=TXT_COLOR)

    session1 = stimuli.TextLine(interblocks_txt[1], position=INTRO_BLOCK_POS2,
                                text_bold=True, text_size=TXT_SIZE, text_colour=TXT_COLOR)

    session2 = stimuli.TextLine(interblocks_txt[2], position=INTRO_BLOCK_POS3,
                                text_bold=True, text_size=TXT_SIZE, text_colour=TXT_COLOR)   
                                           
        
    play = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "play_black.png"),
                           position=PLAY_POS[CONFIG['OPTION']])
        
    if background :
        light_citymap = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "light_citymap_notone.png"),
                                position=(0, 0))
        light_citymap.scale(BACKGROUND_SCALE)
        light_citymap.plot(screen)
    
    for element in [title, session1, session2, play]:
        element.plot(screen)
    
    plot_diode_band(exp, screen)
    screen.present()
    exp.keyboard.wait([CONTROL_KEYS['next_block']])

    
def plot_diode_band(exp, screen):
    
    x_screen_max, y_screen_max = exp.screen.center_x, exp.screen.center_y
    diode_band_size = (x_screen_max*2, DIODE_SCALE * x_screen_max + DIODE_MARGIN)
    diode_band_position = (0,-(y_screen_max - diode_band_size[1]/2))

    diode_band = stimuli.Rectangle(diode_band_size, colour=BLACK,
                               position=(diode_band_position))
    diode_band.plot(screen)
    # screen.present()

def flash_diode_white_square(exp, screen):
    
    x_screen_max, y_screen_max = exp.screen.center_x, exp.screen.center_y
    diode_square_size = DIODE_SCALE * x_screen_max
    diode_position = (-(x_screen_max-diode_square_size/2), -(y_screen_max-diode_square_size/2))
    diode_square = stimuli.Rectangle((diode_square_size,)*2, colour=WHITE,
                                    position=diode_position)
    diode_square.plot(screen)
    # screen.present()
    # exp.clock.wait(DIODE_TIME)
    # plot_diode_band(exp, screen)
    

def plot_target(screen, CONFIG):
    """Function which plot a target"""
    dot = stimuli.Circle(radius=DOT_RADIUS[CONFIG['OPTION']], colour=BLACK)
    circle = stimuli.Circle(radius=CIRCLE_RADIUS[CONFIG['OPTION']], colour=BLACK, line_width=2)
    dot.plot(screen)
    circle.plot(screen)


    
def ask_explicit_report(exp, resp_object, CONFIG, stimulus_response_mapping, 
                         is_demo=False):
    """Function which presents a scale to rate confidence
    and saves the confidence rate when a position on the scale is rated."""
    
    if stimulus_response_mapping == 'HouseLeft':
        house_position = LEFT_POS_EXPLICIT_REPORT
        face_position = RIGHT_POS_EXPLICIT_REPORT
    else : 
        face_position = LEFT_POS_EXPLICIT_REPORT
        house_position = RIGHT_POS_EXPLICIT_REPORT

    screen = stimuli.BlankScreen()
    
    explicit_report_Q = EXPLICIT_REPORT_QUESTION_DEMO[CONFIG['LANGUAGE']]['exp3'] if is_demo\
                else EXPLICIT_REPORT_QUESTION[CONFIG['LANGUAGE']]['exp3']
                
    question \
        = stimuli.TextBox(explicit_report_Q, EXPLICIT_REPORT_Q_AREA,
                          position=(POSITION_BAR_EXPLICIT_REPORT[0], 
                                    POSITION_BAR_EXPLICIT_REPORT[1]+100), 
                          text_size=TXT_SIZE, text_colour=TXT_COLOR)
        
    house_prop = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'],"House.png"),
                                 position=(house_position, POSITION_BAR_EXPLICIT_REPORT[1]))
    face_prop = stimuli.Picture(op.join(CONFIG['PictoPriorsResponsesPath'], "Face.png"),
                                position=(face_position, POSITION_BAR_EXPLICIT_REPORT[1]))
    
    house_prop.scale(SCALE_PICTO_EXPLICIT_REPORT), face_prop.scale(SCALE_PICTO_EXPLICIT_REPORT)

    for stim in [question, house_prop, face_prop]:
        stim.plot(screen)
    for explicit_report_btn_pos in EXPLICIT_REPORT_BUTTON_POSITIONS :
        explicit_report_btn = stimuli.Rectangle(EXPLICIT_REPORT_BUTTON_SIZE, colour=BLACK,
                                             position=explicit_report_btn_pos)
        explicit_report_btn.plot(screen)
        
    plot_diode_band(exp, screen)
    screen.present()
    explicit_report, explicit_report_rt = resp_object.wait(EXPLICIT_REPORT_KEYS[CONFIG['OPTION']].values())   
    for i, value in enumerate(EXPLICIT_REPORT_KEYS[CONFIG['OPTION']].values()):
        if explicit_report == value:
            explicit_report_btn = stimuli.Rectangle(EXPLICIT_REPORT_BUTTON_VALIDATION_SIZE, colour=BLACK,
                                                    position=EXPLICIT_REPORT_BUTTON_POSITIONS[i])
            explicit_report_btn.plot(screen)
    screen.present()
    exp.clock.wait(VALIDATION_EXPLICIT_REPORT_TIME)  


    return explicit_report, explicit_report_rt

def run_trials_of_block_exp3(exp, screens, block, resp_object, 
                             stimulus_response_mapping, key_response_mapping, trigger_port, 
                             stimulus_evidence_levels, CONFIG, args,
                             is_demo=False,
                             time_from_explicit_report=0):
    """Function which runs a block. For each trial, it presents the morph,
    presents the response window, wait for the right or left answer and record
    them with the corresponding response time.
    The absolute response time begins from the presentation of the morph.
    One trial out of {EXPLICIT_REPORT_RECURRENCE}, it asks for confidence rating.
    """
    explicit_report_recurrence = len(block.trials) if is_demo else EXPLICIT_REPORT_RECURRENCE
    previous_time_morph_pst = 0
    for trial_nb, trial in enumerate(block.trials):
        time_begining = exp.clock.stopwatch_time
        screens['fixation'].present()
        
        # during fixation prepare next steps
        trial.stimuli[0].plot(screens['morph'])
        plot_target(screens['morph'],CONFIG)
        evidence_level, stimulus_category \
            = stimulus_evidence_levels.loc[trial.get_factor('name'),:]
        flash_diode_white_square(exp, screens['morph'])
        stimulus_trigger \
            = translate_stimulus_features_into_stimulus_trigger(stimulus_category, evidence_level,
                                                                stimulus_response_mapping)

        #  wait remaining time
        intertrial_time_to_wait \
            = BB_INTER_TRIALS_TIME - TRIGGER_DURATION - (exp.clock.stopwatch_time-time_begining)
        exp.clock.wait(intertrial_time_to_wait)
        time_after_ITI = exp.clock.stopwatch_time
        print(f'ITI at 580 : {time_after_ITI-time_begining}')
        
        trigger_port.send(stimulus_trigger)
        exp.clock.wait(TRIGGER_DURATION)  
        trigger_port.send(TRIGGER_DICT['baseline'])
        time_after_trigger = exp.clock.stopwatch_time
        print(f'trigger at 20 : {time_after_trigger - time_after_ITI}')

        time_morph_pst, time_process = exp.clock.stopwatch_time, screens['morph'].present()

        # if args.is_eyelink:
        #     getEYELINK().sendMessage(f"{block} trial {trial.id};")
                                
        key, rt, absolute_rt \
            = select_response(exp, screens, resp_object, 
                              stimulus_response_mapping, key_response_mapping, trigger_port,
                              CONFIG, args, time_morph_pst, is_demo)
                                                
        if key==CONTROL_KEYS['next_block']:
            print(f"------------> WARNING: skipping {block.name}")
            break
        time_from_explicit_report += random.choice([1,]*4 + [2])
        if time_from_explicit_report >= explicit_report_recurrence :
            explicit_report, explicit_report_rt = \
                ask_explicit_report(exp, resp_object, CONFIG, stimulus_response_mapping, is_demo)
            time_from_explicit_report = 0
            exp.data.add([block.name, trial.id, trial.get_factor('name'),
                                  time_morph_pst, key, rt, absolute_rt,
                                  explicit_report, explicit_report_rt])
            screens['fixation'].present()

            exp.clock.wait(BB_INTER_TRIALS_TIME)

        else:
            exp.data.add([block.name, trial.id, trial.get_factor('name'),
                              time_morph_pst, key, rt, absolute_rt])
            time_end_trial = exp.clock.stopwatch_time
            print(f'Total time at 1700ms : {time_end_trial-time_begining}')
            print(f'SOA from time morph pst : {time_morph_pst-previous_time_morph_pst}')
            previous_time_morph_pst = time_morph_pst
            
    return time_from_explicit_report

def select_response(exp, screens, resp_object, stimulus_response_mapping, key_response_mapping,
                    trigger_port, CONFIG, args, time_morph_pst, demo=False):
    """Function which presents the response screen as soon as the morph as been
    presented. It registers any answer from the presentation with saving
    absolute response time.
    If no early answer was given, it waits time_morph and presents the response
    screen. It waits for the right or left answer with a maximum duration
    and return the answer with the corresponding response times (relative
    and absolute). """
    response_keys = RESPONSE_KEYS[CONFIG['OPTION']]
    # Create response screens
    response_screens = screens[stimulus_response_mapping] 
    # Catch anticipated answers (during the morph presentation)
    key, rt = resp_object.wait(response_keys.values(), 
                                duration=MORPH_PRESENTATION_TIME)# - (exp.clock.stopwatch_time-time_morph_pst))
    absolute_rt = exp.clock.stopwatch_time 
    # If anticipated answer, catch control keys and wait until the end of the morph pst
    if key : 
        rt = rt - MORPH_PRESENTATION_TIME
        print(f'---->>>*******{key,rt}')
        exp.clock.wait(MORPH_PRESENTATION_TIME - (exp.clock.stopwatch_time-time_morph_pst))
        time_after_stim_pst = time_after_answer = exp.clock.stopwatch_time
    
    # If no anticipated answer, present the response screen   
    else: 
        time_after_stim_pst = exp.clock.stopwatch_time
        time_process = response_screens['left_right'].present()
        print(time_process)
        key, rt = resp_object.wait(response_keys.values(), 
                                   duration=RESPONSE_TIME-time_process)
        absolute_rt = exp.clock.stopwatch_time
        time_after_answer = exp.clock.stopwatch_time
        print(f'Response screen < 800 :{time_after_answer - time_after_stim_pst}')
    print(f'Morph presentation at 150 : {time_after_stim_pst - time_morph_pst}')

    # Show selected answer
    print(f"{key} in {response_keys['left'], response_keys['right']}?")
    if key in [response_keys['left'], response_keys['right']]: 
        for side in ['left', 'right']:
            if key == response_keys[side]:
                response = key_response_mapping[side]
                time_process = response_screens[side].present()
                time_to_SOA = RESPONSE_TIME - (exp.clock.stopwatch_time -  time_after_stim_pst)
                print(f'time_to_SOA : {time_to_SOA}')
                exp.clock.wait(time_to_SOA)
                print(f'Validation {side}')   
                    
    elif key and key not in [response_keys['left'], response_keys['right']]:
        print(f'wrong key : {key}')
        time_process = response_screens['left_right'].present()
        key, rt = resp_object.wait(response_keys.values(), 
                                   duration=RESPONSE_TIME-(exp.clock.stopwatch_time -  time_after_stim_pst)- time_process)
        absolute_rt = exp.clock.stopwatch_time
        if key in [response_keys['left'], response_keys['right']]: 
            for side in ['left', 'right']:
                if key == response_keys[side]:
                    response = key_response_mapping[side]
                    time_process = response_screens[side].present()
                    time_to_SOA = RESPONSE_TIME- time_process - (time_after_answer-time_after_stim_pst)
                    time_to_SOA = RESPONSE_TIME - (exp.clock.stopwatch_time -  time_after_stim_pst)
                    print(f'time_to_SOA_bis : {time_to_SOA}')
                    print(f'time_to_SOA : {time_to_SOA}')
                    exp.clock.wait(time_to_SOA)
                    print(f'Validation {side}')   
        else:
            response = None

    else:
        response = None

    time_after_answer_val=exp.clock.stopwatch_time
    print(f'Response validation at 800 : {time_after_answer_val-time_after_stim_pst}')

    print(response)

    return response, rt, absolute_rt


def show_instructions(exp, instructions_img_path, list_of_instructions):
    """Function which gathers instructions pictures for the experiment
    and presents it. If tone_instructions = True, the instructions are different
    for exp1 with tone and without tone. if withtone = True, in exp1,
    the function plays each tone during the instructions"""
    instructions = stimuli.BlankScreen()
    
    for ins_nb, picture in enumerate(sorted(list_of_instructions)):
        ins = stimuli.Picture(op.join(instructions_img_path, picture), position=(0, 0))
        ins.scale_to_fullscreen(keep_aspect_ratio=False)
        ins.plot(instructions)
        instructions.present()
        if ins_nb == len(list_of_instructions)-1:
            event_id, pos, rt = exp.mouse.wait_press(buttons=0)
            event_id, pos, rt = exp.mouse.wait_press(buttons=0)
        else:
            event_id, pos, rt = exp.mouse.wait_press(buttons=0)
            
            
#%% MEG functions
class MockPort:
    """Writes triggers to a file when no meg is connected"""
    i = 0

    def __init__(self, args, filename):
        self.items_list = []
        # fname = "data\mock_port_"
        # fname += args.exp_name+ '_'
        # fname += timestamp+'.csv'
        file = (open(filename, 'w'))
        self.csvwriter = csv.writer(file, delimiter=',')
        self.csvwriter.writerow(["index", "time", "value", "decoded"])
        # file.close()
        # self.csvwriter = csv.writer(open(fname, 'w'), delimiter=',')
        # self.csvwriter.writerow(["index", "time", "value", "decoded"])

    def send(self, value):
        s = ""
        # file = open(fname, 'w')
        self.csvwriter.writerow([self.i, datetime.datetime.now().isoformat(), value, s])
        self.i = self.i + 1
        # file.close()

def init_port(args, file, address=ADDRESS_TRIGGER_PORT):
    # Connect to the MEG depending on the parameter
    # port = None
    # serial_handle = None
    if not args.no_meg:
        try:
            port = io.ParallelPort(address=address)
        except RuntimeError:
            print("\nERROR: could not connect to the parallel port 0x0378")
            exit(1)
        port.send(0)
    else:
        print("\n########################################################")
        print("# WARNING: mock port in use, no actual trigger is sent #")
        print("########################################################\n")
        port = MockPort(args, file)
    return port


def get_response_keys(exp, resp_object, CONFIG):
    stimuli.TextLine(RESP_KEYS_TXT[CONFIG['LANGUAGE']]['left'], position=[0,0], text_font=FONT, 
                     text_size=TXT_SIZE, text_colour=TXT_COLOR).present()
    left_button, _ = resp_object.wait()
    stimuli.TextLine('', position=[0,0], text_font=FONT, text_size=TXT_SIZE, text_colour=TXT_COLOR).present()
    stimuli.TextLine(RESP_KEYS_TXT[CONFIG['LANGUAGE']]['right'], position=[0,0], text_font=FONT, 
                     text_size=TXT_SIZE, text_colour=TXT_COLOR).present()
    right_button, _ = resp_object.wait()
    stimuli.TextLine('', position=[0,0], text_font=FONT, text_size=TXT_SIZE, text_colour=TXT_COLOR).present()
    return left_button, right_button


class ResponseFromPort(object):
    port1 = []
    port2 = []
    port3 = []


    def __init__(self, args, exp, port1Num, port2Num, port3Num, 
                 CONTROL_KEYS):
        
        self.exp = exp
        self.CONTROL_KEYS = CONTROL_KEYS
        ### only works at the MEG. WORKS ONLY IF THE SUBJECT PRESS THE RED BUTTONS ON BOTH RESPON PANELS
        self.port1 = parallel.ParallelPort(address=port1Num)
        self.port2 = parallel.ParallelPort(address=port2Num)
        self.port3 = parallel.ParallelPort(address=port3Num)
        _ = self.port1.readData()
        _ = self.port2.readData()
        _ = self.port3.readData()

        self.port1_baseline_value = self.port1.readData()
        self.port2_baseline_value = self.port2.readData()
        self.port3_baseline_value = self.port3.readData()

        self.port1_last_value = self.port1_baseline_value
        self.port2_last_value = self.port2_baseline_value
        self.port3_last_value = self.port3_baseline_value

        
    #----------------------------------------
    # Check if subject responded.
    # Return 0 if not; 1 or 2 if they did; and -1 if they clicked ESC
    def checkResponse(self):
        # if userPressedEscape():
        #     return -1
        #-- Check if exactly one button was pressed

        # Here we apply some small tricky correction for port whose return is always non-null
        # TODO check for consistency.
        resp1 = self.port1.readData() - self.port1_baseline_value
        resp2 = self.port2.readData() - self.port2_baseline_value
        resp3 = self.port3.readData() - self.port3_baseline_value

        if (resp1 != 0 and resp2 == 0 and resp1 != self.port1_last_value):# and resp3 == 0):
            self.port1_last_value = resp1
            print(f'port1_{resp1}')
            return f'port1_{resp1}'
        if (resp1 == 0 and resp2 != 0 and resp2 != self.port2_last_value):# and resp3 == 0):
            self.port2_last_value = resp2
            print(f'port2_{resp2}')
            return f'port2_{resp2}'
        if (resp1 == 0 and resp2 == 0 and resp3 != 0 and resp3 != self.port3_last_value):
            self.port3_last_value = resp3
            print(f'port3_{resp3}')
            return f'port3_{resp3}'

        if (resp1 != self.port1_last_value):
            self.port1_last_value = resp1
        if(resp2 != self.port2_last_value):
            self.port2_last_value = resp2
        if(resp3 != self.port3_last_value):
            self.port3_last_value = resp3

        return None



    def wait(self,  codes=None, duration=None, no_clear_buffer=False):
             
        """Homemade wait for MEG response buttons

        Parameters
        ----------
        codes : int or list, optional !!! IS IGNORED AND KEPT ONLY FOR CONSISTENCY WITH THE KEYBOARD METHOD
            bit pattern to wait for
            if codes is not set (None) the function returns for any
            event that differs from the baseline
        duration : int, optional
            maximal time to wait in ms
        no_clear_buffer : bool, optional
            do not clear the buffer (default = False)
        """
        start = get_time()
        rt = None
        if not no_clear_buffer:
            _ = self.port1.readData()
            _ = self.port2.readData()
            _ = self.port3.readData()
            self.exp.keyboard.clear()
        while True:
            ctrl = self.exp.keyboard.check(self.CONTROL_KEYS.values())
            if ctrl is not None:
                return ctrl, None

            found = self.checkResponse()
            if found : 
                rt = int((get_time() - start) * 1000)
                break

            if duration is not None:
                if int((get_time() - start) * 1000) > duration:
                    return None, None
            
        return found, rt

