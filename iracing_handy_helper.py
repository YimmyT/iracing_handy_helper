import PySimpleGUI as sg
import json
import shutil
from sys import exit
import os

#########################
# To do
# Create a back button or start over, at least
########################

setup_dir = ''

setup_dir_file = './setup_dir.ini'

setup_file_saved = False

extra_dirs = ''

series_json = './series_to_cars.json'

setup_list = None

transfer_list = []

target_dirs = []

current_layout = None

########
def show_target_dirs_window(values):
    global current_layout, extra_dirs, target_dirs
    for series in series_list:
        if values["-"+series+"-"] == True:
            selected_series = series
            break
    subdir_list = data[series]["dirs"].split("|")
    #   If there are multiple cars in the series, default to setup_dir + first car dir
    #   display TARGET DIRS
    #   display SET DIRS button
        #   Open folder browser to that dir
        #   Allow user to select
        #   Find extra dirs
    #   display TARGET DIRS + extra_dirs
    if len(subdir_list) > 1:
        target_dir_layout = [[sg.Frame("IRacing® Handy Helper: Choose your custom sub-directory",
            [[sg.Text("You have chosen a series with multiple cars. The setups you choose will be copied to all applicable cars in the series!")],
                [sg.Text("You can use the base directories or choose a custom sub-directory by clicking Set.")],                             
                [sg.In(default_text=(setup_dir+"/"+subdir_list[0]).replace(subdir_list[0], '*'),size=(100,1), disabled=True, enable_events=True ,key='-TARGETFOLDER-'), sg.FolderBrowse(button_text="Set", initial_folder=setup_dir+"/"+subdir_list[0])],
                [sg.Text("\n\nTarget Folder(s):")],
                *[[sg.Text(setup_dir+"/"+text, key='-'+text+'-')] for text in subdir_list],
                [sg.Button(size=(10, 1), enable_events=True, key="-CONFIRM2-", button_text="Confirm")]
            ]
            )]]
        target_dir_window = sg.Window("IRacing Handy Helper", target_dir_layout, icon='./ihh.ico')
        while True:
            event, values = target_dir_window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == '-TARGETFOLDER-' and values['-TARGETFOLDER-']:
                extra_dirs = get_extra_dirs(values['-TARGETFOLDER-'])
                for car in subdir_list:
                    target_dirs.append(setup_dir+"/"+car+"/"+extra_dirs)
                    target_dir_window['-'+car+'-'].update(setup_dir+"/"+car+"/"+extra_dirs)
                    print('target dir'+setup_dir+"/"+car+"/"+extra_dirs)
                target_dir_window.refresh()
            if event == "-CONFIRM2-":
                if len(target_dirs) == 0:
                    for car in subdir_list:
                        target_dirs.append(setup_dir+"/"+car)
                        target_dir_window['-'+car+'-'].update(setup_dir+"/"+car)
                        print('target dir'+setup_dir+"/"+car)

                current_layout = 3
                target_dir_window.close()
            
        
    #   If count of cars is 1, set target to the only car and skip to current_layout = 4
    else:
        target_dirs = [setup_dir+subdir_list[0]]
        current_layout = 4
    
########

#   If setup_dir.ini exists, load setup_dir
if os.path.exists(setup_dir_file):
    with open(setup_dir_file, 'r') as file:
        setup_dir = file.read()
    

#   Read series json file and create a list of series names
with open(series_json, "r") as read_file:
    data = json.load(read_file)

series_list = list(data.keys())

#   Find any extra directories after 'setup' and offer to replicate that directory structure in 
#   all the setup dirs for each car in the class
def get_extra_dirs(_setup):
    extra_dirs_w_class = _setup.split("setups/")[1]
    extra_dirs_w_class_list = extra_dirs_w_class.split("/")
    extra_dirs_w_class_list.pop(0)
    #   Remove the car class from the subpath
    return '/'.join(extra_dirs_w_class_list)

