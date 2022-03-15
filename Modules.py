from tkinter import *
from dataclasses import dataclass
import csv
from pathlib import Path

ruletext = "you must offer ten modules for examination \nyou may offer only one module from any one of the sets \nif you wish to qualify in an engineering area, you must follow the specific rules on module choices for that area \nfive modules must be taken in each of Michaelmas and Lent terms.\nyou may not offer more than two modules from Groups E (management). "
guidetext = "Select modules on the left, once you have selected enough modules for an engineering area, the area gets highlighted.\nTo see which modules are needed for an area, click on its name."


# Used to store the modules
@dataclass
class module:
    code: str  # 3 character code of the module
    name: str
    term: str  # Michelmas ("M") or Lent ("L")
    set: int  # The number of the set in which the module is
    prerequisite: str = ""  # List of other modules (codes) needed for this module
    available: bool = True  # Availability based on the modules already selected


# Used to store the engineering areas
@dataclass
class area:
    name: str
    desc: str  # Description
    codes: list()  # Relevant modules (codes)
    eligible: bool = False  # Eligibility based on modules already selected


def importer():  # Reads the two csv files and stores their content in the global variables

    scriptPath = Path(__file__, '..').resolve()  # Store the address of this file, later used for relative addressing

    with open(scriptPath.joinpath("ModuleList.csv"), newline='') as csvfile:  # Read the modules
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            modules.append(module(row[0], row[1], row[2], row[3], row[4]))

    with open(scriptPath.joinpath('Areas.csv'), newline='') as csvfile:  # Read the areas
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [r for r in row if r != ""]  # remove empty columns from end of line
            areas.append(area(row[0], row[1], row[2:]))


def createStaticElements():  # Creates the elements of the window that are static
    window.title("IIA modules")
    # Headers
    Label(window, text="Michelmas modules", bg="lightgrey").grid(column=1, row=0)
    Label(window, text="Lent modules", bg="lightgrey").grid(column=2, row=0)
    Label(window, text="Engineering area", bg="lightgrey").grid(column=3, row=0, columnspan=3)
    # Notes
    Label(window, text="Notes on selected engineering area: ").grid(column=3, row=5)
    # Rules
    Label(window, text="Rules: ").grid(column=3, row=10)
    Label(window, anchor="w", justify="left", text=ruletext).grid(column=4, row=10, rowspan=3, columnspan=2, sticky=W)
    # User's guide
    Label(window, text="User's guide: ").grid(column=3, row=14)
    Label(window, justify="left", text=guidetext).grid(column=4, row=14, columnspan=2, rowspan=3, sticky="N")
    # Reset button
    Button(window, text="Reset", command=lambda: reset()).grid(column=5, row=24, sticky=EW)


