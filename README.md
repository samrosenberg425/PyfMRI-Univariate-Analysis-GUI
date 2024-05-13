# Python GUI For Univariate Analysis
This is a program written to run a univariate contrast for one task based run for one individual subject. There is additional functionality to set up the data and plot the results. The input data must be in the fmriprepped format and include an events file formatted as described below. 

***By Sam Rosenberg | University of Maryland/University of Rutgers, Newark***

## Files
### Lvl1AnalysisGUI.py
This file has the code for the frontend of the GUI. It does not actually perform any of the calculations but calls on functions fromn the class, Lvl1Analysis, from Lvl1Analysis.py. 

### Lvl1Analysis.py
This file has the class, Lvl1Analysis, that performs all of the calculations necessary. 

## Installation
Download both files into the same directory and ensure the proper libraries are installed. 

## How to use the pipeline
Either run Lvl1AnalysisGUI.py either within a Python environment or from the command line using the following command:
```tcsh 
python3 Lvl1AnalysisGUI.py
```
Either of these run options will present the user with a gui based in the system's file viewer.\

#### Necessary data 
- fmriprep output for a subject
- events.tsv file with stimulus onsets, duration, and type as separate columns

### Once the GUI is open
1. Select the fmriprep and output directories using the file browser or by manually inputting the path
2. Enter the subject number
3. Enter the task name
4. Select commands you would like to run (described below)
5. *If needed*, enter the conditions for the contrast or the FWHM size of the smoothing kernel you would like to use. 
6. Click the button to run selected commands


## Usage Notes
This script is intended to be used to conduct a univariate contrast such as a words versus scramble task used as a VWFA localizer. It contains several functions outlined below
### Input
#### Data
- fmriprepped functional data \
- events.tsv file in bids file structure(or accessible directory) that has onset, duration, and trial_type columns(with two trial types)
#### GUI Inputs
- fmriprep directory
- output directory
- subject number
- task name
- Conditions(*optional*)
- Smoothing FWHM(*optional*)
- Select Commands

## Functions
### copy_events_files():
    
- Moves the events timing files from the bids directory to the fmriprep directory. All files paths are predefined to match the file structure of neurodev.

- *Outputs*: 
  - NONE

### extract_event_data():
    
- Takes the events files(copied in the last step), and makes a .1D file for each stimulus that contains their onset times as a row vector delimited by spaces(ie. 1.2 3.4 5.6 7.8...)

- *Outputs*:
    - /fmriprep directory/subject/func/words.1D
        - Text file with row vector of word onset times delimited with spaces
    -  /fmriprep directory/subject/func/scramble.1D
        - Text file with row vector of scramble onset times delimited with spaces

### smooth(kernel_size='6.000'):
    
- Writes a .csh script(denoted {subject}_smooth.csh) calling afni's 3dmerge to blur the  functional image to FWHM of the specified kernel size(if none are specified then the default of '6.000' is used)

- *Outputs*:
    - /fmriprep directory/subject/{subject}_smooth.csh
        - Script to smooth functional data(using AFNI's 3dBlurInMask)
    - /fmriprep directory/subject/func/sm_${subject}_task-{task}_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz
        - Smoothed functional file

### extract_reg():
    
- Takes the regressors output from fmriprep, and makes a new file, confounds.1D, that isolates the regressors of interest:
    - 'trans_x', 'trans_y', 'trans_z' --> x,y,z linear movement
    - 'rot_x', 'rot_y', 'rot_z' --> roll, pitch, yaw
    - 'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1'
    - 'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1'
    - 'a_comp_cor_08', 'a_comp_cor_09', 'a_comp_cor_10' --> (top 3 csf compcor)
    - 'csf', 'framewise_displacement'

- *Outputs*:
    - /fmriprep directory/subject/func/confounds.1D
        - Text file with column vectors of regressors

### deconvolve():
    
- Writes a .csh script(denoted {subject}_decon.csh) calling afni's 3ddeconvolve function to devonvolve the data using the word and scramble onset times (words.1D & scramble.1D) and the specified regressors(confounds.1D). The script is then saved in the subject's fmriprep folder along with its outputs.

- *Outputs*:
    - /fmriprep directory/subject/{subject}_decon.csh
        - AFNI 3ddeconvolve script created for the contrast
    - /fmriprep directory/subject/{subject}.outputs
        - Results of 3ddeconvolve script
    - /fmriprep directory/subject/{subject}.xmat.1D
        - Plots of all regressors



