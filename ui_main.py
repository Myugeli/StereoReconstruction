# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:30:36 2023

@author: myuey
"""

import tkinter
from tkinter import filedialog
import confighandler as chand
import ncc_cor_core as ncc
import os
global config
config = chand.ConfigHandler()
config.load_config()
startup_cycle = True
#create window
root = tkinter.Tk()
root.title("3D Stereo Reconstruction -MG- FSU-Jena")
root.geometry('600x200')
root.resizable(width=False, height=False)
root.focus_force()
lang_opt = tkinter.StringVar(root)
options = ["English", "Deutsch"]
lang_opt.set(options[config.lang]) 

root.columnconfigure(2, minsize=10)
#root.rowconfigure(0, minsize=50)

#output filebox
out_lbl = tkinter.Label(root, text = "Output File:")
out_lbl.grid(row=0, column=0)
out_txt = tkinter.Text(root, height=1, width=35)
out_txt.insert(tkinter.END, config.output)
out_txt.grid(row=0, column=1)
#folder variables
mat_fold = tkinter.StringVar(root)
imgL_fold = tkinter.StringVar(root)
imgR_fold = tkinter.StringVar(root)
ini_fold = os.getcwd()
#matrix folder location
mat_lbl = tkinter.Label(root, text = "Matrices:")
mat_lbl.grid(row = 1, column = 0)
mat_txt = tkinter.Text(root, height = 1, width = 35)
mat_txt.insert(tkinter.END, config.mat_folder)
mat_txt.grid(row = 1, column = 1)
def mat_btn_click():
    folder_path = filedialog.askdirectory()
    mat_fold.set(folder_path)
    mat_txt.delete('1.0', tkinter.END)
    mat_txt.insert('1.0', folder_path)
mat_btn = tkinter.Button(root, text = "Browse", command = mat_btn_click)
mat_btn.grid(row = 1, column = 2)
#images_L location
imgL_lbl = tkinter.Label(root, text = "Left Images:")
imgL_lbl.grid(row = 2, column = 0)
imgL_txt = tkinter.Text(root, height = 1, width = 35)
imgL_txt.insert(tkinter.END, config.left_folder)
imgL_txt.grid(row = 2, column = 1)
def imgL_btn_click():
    folder_path = filedialog.askdirectory()
    imgL_fold.set(folder_path)
    imgL_txt.delete('1.0', tkinter.END)
    imgL_txt.insert('1.0', folder_path)
imgL_btn = tkinter.Button(root, text = "Browse", command = imgL_btn_click)
imgL_btn.grid(row = 2, column = 2)
#images_R location
imgR_lbl = tkinter.Label(root, text = "Right Images:")
imgR_lbl.grid(row = 3, column = 0)
imgR_txt = tkinter.Text(root, height = 1, width = 35)
imgR_txt.insert(tkinter.END, config.right_folder)
imgR_txt.grid(row = 3, column = 1)
def imgR_btn_click():
    folder_path = filedialog.askdirectory()
    imgR_fold.set(folder_path)
    imgR_txt.delete('1.0', tkinter.END)
    imgR_txt.insert('1.0', folder_path)
imgR_btn = tkinter.Button(root, text = "Browse", command = imgR_btn_click)
imgR_btn.grid(row = 3, column = 2)
#interpolation points input
interp_lbl = tkinter.Label(root, text = "Interpolations:")
interp_lbl.grid(row = 4, column = 0)
interp_txt = tkinter.Text(root, height = 1, width = 35)
interp_txt.insert(tkinter.END, config.interp)
interp_txt.grid(row = 4, column = 1)
#offset value input
ofsX_lbl = tkinter.Label(root, text = "Offset X:")
ofsX_lbl.grid(row = 5, column = 0)
ofsX_txt = tkinter.Text(root, height = 1, width = 35)
ofsX_txt.insert(tkinter.END, config.x_offset)
ofsX_txt.grid(row = 5, column = 1)
ofsY_lbl = tkinter.Label(root, text = "Offset Y:")
ofsY_lbl.grid(row = 6, column = 0)
ofsY_txt = tkinter.Text(root, height = 1, width = 35)
ofsY_txt.insert(tkinter.END, config.y_offset)
ofsY_txt.grid(row = 6, column = 1)
#start button
def st_btn_click():
    ncc.run_cor_lin(config, out_txt.get("1.0", tkinter.END))
st_btn = tkinter.Button(root, text = "Start", command = st_btn_click)
st_btn.grid(row = 7, column = 1)

#reset button
def rst_btn_click():
    config.load_config()
    out_txt.delete('1.0', tkinter.END)
    out_txt.insert(tkinter.END, config.output)
    mat_txt.delete('1.0', tkinter.END)
    mat_txt.insert(tkinter.END, config.mat_folder)
    imgL_txt.delete('1.0', tkinter.END)
    imgL_txt.insert(tkinter.END, config.left_folder)
    imgR_txt.delete('1.0', tkinter.END)
    imgR_txt.insert(tkinter.END, config.right_folder)
    interp_txt.delete('1.0', tkinter.END)
    interp_txt.insert(tkinter.END, config.interp)
    ofsX_txt.delete('1.0', tkinter.END)
    ofsX_txt.insert(tkinter.END, config.x_offset)
    ofsY_txt.delete('1.0', tkinter.END)
    ofsY_txt.insert(tkinter.END, config.x_offset)
    
rst_btn = tkinter.Button(root, text = "Reset", command = rst_btn_click)
rst_btn.grid(row = 2, column = 5)
#save all fields as default button - if field is empty, do not modify config
def cfg_btn_click():
    config.output = out_txt.get('1.0', tkinter.END)
    config.mat_folder = mat_txt.get('1.0', tkinter.END)
    config.left_folder = imgL_txt.get('1.0', tkinter.END)
    config.right_folder = imgR_txt.get('1.0', tkinter.END)
    
    config.interp = int(interp_txt.get('1.0', tkinter.END))
    
    config.x_offset = int(ofsX_txt.get('1.0', tkinter.END))
    
    config.y_offset = int(ofsY_txt.get('1.0', tkinter.END))
    
    if lang_opt.get() == "English":
        config.lang = 0
    else:
        config.lang = 1
    config.make_config()   
    
cfg_btn = tkinter.Button(root, text = "Set Defaults", command = cfg_btn_click)
cfg_btn.grid(row = 1, column = 5)
#settings window
def set_window():
    set_disp = tkinter.Toplevel(root)
    if lang_opt.get() == "English":
        set_disp.title("Settings")
    else:
        set_disp.title("Einstellungen")
    set_disp.geometry('400x250')
    set_disp.focus_force()
    set_disp.resizable(width=False, height=False)
    
    tmod_lbl = tkinter.Label(set_disp, text = "t-Vector Modifier:")
    tmod_txt = tkinter.Text(set_disp, height = 1, width = 20)
    tmod_txt.insert(tkinter.END, config.tmod)
    tmod_lbl.grid(row = 0, column = 0)
    tmod_txt.grid(row = 0, column = 1)
    
    tvec_lbl = tkinter.Label(set_disp, text = "t-Vector File:")
    tvec_txt = tkinter.Text(set_disp, height = 1, width = 20)
    tvec_txt.insert(tkinter.END, config.t_file)
    tvec_lbl.grid(row = 1, column = 0)
    tvec_txt.grid(row = 1, column = 1)
    
    Rmat_lbl = tkinter.Label(set_disp, text = "R-Matrix File:")
    Rmat_txt = tkinter.Text(set_disp, height = 1, width = 20)
    Rmat_txt.insert(tkinter.END, config.R_file)
    Rmat_lbl.grid(row = 2, column = 0)
    Rmat_txt.grid(row = 2, column = 1)
    
    lkp_lbl = tkinter.Label(set_disp, text = "Lineskips:")
    lkp_txt = tkinter.Text(set_disp, height = 1, width = 20)
    lkp_txt.insert(tkinter.END, config.skiprow)
    lkp_lbl.grid(row = 3, column = 0)
    lkp_txt.grid(row = 3, column = 1)
    
    kl_lbl = tkinter.Label(set_disp, text = "Left Camera Matrix File:")
    kl_txt = tkinter.Text(set_disp, height = 1, width = 20)
    kl_txt.insert(tkinter.END, config.kL_file)
    kl_lbl.grid(row = 4, column = 0)
    kl_txt.grid(row = 4, column = 1)
    
    kr_lbl = tkinter.Label(set_disp, text = "Right Camera Matrix File:")
    kr_txt = tkinter.Text(set_disp, height = 1, width = 20)
    kr_txt.insert(tkinter.END, config.kR_file)
    kr_lbl.grid(row = 5, column = 0)
    kr_txt.grid(row = 5, column = 1)
    
    delim_lbl = tkinter.Label(set_disp, text = "Delimiter:")
    delim_txt = tkinter.Text(set_disp, height = 1, width = 20)
    delim_txt.insert(tkinter.END, config.delim)
    delim_lbl.grid(row = 6, column = 0)
    delim_txt.grid(row = 6, column = 1)
    
    thr_lbl = tkinter.Label(set_disp, text = "Threshold:")
    thr_txt = tkinter.Text(set_disp, height = 1, width = 20)
    thr_txt.insert(tkinter.END, config.thresh)
    thr_lbl.grid(row = 7, column = 0)
    thr_txt.grid(row = 7, column = 1)
    
    cff_lbl = tkinter.Label(set_disp, text = "Config File:")
    cff_txt = tkinter.Text(set_disp, height = 1, width = 20)
    cff_txt.insert(tkinter.END, config.config_filename)
    cff_lbl.grid(row = 8, column = 0)
    cff_txt.grid(row = 8, column = 1)
    
    def cnc_btn_click():
        set_disp.destroy()
    cnc_btn = tkinter.Button(set_disp, text = "Cancel", command = cnc_btn_click)
    def ori_btn_click():
        ori_config = chand.ConfigHandler()
        ori_config.make_origin()
    ori_btn = tkinter.Button(set_disp, text = "Original Config", command = ori_btn_click)
    def ok_btn_click():
        pass
    ok_btn = tkinter.Button(set_disp, text = "OK", command = ok_btn_click)
    if lang_opt.get() == "Deutsch":
        cnc_btn.config(text = "Abbrechen")
        ori_btn.config(text = "Ori")
        
    cnc_btn.grid(row = 8, column = 2)
    ori_btn.grid(row = 0, column = 2)
    ok_btn.grid(row = 9,column = 2)

set_btn = tkinter.Button(root, text = "Settings", command = set_window)
set_btn.grid(row = 3, column = 5)

#language selector
lang_lbl = tkinter.Label(root, text = "Language:")
lang_lbl.grid(row=0, column=4)
def update_text_language(lang_sel):
    if lang_sel == "English":
        out_lbl.config(text = "Output File:")
        lang_lbl.config(text = "Language:")
        set_btn.config(text = "Settings")
        mat_lbl.config(text = "Matrices:")
    else:
        out_lbl.config(text = "Datei Ausgaben:")
        lang_lbl.config(text = "Sprache:")
        set_btn.config(text = "Einstellungen")
        mat_lbl.config(text = "Matrizen:")
dropdown = tkinter.OptionMenu(root, lang_opt, *options, command=update_text_language)
dropdown.grid(row=0, column=5)
#Check if language needs to be updated on startup
if startup_cycle:
    update_text_language(lang_opt.get())
    startup_cycle = False
    
root.mainloop()

    
