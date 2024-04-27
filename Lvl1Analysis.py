#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:21:18 2024

@author: samrosenberg
"""

"""
-----------------------Univariate 1st Level PIPELINE---------------------------


INPUTS: fmriprepped data including a vwfa localizer scan(words vs. scramble conditions)
OUTPUTS: Univariate contrast of words vs. scramble conditions

-------------------------------------------------------------------------------
"""


import shutil
import sys
import os
import glob
from os import system
import pandas as pd
import subprocess
import numpy as np
import nibabel as nib
from nilearn import plotting, image
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox



class Lvl1Analysis():
    def __init__(self, fmriprep_dir, output_dir, task, subnum): 
        self.task=f"{task}"
        self.subject=f"sub-ntr{subnum}"
        # File path to the bids directory
        
        # File path to the fmriprep output directory
        # ***Make sure to leave /{self.subject}/ at the end of your file path
        self.fmriprep_dir = os.path.join(f'{fmriprep_dir}', f'{self.subject}')
        
        self.fmriprep_func_dir = os.path.join(f'{self.fmriprep_dir}', 'func')
        self.out_dir = os.path.join(f'{output_dir}', f'{self.subject}')
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
    def copy_event_files1(self, bids_dir):
        
        self.func_dir = os.path.join(f'{bids_dir}', f'{self.subject}', 'func')
        # Make a loop only going through the events files and copying them to fmriprep destinations
        events_files = [f for f in os.listdir(self.func_dir) if f.endswith('events.tsv')]
        for event_file in events_files:
            
            # Make name for paths with file name
            source_path=os.path.join(self.func_dir, event_file)
            destination_path=os.path.join(self.fmriprep_dir, 'func/', event_file)
            #destination_path_fig=os.path.join(self.fmriprep_dir, 'figures/', event_file)
            
            #Copy the files from bids to fmriprepped subject's func+figures directories
            shutil.copyfile(source_path, destination_path)
            #shutil.copyfile(source_path, destination_path_fig)
            
        print(f'Events files copied to {destination_path} \n')
        
    def copy_event_files(self):
        # Ask the user to select the BIDS directory
        #bids_dir = filedialog.askdirectory(title="Select BIDS Directory")
        bids_dir='/data/neurodev/NTR/bids'
        if not bids_dir:
            print("No directory selected. Operation canceled.")
            return

        # Construct the functional directory path based on the selected BIDS directory
        self.func_dir = os.path.join(bids_dir, self.subject, "func")

        # Make a loop only going through the events files and copying them to fmriprep destinations
        events_files = [f for f in os.listdir(self.func_dir) if f.endswith("events.tsv")]
        for event_file in events_files:
            # Make name for paths with file name
            source_path = os.path.join(self.func_dir, event_file)
            destination_path = os.path.join(self.fmriprep_dir, "func", event_file)

            # Copy the files from BIDS to fmriprep subject's func directory
            shutil.copyfile(source_path, destination_path)

        print(f"Events files copied to {self.fmriprep_dir}/func \n")

    #CHANGE THIS FUNCTION: make it a loop for all of the runs, 
    def extract_event_data(self, type1, type2):
        # Read events file in as dataframe
        data = pd.read_csv(self.fmriprep_func_dir + f'/{self.subject}_task-{self.task}_run-1_events.tsv', sep='\t')
    
        # type1 and type 2 ar ethe 2 condition types
        # Filter the data for the two words
        word_runs = data[data['trial_type'] == type1]['onset']
        scramble_runs = data[data['trial_type'] == type2]['onset']
    
        # Convert to numpy arrays
        word_row = word_runs.to_numpy()[None, ...]
        scramble_row = scramble_runs.to_numpy()[None, ...]
    
        # Save to files
        np.savetxt(self.fmriprep_func_dir + f'/{type1}.1D', word_row, delimiter=' ', fmt='%.2f')
        np.savetxt(self.fmriprep_func_dir + f'/{type2}.1D', scramble_row, delimiter=' ', fmt='%.2f')

    def smooth(self,kernel_size='6.000'): 



        smooth_script=f"""#!/bin/tcsh
set datadir = {self.fmriprep_func_dir}
set polort = 0
set procs = 1
set subj = {self.subject}
set task = {self.task}
cd $datadir
set outdir = {self.out_dir}