def createButtons():  # Creates both types of buttons
    mich = 0  # Modules from each term, starts from 1 to accomodate header row
    lent = 0

    # Module buttons
    for i in range(len(modules)):
        m = modules[i]

        window.mButtons.append(Button(window, text=m.code + " " + m.name + " ",
                                      command=lambda i=i: onmButtonPress(i)))

        if m.prerequisite != "":  # Display the prerequisites
            window.mButtons[i].config(text=m.code + " " + m.name + " (prereq: " + m.prerequisite + ")")

        # Order the modules into two columns
        if m.term == "M":
            mich += 1
            window.mButtons[i].grid(column=1, row=mich, sticky=EW)

        else:
            lent += 1
            window.mButtons[i].grid(column=2, row=lent, sticky=EW)

    # Area buttons
    for i in range(len(areas)):
        a = areas[i]
        window.aButtons.append(Button(window, text=a.name,
                                      command=lambda i=i: onaButtonPress(i)))

        # Order the areass into three  columns
        window.aButtons[i].grid(column=3 + i % 3, row=1 + i // 3, sticky=EW)


def onmButtonPress(i):  # This gets called, when a module button is pressed

    # Add or remove each module with the same code as the one clicked
    for m in modules:
        if modules[i].code == m.code:
            if m in selected:
                selected.remove(m)
            else:
                selected.append(m)

    # Refresh the button colors, availability and qualifications
    refresh()


def onaButtonPress(i):  # This gets called, when an area button is pressed

    codes = []  # the codes of the modules required for the area
    description.config(text=areas[i].desc)  # the description of the area

    if window.aButtons[i].cget("fg") == "blue":  # if area was already selected, deselect it
        window.aButtons[i].config(fg="black")
        codes = []
        description.grid_forget()  # Hide the description
    else:
        description.grid(column=4, row=5, columnspan=2, rowspan=5, sticky="NW")  # Show the description
        for b in window.aButtons:
            b.config(fg="black")  # deselect every other area

        window.aButtons[i].config(fg="blue")  # change the font color of the selected area
        codes = areas[i].codes  # store the requred codes

    # change the color of the module buttons according to the requirements of the area
    for i in range(len(modules)):
        if modules[i].code in codes:
            window.mButtons[i].config(fg="blue")
        else:
            window.mButtons[i].config(fg="black")


def reset():  # This gets called when the reset button is pressed
    selected.clear()
    refresh()


def refresh():  # Refreshes the display, the availability and the qualifications based on the selected modules

    availability()  # Checks which modules can be selected

    for i in range(len(modules)):
        if modules[i] in selected:  # change the selected buttons to green
            window.mButtons[i].config(bg="green")
        else:
            window.mButtons[i].config(bg="SystemButtonFace")

        if modules[i].available:  # disable the unavailable buttons, re-enable the available ones
            window.mButtons[i].config(state="normal")
        else:
            window.mButtons[i].config(state="disabled")

    qualifications()  # Checks the eligibility to the areas based on the selected modules

    for i in range(len(areas)):
        if areas[i].eligible:  # change the area button to green if eligible
            window.aButtons[i].config(bg="green")
        else:
            window.aButtons[i].config(bg="SystemButtonFace")


def availability():  # Check which module can be selected based on the rules

    # Assume every modul can be selected
    for m in modules:
        m.available = True

    scodes = [s.code for s in selected]  # The codes of selected modules

    # Prerequisites
    for m in modules:
        if m.prerequisite != "" and m.prerequisite not in scodes:
            m.available = False
            if m in selected:  # remove from selected if it becomes unavailable after its preq is deselected
                selected.remove(m)

    # Modules in same set
    for s in selected:
        for m in modules:
            if s != m and s.term == m.term and s.set == m.set:
                m.available = False

    # 5 per term and min 1, max 2 management
    lentCount = 0
    michCount = 0
    managementCount = 0
    for s in selected:
        if s.term == "M":
            michCount += 1
        if s.term == "L":
            lentCount += 1
        if s.code[1] == "E":  # management modules
            managementCount += 1

    if michCount == 5:
        for m in modules:
            if m.term == "M" and m not in selected:  # don't disable selected modules, otherwise they can't be deselected
                m.available = False

    if lentCount == 5:
        for m in modules:
            if m.term == "L" and m not in selected:
                m.available = False

    if managementCount == 2:
        for m in modules:
            if m.code[1] == "E" and m not in selected:
                m.available = False

    if len(selected) == 9 and managementCount < 1:  # at least 1 management module must be selected
        for m in modules:
            if m.code[1] != "E" and m not in selected:
                pass
                m.available = False

    # if one half of the double module is unavailable, then the other should not be selected either
    for m in modules:
        for n in modules:
            if n.code == m.code:
                n.available = n.available and m.available
                m.available = n.available


def qualifications():
    scodes = [s.code for s in selected]  # The codes of selected modules

    for a in areas:
        a.eligible = False  # Assume it is not eligible to anything
        count = 0
        count2 = 0

        # The rules for each module is in a.desc

        if a.name == "Aerospace and Aerothermal Engineering":
            if "3A1" in scodes and "3A3" in scodes:
                for sc in scodes:
                    if sc != "3A1" and sc != "3A3" and sc in a.codes:
                        count += 1
            if count >= 2:
                a.eligible = True

        elif a.name == "Electrical and Electronic Engineering":
            a.eligible = all(ac in scodes for ac in a.codes)  # true if all member of a.codes is in scodes

        elif a.name == "Instrumentation and Control":
            if "3F1" in scodes or "3F2" in scodes:
                for sc in scodes:
                    if sc != "3F1" and sc != "3F2" and sc in a.codes:
                        count += 1

            if count >= 5:
                a.eligible = True

        elif a.name == "Bioengineering":
            biomodules = ["3G1", "3G2", "3G3", "3G4", "3G5", ]
            for sc in scodes:
                if sc in a.codes:
                    count += 1
                if sc in biomodules:
                    count2 += 1

            if count >= 6 and count2 >= 3:
                a.eligible = True

        else:
            for sc in scodes:
                if sc in a.codes:
                    count += 1

            if a.name == "Electrical and Information Sciences":
                a.eligible = count >= 8
            else:
                a.eligible = count >= 6


# To store the imported data
modules = list()
areas = list()
selected = list()  # The modules get added to this list when they get selected

importer()  # Read the module and area list csv files

window = Tk()  # The main window of the application

createStaticElements()

window.mButtons = []  # Array to store the module buttons
window.aButtons = []  # Array to store the area buttons
createButtons()

description = Message(window)  # Global variable to store the descriprion of the selected area

refresh()  # A refresh is needed to apply the inital constrains (prerequisites)

window.mainloop()
