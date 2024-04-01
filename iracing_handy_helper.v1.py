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

extra_dirs = ''

extra_dirs_bool = False  #   Key on when to check for extra dirs

series_json = './series_to_cars.json'

setup_list = None

transfer_list = []

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
layout1 = [[sg.Frame("IRacing® Handy Helper: Select your IRacing® setups directoty",
            [[sg.Text("\n\nLet's start by setting (or confirming) your User Documents -> IRacing® -> setups directory and clicking the Next button")],
            [sg.In(size=(100,1), disabled=True, enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Text("\n\nAdvanced: If you have a specific directory structure you want replicated for each car in the series, select that folder in one of the cars in the series (e.g. Toyota Camry 2022 for Nascar Next Gen). We'll take care of the rest!", size=(20, 1), text_color='red')]]
            )]]

#   Layout for Series selection
layout2 = [[sg.Frame("IRacing® Handy Helper: Select your series",
            [[sg.Text("Which series would you like to import setups into? Select your choice and click the Next button")],
            *[[sg.Radio(text, 1, key=f"-{text}-" )] for text in series_list]]
            )]]

#   Layout for setup selection
layout3 = [[sg.Frame("IRacing® Handy Helper: Select your setup(s)",
            [[sg.Text("Which setups do you want to import? Select your desired setups and click the Next button")],
            [sg.In(size=(100,1), disabled=True, enable_events=True ,key='-FOLDER-'), sg.FilesBrowse(file_types=(("Text files", "*.sto"),))]]
            )]]


#   Base layout that holds the visible and invisible columns>layouts
layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')], 
          [sg.Button("NEXT", disabled=True, size=(10, 1))]]

current_layout = 1  # The currently visible layout

# Create the window
window = sg.Window("IRacing Handy Helper", layout, margins=(150, 1), icon='ihh.ico')

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
    
    #   Enable the next button on the setup directory setting page, only occurs on first page
    if event == '-FOLDER-' and values['-FOLDER-']:
        # Enable the button
        window['NEXT'].update(disabled=False)

    #   Build the setup list from the selected files
    if event == '-FOLDER-0' and values['-FOLDER-0']:
        setup_list = values['-FOLDER-0'].split(';')

    if event == "NEXT":
            #   Set setup directory when empty and available in values
            if setup_dir == "":
                 setup_dir = values['-FOLDER-']
                 #  When setup_dir doesnt' end in /setups, check for optional extra_dirs
                 if setup_dir.endswith('/setups') == False:
                    extra_dirs = get_extra_dirs(setup_dir)
                    extra_dirs_bool = True

            #   Adds to the current_layout count (goes to next page) and updates window
            window[f'-COL{current_layout}-'].update(visible=False)
            current_layout = current_layout + 1 if current_layout < 4 else 1

            #   If there are extra directories in setup_dir after 'setup/', 
            #   give the option to add the extra_dirs to setup_dir and proceed OR ignore
            if extra_dirs_bool and extra_dirs != "":
                extra_dirs_layout = [[sg.Text("We noticed you selected additional directories under 'setups':")],
                                        [sg.Text(f"\n\n{extra_dirs}", text_color='red')],
                                        [sg.Text("\n\nSelect Confirm to copy this folder structure for all the cars in the series")],
                                        [sg.Text("\n... or click Reset to go back and select the base IRacing® setups folder ")],
                    [
                        sg.Button(size=(10, 1), enable_events=True, key="-CONFIRM-", button_text="Next", tooltip='Replicate the above directory structure for all the cars in the class')
                    ],
                    [
                        sg.Button(size=(10, 1), enable_events=True, key="-BACK-", button_text="Reset", tooltip='Go back and re-select the IRacing® setups directory')
                    ],
                ]
                extra_dirs_window = sg.Window("IRacing Handy Helper", extra_dirs_layout)
                while True:
                    event, values = extra_dirs_window.read()
                    if event == "-BACK-":
                        current_layout = 1 # Reset main window
                        break

                    if event == "-CONFIRM-":
                        setup_dir = setup_dir.split("setups/")[0]+'setups/'
                        current_layout = 2 # Reset to series selection page
                        break
                extra_dirs_bool = False
                extra_dirs_window.close()

            #   Perform copy and create a new window for successful transfer
            #   Close both windows on close, Reset to page 1 on reset
            if current_layout == 4:
                #   Clean setup dir from any class directory
                setup_dir = setup_dir.split("setups/")[0]+'setups/'
                for setup in setup_list:
                    selected_series = ""
                    #   Find selected series from the selected radio button
                    for series in series_list:
                        if values["-"+series+"-"] == True:
                            selected_series = series
                            break
                    subdir_list = data[series]["dirs"].split("|")

                    #   Copy to each cars directory including the optional extra_dirs
                    for dir in subdir_list:
                        print(f"copying from: {setup} to {setup_dir}/{dir}/{extra_dirs}")
                        if not os.path.exists(setup_dir+'/'+dir+'/'+extra_dirs):
                            os.makedirs(setup_dir+'/'+dir+'/'+extra_dirs)
                        shutil.copy(setup, setup_dir+'/'+dir+'/'+extra_dirs)
                        transfer_list.append(setup_dir+'/'+dir+'/'+extra_dirs)
                    

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
                completed_window = sg.Window("IRacing Handy Helper", completed_layout)
                while True:
                    event, values = completed_window.read()
                    if event == "-RESET-":
                        transfer_list = []
                        break

                    if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                        window.close()
                        completed_window.close()
                        exit()
                current_layout = 1 # Reset main window
                completed_window.close()

            window[f'-COL{current_layout}-'].update(visible=True)
            print(current_layout)

window.close()