3dBlurInMask \
-mask {self.fmriprep_dir}/anat/${{subj}}_acq-1norm_space-MNI152NLin2009cAsym_res-1_desc-brain_mask.nii.gz \
-input ${{datadir}}/${{subj}}_task-${{task}}_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz \
-FWHM {kernel_size} \
-prefix ./sm_${{subj}}_task-${{task}}_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz \
${{datadir}}/${{subj}}_task-${{task}}_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz \
"""
        fpath=os.path.join(self.out_dir, f'{self.subject}_blur.csh')
        
        with open(fpath, 'w') as file:
            file.write(smooth_script)
        
        try:
            subprocess.run(['tcsh', f"{fpath}"], check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running the smoothing script: {e} \n")
        else:
            print("The smoothing script has been executed successfully. \n")

    # Extract covariate data

    def extract_reg(self):
        # Read data into python as a pandas dataframe 
        # It is easy to work with
        
        # CHANGE - same as before with the name here
        # Also make this function a loop
        data=pd.read_csv(self.fmriprep_func_dir+f'/{self.subject}_task-{self.task}_run-1_desc-confounds_timeseries.tsv', sep='\t')
        data.fillna(0, inplace=True)
        
        
        # Write the confounds of interest into aw 1D file that will be used in AFNI
        # More info on the confounds: https://fmriprep.org/en/stable/outputs.html
        # Includes the motion regressors, their derivatives, top 3 csf compcor
        # components, global csf, and framewise displacement 
        data[['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z','trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1', 'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1', 'a_comp_cor_08', 'a_comp_cor_09', 'a_comp_cor_10', 'framewise_displacement']].to_csv(self.fmriprep_func_dir+'/confounds.1D',  sep='\t', header=False, index=False)

        print('Regressors printed to: ',  self.fmriprep_func_dir, '/confounds.1D \n',  sep='')
        
    '''
    Extract the top 3 compcor components from the csf should
    be in the .json file not the text file. 
    May be worth looking at the broken stick method for chosing compcor components
    https://blogs.sas.com/content/iml/2017/08/02/retain-principal-components.html

    '''
    def deconvolve(self, kernel_size='6.000', type1="", type2=""):
        #3ddeconvolve script to be written

        # Search for files with the ending '.1D' in the directory
        confoundsfile = f"{self.fmriprep_func_dir}/confounds.1D"
        
        # Check if any files with the '.1D' extension were found
        if not os.path.exists(confoundsfile):
            self.extract_reg()
        if type1 and type2:
            cond1=type1
            cond2=type2
            if not os.path.exists(f'{self.fmriprep_func_dir}/{cond1}.1D') or os.path.exists(f'{self.fmriprep_func_dir}/{cond2}.1D') :
                error_message = "Condition Files not found, please try a different name or run Extract Events"
                messagebox.showerror("Error", error_message)
                quit
        else:
            files_with_1d_extension=glob.glob(f"{self.fmriprep_func_dir}/*.1D")        
            if (len(files_with_1d_extension)>2):
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                # Create a pop-up dialog for user input
                cond1_input = filedialog.askopenfilename(title="Open Condition 1 .1D file(task)", initialdir=self.fmriprep_func_dir)
                cond2_input = filedialog.askopenfilename(title="Open Condition 2 .1D file(baseline to subtract)", initialdir=self.fmriprep_func_dir)
                cond1 = cond1_input.split(".1D")[0]
                cond2 = cond2_input.split(".1D")[0]
                # Run the main event loop
                root.mainloop()
            else:
                cond1 = simpledialog.askstring("Input", "Condition 1(task condition, as it appears in events file):")
                cond2 = simpledialog.askstring("Input", "Condition 2(baseline task to subtract, as it appears in events file):")
                self.extract_event_data(type1=cond1, type2=cond2)
            
        
        
        # Want to stim times for each run 
        # Change stim times, stim label, and gltsym
        # Add in file with z-scored imageability scores
        
        
        decon_script_content=f"""#!/bin/tcsh


set datadir = {self.fmriprep_dir}
set procs = 6
set subj = {self.subject}
set task = {self.task}
cd $datadir/func
set outdir = /data/neurodev/NTR/afni_outputs/{self.subject}/{self.task}.outputs

echo "Starting subject $subj {cond1}-{cond2}"

