# Generic-Python-Remote-Script
Ableton Live - Generic Configurable Python Scripts
MIDI Remote script which can be customized for any MIDI controller.

# To install in Live,
1) Choose a name for you script. For example we will choose "MyName".

2) Edit the the "Generic.py" file and replace all instances of the word "Generic" with "MyName" (the name you choose at point 1).

3) Rename the "Generic.py" to "MyName.py" (as you choose at point 1).

4) Edit the "__init__.py" script replacing "Generic" with "MyName" (or any other name consistent to step 1 above)

5) Rename/name the directory containing all the .py scripts as "MyName" (the name you choose at point 1)

6) Edit the mappings as explained in the CUSTOMIZE INSTRUCTIONS reported below.

7) Copy the directory into Live MIDI script folder:

On a MAC machine: /Contents/App-Resources/MIDI Remote Scripts/

On a Windows machine: \ProgramData\Ableton\Live x.x\Resources\MIDI Remote Scripts\

8) Select the script as Control Surface in Live preferences, and couple it with the MIDI controller you want to use.

# CUSTOMIZE INSTRUCTIONS
To customize for MIDI associations to functions the file to edit is the "MIDI_Map.py" script.
This requires you to:

1. Define The dimension of the surfaces (for the "session view box").
The clip session matrix definition must be matrix MATRIX_DEPTH * TRACK_NUMBER
Further all other vectors referring to tracks must be TRACK_NUMBER long.

To define this set:
MATRIX_DEPTH = X #number of scenes in the box (X >= 0)
TRACK_NUMBER = Y #number of tracks for Mixer mapping (Y >= 0)

2. Define the special functions / buttons (only buttons, no sliders):
NUMBER_BUTTONS = 40 #number of buttons in BUTTON_VECTOR
NUMBER_SLIDERS = 4 #number of sliders in SLIDER_VECTOR

3. Define the Device control banks and parameter number:
BANKS_NUMBER = 8 #number of parameter banks
PARAMS_NUMBER = 8 #number of parameters per bank

4. Define Pad numbers for drum rack support
PAD_X_NUMBER = 4 #number of pad columns
PAD_Y_NUMBER = 4 #number of pad rows

5. When assigning MIDI messages (notes or CC) to controls in Live, keep in mind that in general each association requires THREE values to be specified:

- The MIDI message Number for Note or CC (Control Change) to be used (-1 for no association)
- The Type of MIDI message (Type 0 == MIDI notes, Type 1 == MIDI CC)
- The Channel, in the range 0 to 15 (corresponding to MIDI channels 1 to 16)

Example: the following associates the MIDI Notes 36 (C1) and 38 (D1) to Scene Launch of scene 1 and 2, using MIDI channel 1.

SCENELAUNCH = (36, #Scene 1
               38, #Scene 2
               -1, #Scene 3
               -1, #Scene 4
               -1, #Scene 5
               -1, #Scene 6
               -1, #Scene 7
               -1, #Scene 8
               -1, #Scene 9
               -1, #Scene 10
               )

SCENELAUNCH_TYPE = (0, #Scene 1
               0, #Scene 2
               0, #Scene 3
               0, #Scene 4
               0, #Scene 5
               0, #Scene 6
               0, #Scene 7
               0, #Scene 8
               0, #Scene 9
               0, #Scene 10
               )

SCENELAUNCH_CH = (0, #Scene 1
               0, #Scene 2
               0, #Scene 3
               0, #Scene 4
               0, #Scene 5
               0, #Scene 6
               0, #Scene 7
               0, #Scene 8
               0, #Scene 9
               0, #Scene 10
               )

A similar setup applies to all other associations.
