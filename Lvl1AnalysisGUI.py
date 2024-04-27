#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:21:18 2024

@author: samrosenberg
"""



"""
-----------------------Univariate 1st Level PIPELINE GUI---------------------------


INPUTS: fmriprepped data including a vwfa localizer scan(words vs. scramble conditions)
OUTPUTS: Univariate contrast of conddition 1 vs. condition 2

-------------------------------------------------------------------------------
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
from Lvl1Analysis import Lvl1Analysis

class Lvl1Analysis_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("1st Level Analysis")

        # Filepath variables
        self.fmriprep_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.task_var = tk.StringVar()
        self.type1_var = tk.StringVar()
        self.type2_var = tk.StringVar()
        self.number_var = tk.StringVar()
        self.smooth_fwhm_var = tk.StringVar(value="6.000")  # Default value for Smoothing FWHM

        # fmriprep directory label and entry
        fmriprep_label = tk.Label(self, text="Select fmriprep Directory:")
        fmriprep_label.grid(row=0, column=0, sticky="w")
        self.fmriprep_entry = tk.Entry(self, textvariable=self.fmriprep_var)
        self.fmriprep_entry.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Button to select fmriprep directory
        fmriprep_button = tk.Button(self, text="Browse", command=self.select_fmriprep)
        fmriprep_button.grid(row=0, column=1, columnspan=1, sticky="ew")

        # Output directory label and entry
        output_label = tk.Label(self, text="Select Output Directory:")
        output_label.grid(row=2, column=0, sticky="w")
        self.output_entry = tk.Entry(self, textvariable=self.output_var)
        self.output_entry.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Button to select output directory
        output_button = tk.Button(self, text="Browse", command=self.select_output)
        output_button.grid(row=2, column=1, sticky="ew")

        # Number label and entry
        number_label = tk.Label(self, text="Enter Subject Number:")
        number_label.grid(row=4, column=0, sticky="w")
        self.number_entry = tk.Entry(self, textvariable=self.number_var)
        self.number_entry.grid(row=4, column=1, sticky="ew")
        
        # Select commands label
        self.instr_entry = tk.Label(self, text="Select commands to run below:")
        self.instr_entry.grid(row=7, column=0, sticky="ew")

        # Task label+entry
        self.task_label = tk.Label(self, text="Enter task name:")
        self.task_label.grid(row=5, column=0, sticky="w")
        self.task_entry = tk.Entry(self, textvariable=self.task_var)
        self.task_entry.grid(row=5, column=1, sticky="ew")

        # Smooth FWHM label and entry
        self.smooth_fwhm_label = tk.Label(self, text="Smoothing FWHM:")
        self.smooth_fwhm_label.grid(row=12, column=1, sticky="w")
        self.smooth_fwhm_entry = tk.Entry(self, textvariable=self.smooth_fwhm_var, state=tk.DISABLED)
        self.smooth_fwhm_entry.grid(row=13, column=1, sticky="ew")
        self.smooth_fwhm_label = tk.Label(self, text="(Default 6mm)")
        self.smooth_fwhm_label.grid(row=13, column=2, sticky="w")
        
        
        # Trial type 1 name+entry
        self.type1_label = tk.Label(self, text="Condition 1 Name:")
        self.type1_label.grid(row=9, column=1, sticky="w")
        self.type1_entry = tk.Entry(self, textvariable=self.type1_var, state=tk.DISABLED)
        self.type1_entry.grid(row=10, column=1, sticky="ew")
        
        # Trial type 2 name+entry
        self.type2_label = tk.Label(self, text="Condition 2 Name:")
        self.type2_label.grid(row=9, column=2, sticky="w")
        self.type2_entry = tk.Entry(self, textvariable=self.type2_var, state=tk.DISABLED)
        self.type2_entry.grid(row=10, column=2, sticky="ew")

        commands = ["Copy Event Files", "Extract Event Data", "Smooth Data", "Deconvolve", "Make Nifti File", "Plot Brain"]
        self.command_vars = {}
        counter = np.linspace(8, 18, 6).astype(int)
        rows=8
        for idx, command in enumerate(commands):
            rows = counter[idx]  # Start the checkboxes from row 15
            var = tk.IntVar()
            checkbox = tk.Checkbutton(self, text=command, variable=var, command=self.toggle_optional_entry)
            checkbox.grid(row=rows, column=0, sticky="w")
            blank = tk.Label(self, text='')
            blank.grid(row=rows-1, column=0, sticky="w")
            self.command_vars[command] = var


        '''# Checkboxes for commands
        commands = ["Copy Event Files", "Extract Event Data", "Smooth Data", "Deconvolve", "Make Nifti File", "Plot Brain"]
        self.command_vars = {}
        count=np.linspace(10, 20, 6).astype(int)
        for idx, command in enumerate(commands):
            idx=count[idx]
            var = tk.IntVar()
            checkbox = tk.Checkbutton(self, text=command, variable=var, command=self.toggle_optional_entry)
            checkbox.grid(row=(idx), column=0, sticky="w")
            self.command_vars[command] = var'''
        # Run buttons
        run_selected_button = tk.Button(self, text="Run Selected Commands", command=self.run_selected_commands)
        run_selected_button.grid(row=rows+2, column=0, columnspan=3, sticky="ew")

        run_all_button = tk.Button(self, text="Run All Commands", command=self.run_all_commands)
        run_all_button.grid(row=rows+3, column=0, columnspan=3, sticky="ew")

        # Help button
        help_button = tk.Button(self, text="Help", command=self.show_help)
        help_button.grid(row=rows+4, column=0, columnspan=3, sticky="ew")

    def select_fmriprep(self):
        fmriprep_dir = filedialog.askdirectory()  # Open directory selection dialog
        self.fmriprep_var.set(fmriprep_dir)

    def select_output(self):
        output_dir = filedialog.askdirectory()  # Open directory selection dialog
        self.output_var.set(output_dir)

    def run_selected_commands(self):
        fmriprep_dir = self.fmriprep_var.get()
        output_dir = self.output_var.get()
        subnum = self.number_var.get()
        task= self.task_var.get()
        if not all([fmriprep_dir, output_dir, task, subnum]):
            messagebox.showerror("Error", "Please enter all required information.")
            return

        pipeline = Lvl1Analysis(fmriprep_dir, output_dir, task, subnum)

        selected_commands = []
        for command, var in self.command_vars.items():
            if var.get() == 1:
                selected_commands.append(command)
        
        for command in selected_commands:
            if command == "Copy Event Files":
                pipeline.copy_event_files()
            elif command == "Extract Event Data":
                type1=self.type1_var.get()
                type2=self.type2_var.get()
                pipeline.extract_event_data(type1, type2)
            elif command == "Smooth Data":
                pipeline.smooth()
            elif command == "Deconvolve":
                type1=self.type1_var.get()
                type2=self.type2_var.get()
                pipeline.deconvolve(type1=type1, type2=type2)
            elif command == "Make Nifti File":
                pipeline.make_nifti_file()
            elif command == "Plot Brain":
                # or "mosaic"
                pipeline.plot_brain()
    
        messagebox.showinfo("Commands Executed", "Selected commands executed.")


    def run_all_commands(self):
       fmriprep_dir = self.fmriprep_var.get()
       output_dir = self.output_var.get()
       subnum = self.number_var.get()
       task = self.task_var.get()
       type1=self.type1_var.get()
       type2=self.type2_var.get()
       if not all([fmriprep_dir, output_dir, subnum, task, type1, type2]):
           messagebox.showerror("Error", "Please enter all required information.")
           return

       pipeline = Lvl1Analysis(fmriprep_dir, output_dir,task, subnum)
       pipeline.run_entire_process(type1=type1, type2=type2)

    def show_help(self):
        help_text = """
copy_events_files():
    
    -Moves the events timing files from the bids directory to the fmriprep directory. All files paths are predefined to match the file structure of neurodev.

    -Outputs: 
        NONE

extract_event_data():
    
    -Takes the events files(copied in the last step), and makes a .1D file for each stimulus that contains their onset times as a row vector delimited by spaces(ie. 1.2 3.4 5.6 7.8...)

    -Outputs:
        /fmriprep directory/subject/func/words.1D --> (text file with row vector of word onset times)
        /fmriprep directory/subject/func/scramble.1D --> (text file with row vector of scramble onset times)

smooth(kernel_size='6.000'):
    
    -Writes a .csh script(denoted {subject}_smooth.csh) calling afni's 3dmerge to blur the vwfa functional image to FWHM of the specified kernel size(if none are specified then the default of '6.000' is used)

    -Outputs:
        /fmriprep directory/subject/{subject}_smooth.csh -->(script to smooth)
        /fmriprep directory/subject/func/sm_${subject}_task-vwfa_run-1_space-MNI152NLin2009cAsym_res-1_desc-preproc_bold.nii.gz --> (smoothed vwfa run file)

extract_reg():
    
    -Takes the regressors output from fmriprep, and makes a new file, confounds.1D, that isolates the regressors of interest:
        - 'trans_x', 'trans_y', 'trans_z' --> x,y,z linear movement
        - 'rot_x', 'rot_y', 'rot_z' --> roll, pitch, yaw
        - 'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1'
        - 'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1'
        - 'a_comp_cor_08', 'a_comp_cor_09', 'a_comp_cor_10' --> (top 3 csf compcor)
        - 'csf', 'framewise_displacement'

    -Outputs:
        /fmriprep directory/subject/func/confounds.1D --> (text file with column vectors of regressors)

deconvolve():
    
    -Writes a .csh script(denoted {subject}_decon.csh) calling afni's 3ddeconvolve function to devonvolve the data using the word and scramble onset times (words.1D & scramble.1D) and the specified regressors(confounds.1D). The script is then saved in the subject's fmriprep folder along with its outputs.

    -Outputs:
        /fmriprep directory/subject/{subject}_decon.csh --> (3ddeconvolve script used)
        /fmriprep directory/subject/{subject}.outputs --> (results of 3ddeconvolve script)
        /fmriprep directory/subject/{subject}.xmat.1D -->(plots of all regressors)
"""
        help_window = tk.Toplevel(self)
        help_window.title("Help")
        
        help_text_widget = tk.Text(help_window, wrap=tk.WORD,  font='Arial 8')
        help_text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Insert formatted text
        help_text_widget.insert(tk.END, help_text)
        
        # Configure tags for different styles
        help_text_widget.tag_configure("bold", font=("Arial", 16, "bold"))
        
        # Apply bold tags to the text
        #for i in [2, 9, 17, 25, 38]:
        #    help_text_widget.tag_add("bold", f"{i}.0", f"{i}.40")
        lines = help_text.split('\n')
        for idx, line in enumerate(lines, start=1):
            if '):' in line:  # Check if the word "Outputs" is in the line
                help_text_widget.tag_add("bold", f"{idx}.0", f"{idx}.40")
            
        help_text_widget.tag_configure("italic", font=("Arial", 10, "italic"))
        # Split the help text into lines
        lines = help_text.split('\n')
        for idx, line in enumerate(lines, start=1):
            if 'Outputs' in line:  # Check if the word "Outputs" is in the line
                help_text_widget.tag_add("italic", f"{idx}.0", f"{idx}.40")
            #else:
                #help_text_widget.tag_add(tk.END, line + '\n')
        
        #help_text_widget.tag_configure("italic", font=("TkDefaultFont", 11, "italic"))
        
        # Ensure the text is readonly
        help_text_widget.configure(state="disabled")

    def toggle_optional_entry(self):
        if self.command_vars["Smooth Data"].get() == 1:
            self.smooth_fwhm_entry.config(state=tk.NORMAL)
        else:
            self.smooth_fwhm_entry.config(state=tk.DISABLED)
        if self.command_vars["Extract Event Data"].get() == 0 and self.command_vars["Deconvolve"].get() == 0:
            self.type1_entry.config(state=tk.DISABLED)
            self.type2_entry.config(state=tk.DISABLED)
        else:
            self.type1_entry.config(state=tk.NORMAL)
            self.type2_entry.config(state=tk.NORMAL)
   

if __name__ == "__main__":
    app = Lvl1Analysis_GUI()
    app.mainloop()