3dDeconvolve \
-jobs $procs \
-input ./sm_${{subj}}_task-${{task}}_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz \
-mask ${{subj}}_task-{self.task}_run-1_space-MNI152NLin2009cAsym_res-1_desc-brain_mask.nii.gz \
-polort 0 \
-progress 5000 \
-num_stimts 18 \
-num_glt 1 \
-stim_times 1 ./{cond1}.1D 'SPMG1(1)' \
-stim_label 1 'words' \
-stim_times 2 ./{cond2}.1D 'SPMG1(1)' \
-stim_label 2 'scramble' \
-stim_file 3 ./confounds.1D"[0]" -stim_label 3 "dS" -stim_base 3 \
-stim_file 4 ./confounds.1D"[1]" -stim_label 4 "dL" -stim_base 4 \
-stim_file 5 ./confounds.1D"[2]" -stim_label 5 "dP" -stim_base 5 \
-stim_file 6 ./confounds.1D"[3]" -stim_label 6 "Roll" -stim_base 6 \
-stim_file 7 ./confounds.1D"[4]" -stim_label 7 "Pitch" -stim_base 7 \
-stim_file 8 ./confounds.1D"[5]" -stim_label 8 "Yaw" -stim_base 8 \
-stim_file 9 ./confounds.1D"[6]" -stim_label 9 "dS_deriv" -stim_base 9 \
-stim_file 10 ./confounds.1D"[7]" -stim_label 10 "dL_deriv" -stim_base 10 \
-stim_file 11 ./confounds.1D"[8]" -stim_label 11 "dP_deriv" -stim_base 11 \
-stim_file 12 ./confounds.1D"[9]" -stim_label 12 "Roll_deriv" -stim_base 12 \
-stim_file 13 ./confounds.1D"[10]" -stim_label 13 "Pitch_deriv" -stim_base 13 \
-stim_file 14 ./confounds.1D"[11]" -stim_label 14 "Yaw_deriv" -stim_base 14 \
-stim_file 15 ./confounds.1D"[12]" -stim_label 15 "a_comp_cor08" -stim_base 15 \
-stim_file 16 ./confounds.1D"[13]" -stim_label 16 "a_comp_cor09" -stim_base 16 \
-stim_file 17 ./confounds.1D"[14]" -stim_label 17 "a_comp_cor10" -stim_base 17 \
-stim_file 18 ./confounds.1D"[15]" -stim_label 18 "framewise_displacement" -stim_base 18 \
-gltsym 'SYM: {cond1} -{cond2}' \
-glt_label 1 {cond1} -{cond2} \
-tout \
-errts $outdir/errts.mc.${{subj}} \
-fitts $outdir/fitts.$subj \
-bucket $outdir/stats.${{subj}} \


echo "Finished subject $subj"
 """
     

        fpath=os.path.join(self.out_dir, f'{self.subject}_decon.csh')
        
        with open(fpath, 'w') as file:
            file.write(decon_script_content)
        
        try:
            result=subprocess.run(['tcsh', f"{fpath}"], check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running the deconvolve script: {e} \n")
        else:
            print("The deconvolve script has been executed successfully. \n")

    def make_nifti_file(self):
        
        brikhead_path=os.path.join(f"{self.out_dir}", f"{self.task}.outputs/stats.{self.subject}+tlrc")
        nii_path=os.path.join(f"{self.out_dir}", f"stats.{self.subject}.nii")
        nifti_script=f"""#!/bin/tcsh 
set subj={self.subject}
cd {self.out_dir}
echo "Starting subject $subj"
3dAFNItoNIFTI {brikhead_path} -prefix {nii_path}

echo "Finished subject $subj"
"""
        fpath=os.path.join(self.out_dir, f"{self.subject}_makenifti.csh")
        print(fpath)
        
        with open(fpath, 'w') as file:
            file.write(nifti_script)
            
        try:
            results=subprocess.run(["tcsh", f"{fpath}"], check=True, text=True)
            print(results)
        except subprocess.CalledProcessError as e:
            print(f"Error running the nifti script: {e}")
        else:
            print("The nifti script has been executed successfully. \n")
         
            
    def plot_brain(self, form='mosaic'):
        # Check if nifti file exists or else make one
        print(self.subject)
        nifti_file=os.path.join(f"{self.out_dir}", f"stats.{self.subject}.nii")
        if not os.path.exists(nifti_file):
            self.make_nifti_file()
        
        nii_image=nib.load(nifti_file)
        single_volume=nii_image.slicer[:,:,:,0,6]
        # Plot Brain
        if form=='vwfa':
            plotting.plot_stat_map(single_volume, display_mode='ortho', colorbar=True, threshold=3.3675, cut_coords=(-45, -57, -12))
        if form=='mosaic':
            plotting.plot_stat_map(single_volume, display_mode='mosaic', colorbar=True, threshold=3.3675)

        plotting.show()
        
    # If you would like to make life easy and run everything at once, voila
    def run_entire_process(self, type1, type2, kernel_size='6.000'):
        
        # CHANGE - take out smoothing or any other functions we'd want to skip
        print("0/7 Tasks Completed: \nCopying Event Files from BIDS Directory \n")
        self.copy_event_files()
        print("1/7 Tasks Completed \nStarting to Extract Events Data \n")
        self.extract_event_data(type1=type1, type2=type2)
        print("2/7 Tasks Completed: \nStarting Smoothing \n")
        self.smooth(kernel_size)
        print("3/7 Tasks Completed: \nStarting to Extract Regressors \n")
        self.extract_reg()
        print("4/7 Tasks Completed: \nStarting 3ddeconvolve \n")
        self.deconvolve(type1=type1, type2=type2)
        print("5/7 Tasks Completed: \nStarting NIFTI Conversion \n")
        self.make_nifti_file()
        print("6/7 Tasks Completed: \nPlotting brain now")
        self.plot_brain()
        print("7/7 Tasks Completed: \nBrain Plotted")
  
    
    def __str__(self): 
        return "Test subject:%s" % (self.fmriprep_dir)