#   Layout for Iracing setup folder selection
layout1 = [[sg.Frame("IRacing® Handy Helper: Select your IRacing® setups directory",
            [[sg.Text("\n\nLet's start by setting (or confirming) your User Documents -> IRacing® -> setups directory and clicking the Next button")],
            [sg.In(size=(100,1), disabled=True, enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Text("\n\nAdvanced: If you have a specific directory structure you want replicated for each car in the series, select that folder in one of the cars in the series (e.g. Toyota Camry 2022 for Nascar Next Gen). We'll take care of the rest!", size=(20, 1))]]
            )]]

#   Layout for Series selection
layout2 = [[sg.Frame("IRacing® Handy Helper: Select your series",
            [[sg.Text("Which series would you like to import setups into? Select your choice and click the Next button")],
            *[[sg.Radio(text, 1, key=f"-{text}-", default=True)] for text in series_list],
            [sg.Text("\n\nIRacing® default 'setups' directory")],
            [sg.In(default_text=setup_dir,size=(100,1), disabled=True, enable_events=True ,key='-SETUPFOLDER-'), sg.FolderBrowse()]]
            )]]

#   Layout for setup selection
layout3 = [[sg.Frame("IRacing® Handy Helper: Select your setup(s)",
            [[sg.Text("Which setups do you want to import? Select your desired setups and click the Next button")],
            [sg.In(size=(100,1), disabled=True, enable_events=True ,key='-FOLDER-'), sg.FilesBrowse(file_types=(("Text files", "*.sto"),))]]
            )]]


#   Base layout that holds the visible and invisible columns>layouts
layout = [[sg.Column(layout2, visible=True, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')], 
          [sg.Button("NEXT", disabled=(True if setup_dir == '' else False), size=(10, 1))]]

current_layout = 2  # The currently visible layout

# Create the window
window = sg.Window("IRacing Handy Helper", layout, margins=(150, 1), icon='ihh.ico', resizable=True)

# Create an event loop
while True:
    event, values = window.read()
    print(f"layout {current_layout}")
    print(f"setup dir |{setup_dir}|")
    print(f"extra |{extra_dirs}|")
    print(event, values)
    # End program if user closes window 
    if event == sg.WIN_CLOSED:
        break

    if event == '-SETUPFOLDER-' and values['-SETUPFOLDER-']:
        # Enable series buttons on setup dir selection
        window['NEXT'].update(disabled=False)

    #   Build the setup list from the selected files
    if event == '-FOLDER-' and values['-FOLDER-']:
        setup_list = values['-FOLDER-'].split(';')
        print('setups selected')
        print(setup_list)

    if event == "NEXT":
        if setup_file_saved == False:
            setup_dir = values['-SETUPFOLDER-']
            print('here!!'+setup_dir)
            #   When setup_dir is empty or not a typical setups dir, warn user and reset page
            if setup_dir == "" or setup_dir.endswith('/setups') == False:
                print('here11 '+setup_dir)
                print('here11 '+str(setup_dir.endswith('/setups') == False))
                sg.popup_ok("Oops. Please select the default IRacing® 'setups' folder.","Path should look like:","C:/Users/[windows user]/OneDrive/Documents/iRacing/setups'", title="Error", icon='./ihh.ico')
                current_layout = 2
            else:
                with open(setup_dir_file, 'w') as f:
                    f.write(setup_dir)
                setup_file_saved = True
                window[f'-COL{current_layout}-'].update(visible=False)
                current_layout = 3
                show_target_dirs_window(values)
                window[f'-COL{current_layout}-'].update(visible=True)
        elif current_layout == 2 and setup_file_saved == True:
                print("SHOW TARGT WINDOW")
                show_target_dirs_window(values)
                window[f'-COL2-'].update(visible=False)
                current_layout = 3
                window[f'-COL{current_layout}-'].update(visible=True)       
        else:
            for setup in setup_list:
                #   Copy to each cars directory including the optional extra_dirs
                print('target dirs')
                print(target_dirs)
                for dir in target_dirs:
                    print(f"copying from: {setup} to {dir}")
                    if not os.path.exists(dir):
                        os.makedirs(dir)

                    if os.path.exists(dir+"/"+setup):
                        os.remove(dir+"/"+setup)
                    shutil.copy(setup, dir)
                    transfer_list.append('['+setup.split("/")[-1]+']'+dir+'/')
                

            completed_layout = [[sg.Text("Welcome to the IRacing® Handy Helper > Transfers complete!", font="bold")],
                    [
                        sg.Listbox(
                            values=transfer_list, enable_events=True, size=(100, 10), key="-File List-"
                        )
                    ],
                    [
                        sg.Button(size=(10, 1), enable_events=True, key="-CLOSE-", button_text="Close")
                    ],
                    [
                        sg.Button(size=(10, 1), enable_events=True, key="-RESET-", button_text="Reset")
                    ],
                ]
            completed_window = sg.Window("IRacing Handy Helper", completed_layout, resizable=True, icon='./ihh.ico')
            while True:
                event, values = completed_window.read()
                if event == "-RESET-":
                    transfer_list = []
                    target_dirs = []
                    window[f'-COL{current_layout}-'].update(visible=False)
                    break

                if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                    window.close()
                    completed_window.close()
                    exit()
            current_layout = 2 # Reset main window
            completed_window.close()
            window[f'-COL{current_layout}-'].update(visible=True)
            print(current_layout)
window.close()

