#!/usr/bin/env python
# -*- coding: cp1252 -*-


import os
from Tkinter import *
import tkMessageBox
from data_package_functions_24_august import *



### Function
def start_function():
    opener = create_opener()
    folder_exist = check_datafolder(srcdir.get())
    if folder_exist == FALSE:
        tkMessageBox.showwarning('Result','This folder does not exist.\nTry again')
        srcdir.set('')
    ##Check if layer exists
    layer_exist = check_layer(layer_name.get())
    if layer_exist == FALSE:
        tkMessageBox.showwarning('Result','This layer does not exist or the table bod.public.dataset has not been filled.\nTry again or close program to fill the bod table')
        layer_name.set('')
    else:
        ## check if it is the good layer
        title_layer = layer_title(layer_name.get())
        validity = tkMessageBox.askquestion('Validation', "Is this the title of the layer?\n" + title_layer)
        if validity == 'no':
            tkMessageBox.showwarning('Result','Try again')
            layer_name.set('')
    if folder_exist == TRUE and validity == 'yes':
        master.destroy()
        id_layer = find_id(layer_name.get())
        create_folder(layer_name.get(), srcdir.get(), id_layer)
    tkMessageBox.showinfo('Result','Data Folder is ready')


##Create interface

folder_exist = FALSE
validity = "no"

    
master = Tk()
master.title("data.geoadmin.ch")

Label(master, text="""Enter the technical name of the layer
\nand the path to the folder containing the data to be transferred
\nExample:
\nch.are.agglomerationen_isolierte_staedte 
\nI:/BGDI/01_Originaldaten/bund/are/_Rohdaten/ch.are.agglomerationen-isolierte_staedte_20140506 """).grid(row=0, column=1)
Label(master, text="layer name", anchor=CENTER).grid(row=1, column=0)
Label(master, text="data folder", anchor=CENTER).grid(row=2, column=0)

layer_name = StringVar()
srcdir = StringVar()
e1 = Entry(master, textvariable=layer_name, width=100)
e2 = Entry(master, textvariable=srcdir, width=100)

e1.grid(row=1, column=1)
e2.grid(row=2, column=1)

e1.insert(10, "ch.are.agglomerationen_isolierte_staedte")
e2.insert(10, "I:/BGDI/01_Originaldaten/bund/are/_Rohdaten/ch.are.agglomerationen-isolierte_staedte_20140506")

Button(master, text='OK', command=start_function).grid(row=4, column=1,sticky=W, padx=500)

mainloop()
