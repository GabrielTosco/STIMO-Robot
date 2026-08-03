import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
import random
import sys
import traceback


_DPAD_TARGET = None


def set_dpad_target(widget):
    """Route physical D-pad events to the currently active window."""
    global _DPAD_TARGET
    _DPAD_TARGET = widget

def check_dpad_file(root):
    try:
        with open("dpad_input.txt", "r+") as f:
            command = f.read().strip()
            f.seek(0)
            f.truncate()
        if command:
            target = _DPAD_TARGET or root   # <--- route to active window
            if command == "UP":
                target.event_generate("<Up>")
            elif command == "DOWN":
                target.event_generate("<Down>")
            elif command == "LEFT":
                target.event_generate("<Left>")
            elif command == "RIGHT":
                target.event_generate("<Right>")
            elif command == "ENTER":
                target.event_generate("<Return>")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[D-PAD] File read error: {e}")

    root.after(100, lambda: check_dpad_file(root))




# --- Pygame Import and Check ---
try:
    import pygame
except ImportError:
    # Use Tkinter for the error message if Pygame isn't found
    root_check = tk.Tk()
    root_check.withdraw() # Hide the root window
    messagebox.showerror("Fatal Error",
                         "Pygame module not found.\n"
                         "Please install it using:\n\n"
                         "pip install pygame\n\n"
                         "The application will now exit.")
    root_check.destroy()
    sys.exit(1) # Exit the script

# --- Constants ---

# Colors (RGB Tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHT_BLUE = (173, 216, 230) # Background for Hangman, Word Scramble
GRAY = (200, 200, 200)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
FILL_IN_BG = (230, 230, 250)      # Lavender background for Fill-in-Blank
ODD_ONE_OUT_BG = (255, 250, 205) # Lemon Chiffon background for OddOneOut
INPUT_BOX_COLOR_INACTIVE = (220, 220, 220)
INPUT_BOX_COLOR_ACTIVE = WHITE
INPUT_TEXT_COLOR = BLACK
HINT_COLOR = (50, 50, 50)         # Dark gray for hints/questions
OPTION_BG_NORMAL = GRAY
OPTION_BG_HOVER = (170, 170, 170)
OPTION_BG_CORRECT = DARK_GREEN
OPTION_BG_INCORRECT = DARK_RED
OPTION_TEXT_COLOR = BLACK
OPTION_TEXT_COLOR_RESULT = WHITE
ATTEMPTS_COLOR_NORMAL = BLUE
ATTEMPTS_COLOR_LOW = RED
ATTEMPTS_COLOR_CRITICAL = DARK_RED
# --- NEW End Screen Colors ---
END_SCREEN_OVERLAY_COLOR = (0, 0, 0, 180) # Semi-transparent black
END_SCREEN_BUTTON_BG = (70, 70, 70) # Dark gray button
END_SCREEN_BUTTON_HOVER_BG = (100, 100, 100) # Lighter gray on hover
END_SCREEN_BUTTON_TEXT_COLOR = WHITE


# Screen dimensions (Used for windowed mode and Pygame setup)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Font sizes
QUESTION_FONT_SIZE = 28
WORD_FONT_SIZE = 48
GUESS_FONT_SIZE = 24
MSG_FONT_SIZE = 30
INFO_FONT_SIZE = 20
TITLE_FONT_SIZE = 22
SCORE_FONT_SIZE = 26
SCRAMBLED_WORD_FONT_SIZE = 60
SENTENCE_FONT_SIZE = 32
INPUT_FONT_SIZE = 32
OPTION_FONT_SIZE = 26
ATTEMPTS_FONT_SIZE = 24 # Font size for attempts display
# --- NEW End Screen Font ---
END_SCREEN_FONT_SIZE = 28


# Game Constants
TOTAL_SESSION_ATTEMPTS = 3         # <-- UNIVERSAL ATTEMPT LIMIT FOR ALL GAMES
MAX_MISTAKES_DRAW_HANGMAN = 6      # Number of hangman drawing stages (0 to 6) - Specific to Hangman drawing
MAX_ITEMS_PER_SESSION = 10         # Max questions/items per game session
BLANK_MARKER = "[BLANK]"           # Marker for Fill-in-the-Blank game

# --- Game Status Constants (for run return) ---
GAME_QUIT = "QUIT" # User chose "Back" or hit ESC/Close
GAME_ERROR = "ERROR" # Unexpected error during game

# --- Handout Viewing Function ---

# !!! IMPORTANT !!!
# UPDATE THIS PATH to the actual location of your 'handout' folder.
BASE_HANDOUT_PATH = r"/home/stimo/STIMO_Mode/handout"
# <--- PALITAN ITO

# Dictionary mapping handout keys to their full file paths.
HANDOUT_PATHS = {
    # FMSS (Fundamentals of Mixed Signals and Sensors)
    "FMSS_Handout_1": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_1.pdf"), # Prelim
    "FMSS_Handout_2": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_2.pdf"), # Prelim
    "FMSS_Handout_3": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_3.pdf"), # Midterm
    "FMSS_Handout_4": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_4.pdf"), # Midterm
    "FMSS_Handout_5": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_5.pdf"), # Pre-Final
    "FMSS_Handout_6": os.path.join(BASE_HANDOUT_PATH, "FMSS_Handout_6.pdf"), # Final

    # DDC (Data and Digital Communication)
    "DDC_Handout_1": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_1.pdf"),   # Prelim
    "DDC_Handout_2": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_2.pdf"),   # Prelim
    "DDC_Handout_3": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_3.pdf"),   # Midterm
    "DDC_Handout_4": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_4.pdf"),   # Midterm
    "DDC_Handout_5": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_5.pdf"),   # Pre-Final
    "DDC_Handout_6": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_6.pdf"),   # Pre-Final
    "DDC_Handout_7": os.path.join(BASE_HANDOUT_PATH, "DDC_Handout_7.pdf"),   # Final
    # MR (Methods of Research)
    "MR_Handout_1": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_1.pdf"),    # Prelim
    "MR_Handout_2": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_2.pdf"),    # Prelim
    "MR_Handout_3": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_3.pdf"),    # Midterm
    "MR_Handout_4": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_4.pdf"),    # Midterm
    "MR_Handout_5": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_5.pdf"),    # Pre-Final
    "MR_Handout_6": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_6.pdf"),    # Pre-Final
    "MR_Handout_7": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_7.pdf"),    # Final
    "MR_Handout_8": os.path.join(BASE_HANDOUT_PATH, "MR_Handout_8.pdf"),    # Final
    # CSA (Computer System Architecture)
    "CSA_Handout_1": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_1.pdf"),   # Prelim
    "CSA_Handout_2": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_2.pdf"),   # Prelim
    "CSA_Handout_3": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_3.pdf"),   # Midterm
    "CSA_Handout_4": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_4.pdf"),   # Midterm
    "CSA_Handout_5": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_5.pdf"),   # Pre-Final
    "CSA_Handout_6": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_6.pdf"),   # Pre-Final
    "CSA_Handout_7": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_7.pdf"),   # Final
    "CSA_Handout_8": os.path.join(BASE_HANDOUT_PATH, "CSA_Handout_8.pdf"),   # Final
    # LCD (Logic Circuits and Design)
    "LCD_Handout_1": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_1.pdf"),   # Prelim
    "LCD_Handout_2": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_2.pdf"),   # Prelim
    "LCD_Handout_3": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_3.pdf"),   # Midterm
    "LCD_Handout_4": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_4.pdf"),   # Midterm
    "LCD_Handout_5": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_5.pdf"),   # Pre-Final
    "LCD_Handout_6": os.path.join(BASE_HANDOUT_PATH, "LCD_Handout_6.pdf"),   # Final
    # EE (Engineering Economics)
    "EE_Handout_1": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_1.pdf"),    # Prelim
    "EE_Handout_2": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_2.pdf"),    # Prelim
    "EE_Handout_3": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_3.pdf"),    # Midterm
    "EE_Handout_4": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_4.pdf"),    # Midterm
    "EE_Handout_5": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_5.pdf"),    # Pre-Final
    "EE_Handout_6": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_6.pdf"),    # Pre-Final
    "EE_Handout_7": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_7.pdf"),    # Final
    "EE_Handout_8": os.path.join(BASE_HANDOUT_PATH, "EE_Handout_8.pdf"),    # Final
    # FCS (Feedback and Control System)
    "FCS_Handout_1": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_1.pdf"),   # Prelim
    "FCS_Handout_2": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_2.pdf"),   # Prelim
    "FCS_Handout_3": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_3.pdf"),   # Midterm
    "FCS_Handout_4": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_4.pdf"),   # Midterm
    "FCS_Handout_5": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_5.pdf"),   # Pre-Final
    "FCS_Handout_6": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_6.pdf"),   # Pre-Final
    "FCS_Handout_7": os.path.join(BASE_HANDOUT_PATH, "FCS_Handout_7.pdf"),   # Final
    # CAD (Computer-Aided Drafting)
    "CAD_Handout_1": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_1.pdf"),   # Prelim
    "CAD_Handout_2": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_2.pdf"),   # Prelim
    "CAD_Handout_2-1": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_2-1.pdf"),# Prelim
    "CAD_Handout_2-2": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_2-2.pdf"),# Prelim
    "CAD_Handout_3": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_3.pdf"),   # Midterm
    "CAD_Handout_4": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_4.pdf"),   # Midterm
    "CAD_Handout_5": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_5.pdf"),   # Pre-Final
    "CAD_Handout_6": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_6.pdf"),   # Pre-Final
    "CAD_Handout_7": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_7.pdf"),   # Final
    "CAD_Handout_7-1": os.path.join(BASE_HANDOUT_PATH, "CAD_Handout_7-1.pdf"),# Final
}

def view_handout(handout_key):
    """Attempts to open the specified handout file using the default system viewer."""
    file_path = HANDOUT_PATHS.get(handout_key)
    if file_path and os.path.exists(file_path):
        try:
            normalized_path = os.path.normpath(file_path) # Clean up path separators
            print(f"Attempting to open handout: {normalized_path}")
            if sys.platform == "win32":
                os.startfile(normalized_path) # Recommended way for Windows
            else:
                file_uri = 'file:///' + normalized_path.replace('\\', '/')
                webbrowser.open(file_uri)
        except Exception as e:
            messagebox.showerror("Error Opening Handout",
                                 f"Could not open '{handout_key}'.\nError: {e}\nPath: {normalized_path}")
            print(f"Error opening {normalized_path}: {e}")
            traceback.print_exc()
    elif file_path:
        messagebox.showerror("File Not Found",
                             f"File not found for '{handout_key}':\n{file_path}\n\n"
                             f"Please check the BASE_HANDOUT_PATH ('{BASE_HANDOUT_PATH}') and ensure the file exists.")
        print(f"File not found: {file_path}")
    else:
         messagebox.showerror("Invalid Handout Key",
                              f"Handout key '{handout_key}' not defined in HANDOUT_PATHS.")
         print(f"Invalid handout key: {handout_key}")

# --- Universal Game Data Loading Function ---
def load_game_data_by_handout():
    """Loads game data grouped by handout_key. Defines content for all games."""
    data = {
        # --- Computer-Aided Drafting ---
        "CAD_Handout_1": [
            ("CAD technology is extensively employed primarily because of its accuracy and productivity, replacing which traditional method?", "Hand drafting"),
("Which term traditionally emphasizes the creation of precise technical drawings, schematics, and blueprints?", "Computer-Aided Drafting "),
("What are engineering drawings primarily used for, according to the text?", "materials"),
("The standardization of drawing techniques and the mass production of blueprints became significant during which historical period mentioned in the text?", "Industrial Era"),
("The handout emphasizes that the cost and loss of control associated with fixing design errors tend to do what as the product lifecycle progresses?", "Grow exponentially"),
("Rapid prototyping primarily accelerates development and reduces costs by utilizing fast-paced fabrication methods, predominantly involving:", "Additive manufacturing"),
("What does the engineering methodology DFMA stand for?", "DMA"),
("Which component of DFMA specifically focuses on aspects like material selection, simplified geometry, and using standard parts to ease the production of individual components?", "DFM "),
("Designing parts to minimize their quantity and ensuring they can only be put together correctly mistake-proofing are key principles of which methodology?", "DFA "),
("According to the handout, a major benefit of implementing DFMA principles during the design stage is:", "Reduced manufacturing")],

        "CAD_Handout_2": [
            ("What is the term for the creative process engineers use to achieve outcomes?", "Design"),
("What is the first step in Krick's design process?", "Problem Formulation"),
("Which step involves gathering lots of information about the problem?", "Problem Analysis"),
("Which step is about finding many different possible solutions?", "Search for Alternative Solutions"),
("What step involves choosing the best solution from the alternatives?", "Decision Making"),
("What is the final step where you prepare all the information and reports?", "Documentation"),
("What is the name for a virtual copy of a physical object used in design?", "Digital Twin"),
("What computer tool is the foundation for creating a Digital Twin?", "CAD"),
("What method uses virtual testing to check a design before building it?", "Modeling and Simulation"),
("What should designs focus on to make sure they are useful?", "Needs and requirements of intended users")],

        "CAD_Handout_2-1": [
            ("In CAD, what is a 2D representation used as a base for 3D features called?", "sketch"),
            ("How many dimensions does a standard CAD sketch have?", "Two Dimensions "),
            ("What are the basic shapes like lines, circles, and arcs called in sketching?", "Sketch primitives"),
            ("What is the name of the flat surface where a 2D sketch is created?", "Sketch Plane "),
    ("What controls how sketch shapes are positioned relative to each other?", "Geometric relationships "),
    ("What constraint makes two lines run side-by-side without ever meeting?", "Parallel"),
    ("Which tool is used to add rounded corners to a sketch?", "Fillet"),
    ("Which tool is used to cut off unwanted parts of a sketched line?", "Trim"),
    ("What type of lines or shapes are used for reference only and ignored when creating the 3D feature?", "Construction element"),
    ("What is the point (0,0,0) where the three main planes intersect called?", "Origin")
        ],
        "CAD_Handout_2-2": [
            ("What is the process of creating a digital prototype by modeling individual components called?",  "Part modeling"),
            ("What is an individual, self-contained component designed as a distinct entity called?", "A part"),
            ("Which modeling technique uses dimensions and mathematical rules (parameters and constraints) to drive the geometry?",
             "Parametric Modeling"),
            ("What is a key benefit of using parameters in modeling?", "Flexibility"),
            ("Which modeling technique uses building blocks like holes, slots, and fillets?", "Feature Modeling"),
            ("What is a key advantage of using Feature Modeling?", "Ease of Modification"),
            ("What command extends a 2D sketch along a straight path to add depth?", "Extrude"),
            ("What command creates a shape by rotating a sketch around a central axis?", "Revolve"),
            ("What command creates a shape by moving a profile along a path?", "Sweep"),
            ("What is the term for geometric profiles removed from a solid?", "Cutouts"),
        ],
        "CAD_Handout_3": [
            ("What technique creates 3D models by defining specific geometric and functional entities called features?",
             "Feature Modeling"),
            ("Which iterative design method replicates features linearly or in a grid?", "Linear Pattern"),
            ("Which iterative design method replicates features around a defined axis?", "Circular Pattern"),
            ("What displays the history and hierarchy of features in a part or assembly?",
             "Feature Tree / Feature List"),
            ("In Ordered-Parametric Modeling, what happens if a dependent feature is moved before its parent?",
             "Errors may occur"),
            ("Which feature modeling technique uses commands like revolve or sweep to remove material?",
             "Advanced Cutouts"),
            ("Which feature removes material by connecting two or more 2D profiles smoothly?", "Loft cutout"),
            ("What term describes features like fillets, chamfers, and ribs used to modify parts?",
             "Treatment Features"),
            ("Which treatment feature applies an internal rounded corner (concave)?", "Fillet"),
            ("Which treatment feature adds a beveled or angled corner or edge?", "Chamfers"),
        ],
        "CAD_Handout_4": [
            (
            "What modeling technique designs intricate geometric features using representations without mass or thickness?",
            "Surface modeling"),
            ("What do surfaces, as one-sided representations, lack?", "Mass and thickness"),
            ("What is the typical starting point or foundation for constructing surfaces?", "2D Geometry"),
            ("Which surfacing feature extends a 2D profile normal to its sketch plane without adding volume?",
             "Extrude Surface"),
            ("Which surfacing feature creates a surface by rotating a profile around a specified axis?",
             "Revolve Surface"),
            ("Which surfacing feature creates a surface by pushing a profile along a defined path?", "Sweep Surface"),
            ("Which surfacing feature creates a surface by blending through a series of profiles?", "Loft Surface"),
            ("Which feature creates a surface parallel to an existing face or surface at a specified distance?","Offset Surface"),
            ("Which operation combines surfaces or solids that share edges into a single entity?", "Boolean Union"),
            ( "Which feature creates a solid part from surfaces or planes that form a fully enclosed volume?", "Enclose"),
        ],
        "CAD_Handout_5": [
            (    f"{BLANK_MARKER} is the process of designing and organizing multiple components within an assembly to ensure they work together as intended.",  "Assembly Modeling"),
            (   f"An {BLANK_MARKER} is a hierarchical structure where parts and subassemblies are organized, and their relationships and degrees of freedom are defined.",  "assembly"),
            ( f"{BLANK_MARKER}, the common term for assembly relationships, define how parts are connected or positioned relative to each other in an assembly.",     "Mates"),
            (f"A {BLANK_MARKER} mate locks two parts together with no movement allowed.", "Fastened"),
            (f"A {BLANK_MARKER} mate allows rotation around a fixed axis between two parts.", "Revolute"),
            (f"A {BLANK_MARKER} mate allows linear movement along a fixed path without rotation.", "Slider"),
            (f"The {BLANK_MARKER} approach is a part-centric modeling method where the assembly design begins with a primary structural or functional element.", "Bottom-Up"),
            ( f"The {BLANK_MARKER} approach is an assembly-centric modeling method where the design starts at the highest assembly level.",  "Top-Down"),
            ( f"{BLANK_MARKER} is constructing a part in the context of a given assembly, using surrounding components as references.", "Part Assembly Modeling"),
            (  f"{BLANK_MARKER} are used in CAD assemblies to visually break down complex assemblies into individual parts, showing how components fit together.",  "Exploded views"),
        ],
        "CAD_Handout_6": [
            (
            f"{BLANK_MARKER} drawings play a principal role in the product development process, serving as a primary means of communication between engineers, designers, and stakeholders.","Computer-aided design"),
            (f"One of the five fundamental purposes of CAD drawings is {BLANK_MARKER}, sharing design information clearly among everyone involved.", "Communication"),
            (f"Adhering to established {BLANK_MARKER} in technical drawing ensures consistency, accuracy, and effective communication.",  "standards"),
            ( f"The {BLANK_MARKER} is a major organization in the United States that oversees drawing standards, with ASME developing and maintaining them.","American National Standards Institute "),
            (f"{BLANK_MARKER} in CAD drawings define the size, location, and relationships of model features.", "Dimensions"),
            ( f"{BLANK_MARKER} are notes added to a drawing that clarify or provide specific information relevant to the part.", "Annotations"),
            ( f"The {BLANK_MARKER} on a drawing sheet contains information like the drawing title, part number, author, date, and scale.", "Title Block"),
            ( f"A {BLANK_MARKER} drawing thoroughly defines a part for manufacturing, including orthogonal views, dimensions, and tolerances.","Detail"),
            (f"Standard {BLANK_MARKER} Views use projections of a part from three standard planes: Front, Top, and Right.","Orthogonal"),
            ( f"{BLANK_MARKER} views, like isometric or trimetric, show 3D perspectives but are not used for dimensioning.","Pictorial"),
        ],
        "CAD_Handout_7": [
            ("What is the term for the acceptable limit of variation for a dimension in engineering drawings?",
             ["Allowance", "Clearance", "Tolerance", "Interference"], "Tolerance"),
            (
            "When comparing mutually exclusive alternatives where revenues differ, which alternative should generally be selected?",
            ["The one with the lowest initial investment.", "The one with the shortest useful life.",
             "The one with the greatest positive equivalent worth (e.g., PW, AW, FW) at MARR.",
             "The one requiring the least maintenance."],
            "The one with the greatest positive equivalent worth (e.g., PW, AW, FW) at MARR."),
            (
            "Which error detection method adds a single bit to a character to create either an even or odd number of 1s?",
            ["Checksum", "Parity Check (Vertical Redundancy Check)", "Cyclic Redundancy Checksum",
             "Longitudinal Redundancy Check"], "Parity Check (Vertical Redundancy Check)"),
            (
            "Which mode of I/O data transfer requires constant monitoring of the peripheral by the CPU for each data item transfer?",
            ["Direct Memory Access (DMA)", "Interrupt Initiated I/O", "Programmed I/O", "Buffered I/O"],
            "Programmed I/O"),
            (
            "Which random sampling method involves dividing the population into homogeneous groups (strata) and then randomly sampling from each group?",
            ["Simple Random Sampling", "Systematic Sampling", "Cluster Sampling", "Stratified Sampling"],
            "Stratified Sampling"),
            (
            "Which type of binary code follows the positional weighting principle, where each position represents a specific weight (e.g., 8421 BCD)?",
            ["Gray Code", "Excess-3 Code", "Weighted Code", "Reflective Code"], "Weighted Code"),
            ("What term describes the difference between a measured value and its true value?",
             ["Precision", "Accuracy", "Resolution", "Error"], "Error"),
            ("In a Signal Flow Graph (SFG), what does a node represent?",
             ["A system gain", "A variable", "A summing point", "A direction of flow"], "A variable"),
            (
            "Which protocol translates an IP address into the appropriate Medium Access Control (MAC) layer address for delivery on a local network?",
            ["DHCP", "ARP", "ICMP", "UDP"], "ARP"),
            ("Which assembly mate allows rotation around a fixed axis but prevents other types of movement?",
             ["Slider mate", "Fastened mate", "Revolute mate", "Ball mate"], "Revolute mate"),
        ],
        "CAD_Handout_7-1": [
            (
            "Which tool forecasts the behavior of engineering components, allowing maintenance scheduling before failure?",
            ["CAD Modeling", "Finite Element Analysis", "Modal Analysis", "Tolerance Analysis"],
            "Finite Element Analysis"),
            (
            "What does the 'F' in FEA stand for, representing the mathematical simulation of physical structures under force?",
            ["Force", "Functional", "Finite", "Foundational"], "Finite"),
            ("In FEA, what term defines how a model is constrained, such as having fixed or free surfaces?",
             ["Loads", "Materials", "Fixtures (Boundary Conditions)", "Connections"], "Fixtures (Boundary Conditions)"),
            (
            "What term refers to the relationships between parts in an assembly that define their interaction during a simulation?",
            ["Fixtures", "Loads", "Materials", "Connections"], "Connections"),
            ("What are the forces or moments applied to components during an FEA simulation called?",
             ["Loads", "Fixtures", "Constraints", "Materials"], "Loads"),
            ("For reliable results in structural FEA, assigning accurate properties for which aspect is crucial?",
             ["Fixture", "Load", "Material", "Connection"], "Material"),
            ("Which stress measure combines stresses to predict when a material might yield under complex loading?",
             ["Max Principal Stress", "Signed von Mises Stress", "Von Mises Stress", "Safety Factor"],
             "Von Mises Stress"),
            (
            "What ratio compares a material's yield strength to the applied stress (von Mises) to indicate design robustness?",
            ["Displacement Factor", "Stress Ratio", "Safety Factor", "Deformation Scale"], "Safety Factor"),
            ("Which simulation result shows the amount each part of a model moves under an applied load?",
             ["Stress", "Strain", "Displacement", "Safety Factor"], "Displacement"),
            (
            "Which type of analysis helps understand how a structure responds to vibrations by identifying natural frequencies and mode shapes?",
            ["Structural Analysis", "Thermal Analysis", "Modal Analysis", "Tolerance Analysis"], "Modal Analysis"),
        ],
        # --- Feedback and Control System ---
        "FCS_Handout_1": [
            ("In a control system, what component measures the variable being controlled?", "Sensor"),
            ("What is the device called that directly influences the controlled variable?", "Actuator"),
            ("What term describes unwanted inputs that affect the system's output?", "Disturbance"),
            ("What is the combination of the process and the actuator known as?", "Plant"),
            ("Which system type lacks a feedback mechanism to correct the output?", "Open-loop system"),
            ("Which system type uses feedback to compare the actual output with the desired input?","Closed-loop system"),
            ("What problem can occur if a closed-loop system is improperly designed?", "Instability"),
            ("What is a disadvantage of adding components like controllers and sensors to a system?", "Cost"),
            ("What is the first step in the Control System Design Flowchart?", "Objectives"),
            ("What is the process of turning a physical system into mathematical equations called?", "Modeling"),
        ],
        "FCS_Handout_2": [
            ("Which category of model is described using only words?", "Verbal Models"),
            ("Which category of model uses mathematical equations?", "Mathematical Models"),
            ("What type of equation involves derivatives of dependent variables?", "Differential equations"),
            ("What determines the order of an Ordinary Differential Equation (ODE)?", "Highest differential term"),
            ("If an ODE has coefficients that depend on the dependent variable (like y), what is it called?", "Non-linear"),
            ("What is the fundamental law used for modeling simple mechanical systems involving force and mass?", "Newton's second law"),
            ("What mathematical transform converts time-domain functions to the frequency domain (s-domain)?", "Laplace Transform"),
            ("In the s-domain, what is the impedance representation of an inductor L?", "sL"),
            ("In the s-domain, what is the impedance representation of a capacitor C?", "1/sC"),
            ("What type of diagram uses boxes and arrows to show input-output relationships between system components?",
             "Block diagrams"),
        ],
        "FCS_Handout_3": [("Mathematical representation of a system.", "MODEL"), ("Ratio of output to input in Laplace domain.", "TRANSFER-FUNCTION"), ("Visual representation of system components.", "BLOCK-DIAGRAM")],
        "FCS_Handout_4": [("System response without input.", "NATURAL-RESPONSE"), ("System response due to input.", "FORCED-RESPONSE"), ("Time to reach steady state.", "SETTLING-TIME")],
        "FCS_Handout_5": [
            (
            f"A {BLANK_MARKER} consists of unidirectional and operational blocks, representing the transfer function of variables.",
            "block diagram"),
            (f"In a block diagram, lines with arrows denote {BLANK_MARKER}, not wires.", "signals"),
            (f"In a block diagram, {BLANK_MARKER} denote systems and normally contain the mathematical representation.",
             "Boxes"),
            (
            f"The main goal of block diagram transformation is to reduce any system to a {BLANK_MARKER} block diagram.",
            "simple"),
            (
            f"The connection type where the output of one block serves as the input to the next is called a {BLANK_MARKER} or series connection.",
            "cascade"),
            (
            f"A {BLANK_MARKER} point is considered as a point where a signal is sampled and interconnected to other blocks.",
            "pickoff"),
            ( f"The most commonly used type of block diagram connection in automatic control systems is the {BLANK_MARKER} connection.","feedback"),
            ( f"For a negative feedback loop with forward path G(s) and feedback path H(s), the simplified transfer function is G(s) / (1 {BLANK_MARKER} G(s)H(s)).","+"),
            (f"For a positive feedback loop with forward path G(s) and feedback path H(s), the simplified transfer function is G(s) / (1 {BLANK_MARKER} G(s)H(s)).",  "-"),
            (f"For blocks G1 and G2 connected in {BLANK_MARKER}, the transformed single block is G1 + G2.", "parallel"),
        ],
        "FCS_Handout_6": [
            (f"An alternative method to block diagram reduction is the {BLANK_MARKER} (SFG).", "signal flow graph"),
            (
            f"In an SFG, a {BLANK_MARKER} shows the dependence of one variable (node) on another and has both GAIN and DIRECTION.",
            "branch"),
            (f"In an SFG, a {BLANK_MARKER} is used to represent a variable.", "node"),
            (
            f"A node is a {BLANK_MARKER} node (input node) if all branches connected to the node are leaving the node.",
            "source"),
            (
            f"A node is a {BLANK_MARKER} node (output node) if all branches connected to the node are entering the node.",
            "sink"),
            (f"A {BLANK_MARKER} path is a path from a source to a sink in an SFG.", "forward"),
            (
            f"A {BLANK_MARKER} is a closed path in an SFG that originates and terminates on the same node, without meeting any node twice.",
            "loop"),
            (f"Loops are {BLANK_MARKER} loops if the two loops do not have a common node.", "non-touching"),
            (
            f"The main formula for determining the transfer function of a given signal flow graph is called {BLANK_MARKER}.",
            "Mason's Gain Rule"),
            (f"In Mason's Gain Rule, {BLANK_MARKER} represents the kth forward path gain.", "Fk"),
        ],
        "FCS_Handout_7": [
            (
            "What type of analysis deals with understanding systems by looking at the frequency content of the system transfer function?",
            ["Time Domain Analysis", "Frequency Analysis", "Stability Analysis", "Transient Analysis"],
            "Frequency Analysis"),
            ("In the Laplace transform variable 's', what does 's' represent?",
             ["Time constant", "Damping ratio", "Complex frequency", "Gain"], "Complex frequency"),
            ("According to the handout, what does a linear system introduce to a signal passed through it?",
             ["Frequency change only", "Magnitude and/or phase change only", "Harmonic distortion",
              "Signal delay only"], "Magnitude and/or phase change only"),
            (
            "What type of plot graphs the magnitude (in dB) and phase (in degrees) of a transfer function versus frequency?",
            ["Nyquist plot", "Root Locus plot", "Nichols chart", "Bode plot"], "Bode plot"),
            ("The Barkhausen criterion for stability focuses on which part of a feedback system?",
             ["Forward path transfer function G(s)", "Feedback path transfer function H(s)",
              "Loop transfer function GH(s)", "Reference Input R(s)"], "Loop transfer function GH(s)"),
            ("In a first-order time response, what is characteristic?",
             ["Overshoot", "Ringing", "No overshoot", "Multiple oscillations"], "No overshoot"),
            ("What parameter in a second-order system indicates how much the response goes over the final value?",
             ["Rise time", "Settling time", "Overshoot", "Damping ratio"], "Overshoot"),
            (
            "What is the slope of the magnitude Bode plot (asymptote) for a first-order pole after its corner frequency?",
            ["+20 dB/decade", "-20 dB/decade", "+40 dB/decade", "-40 dB/decade"], "-20 dB/decade"),
            (
            "What component in a transfer function results in a constant -20 dB/decade slope on the magnitude Bode plot?",
            ["First-order zero", "First-order pole", "Integrator", "Differentiator"], "Integrator"),
            ("What is the phase shift introduced by a simple integrator (1/s) in a Bode plot?",
             ["0 degrees", "+90 degrees", "-90 degrees", "-180 degrees"], "-90 degrees"),
        ],
        # --- Engineering Economics ---
        "EE_Handout_1": [
            ("What discipline deals with the economic aspects of engineering projects?", "Engineering Economics"),
            ("According to Principle 1, how can alternatives be developed?", "Brainstorming session"),
            ("What is the study of wants, efforts, wealth, and satisfaction called?", "Economics"),
            ("Name one of the four factors of production mentioned.", "Land"),
            ("What basic economic activity means the use of goods/services for satisfaction?", "Consumption"),
            ("What kind of relationship exists between price and quantity in the Law of Demand?", "Inverse relationship"),
            ( "What kind of relationship exists between price and quantity in the Law of Supply?", "Direct relationship"),
            ("What are goods/services directly used by people called?", "Consumer goods and services"),
            ("What type of cost does not change with the level of activity?", "Fixed costs"),
            ("What is the cost of something that has already happened and cannot be recovered called?", "Sunk cost"),
        ],
        "EE_Handout_2": [
            ("What concept indicates that money increases in value over time due to earned interest?",
             "Time Value of Money"),
            ("What type of capital is obtained from lenders for investment?", "Debt Capital"),
            ("What term describes the amount paid for borrowing money, often expressed as a percentage?", "Interest"),
            ("What is the term for interest earned expressed as a percentage of the principal amount?",
             "Rate of return (ROR)"),
            ("Which type of interest calculation is linearly proportional to the principal, rate, and time?",
             "Simple interest"),
            ("Which type of interest is based on the principal plus any accumulated interest from previous periods?",
             "Compound Interest"),
            ("What concept states that different sums of money at different times can be equal in economic value?",
             "Economic Equivalence"),
            ("What is the graphical representation of cash flows drawn on a time scale called?", "Cash Flow Diagram"),
            ("In a cash flow diagram, what do upward arrows represent?", "Receipts / Cash inflows"),
            ("In cash flow notation, what does 'F' stand for?", "Future sum of money"),
        ],
        "EE_Handout_3": [
            ("Which analysis method is based on the equivalent worth of cash flows at the beginning point in time?",
             "Present Worth Method"),
            ("What does a positive Present Worth (PW) indicate about an investment project?",
             "Amount of profit over minimum required"),
            ("What is the value of a bond at any time?", "The PW of future cash receipts"),
            ("Which analysis method computes the equivalent worth of a project at the end of its investment period?",
             "Future Worth Method"),
            ("Which method involves an equal annual series of amounts equivalent to cash flows over a study period?",
             "Annual Worth Method"),
            ("What is a series of equal payments occurring at equal periods of time called?", "Annuity"),
            ("What type of annuity has cash flows that do not begin until some later date?", "Deferred annuity"),
            ("What term describes cash flows that increase or decrease by a uniform amount each period?",
             "Gradients / Uniform gradient"),
            (
            "Which method solves for the interest rate that equates the equivalent worth of cash inflows and outflows?",
            "Internal Rate of Return (IRR) Method"),
            (
            "Which rate of return method directly accounts for the interest rate at which net cash flows can be reinvested?",
            "External Rate of Return (ERR) Method"),
        ],
        "EE_Handout_4": [
            ("What condition exists when the decision-maker can estimate outcome probabilities?",
             "Decisions under risk"),
            ("What condition exists when outcome probabilities cannot be estimated?", "Decision under uncertainty"),
            ("Name one major source of uncertainty in engineering economy studies mentioned.",
             "Possible inaccuracy of the cash-flow estimates"),
            (
            "What is the relative magnitude of change in a measure of merit caused by changes in estimated factors called?",
            "Sensitivity"),
            ("What analysis determines how a measure of worth changes if a parameter varies over a range?",
             "Sensitivity analysis"),
            ("Which sensitivity analysis technique is common when a decision depends heavily on one uncertain factor?",
             "Break-Even Analysis"),
            ("What is the value of a factor at which two alternatives are equally desirable called?",
             "Break-even point"),
            ("Name one of the three important factors mentioned for analyzing a proposed business venture.",
             "Capacity Utilization"),
            ("What is one common factor used for break-even analysis?", "Equipment life"),
            (
            "What conservative practice involves using a truncated project life, shorter than the estimated useful life?",
            "Reduction of Useful Life"),
        ],
        "EE_Handout_5": [
            (f"{BLANK_MARKER} is the decrease in the value of physical properties through time.", "Depreciation"),
            (
                f"{BLANK_MARKER} property is the property that is eligible for depreciation deductions such as vehicles, real estate, machinery, and heavy equipment.",
                "Depreciable"),
            (f"Depreciable property is classified as either {BLANK_MARKER} or intangible.", "tangible"),
            (
                f"{BLANK_MARKER} depreciation is applied because of the lessening of a property's physical ability to produce results.",
                "Physical"),
            (
                f"{BLANK_MARKER} depreciation or obsolescence is applied because of the lessening in demand for the function that the property was designed to render.",
                "Functional"),
            (f"The {BLANK_MARKER} value (F) is the estimated value of a property at the end of its depreciable life.",
             "salvage"),
            (f"The symbol BVn represents the {BLANK_MARKER} of the asset at the end of year n.", "book value"),
            (
                f"The {BLANK_MARKER} Method is the simplest and most widely used depreciation method, assuming a constant amount depreciated each year.",
                "Straight Line"),
            (
                f"The {BLANK_MARKER} Method considers the digits corresponding to the number of each permissible year of life.",
                "Sum-of-the-Years-Digit "),
            (
                f"The {BLANK_MARKER} Method assumes that the annual cost of depreciation is a fixed percentage of the book value at the beginning of the year.",
                "Declining Balance "),
        ],
        "EE_Handout_6": [
            (
            f"When the selection of one feasible alternative excludes the choice of any other alternatives, the alternatives are called {BLANK_MARKER} exclusives.",
            "mutually"),
            (
            f"The alternative that requires the minimum investment of capital and produces satisfactory functional results is considered the {BLANK_MARKER} alternative.",
            "base"),
            (
            f"The cost of capital invested in a project, also used to convert cash flows to equivalent worth, is the {BLANK_MARKER}.",
            "Minimum Attractive Rate of Return "),
            (
            f"{BLANK_MARKER} alternatives are those with initial capital investments that produce positive cash flows from increased revenue or reduced costs.",
            "Investment"),
            (
            f"The selected time period where mutually exclusive alternatives are compared is the {BLANK_MARKER} period, also called the planning horizon.",
            "study"),
            (
            f"The {BLANK_MARKER} assumption involves using a study period equal to a common multiple of the lives of the alternatives.",
            "repeatability"),
            (
            f"The {BLANK_MARKER} assumption uses a finite and identical study period for all alternatives, often requiring cash flow adjustments.",
            "coterminated"),
            (
            f"The {BLANK_MARKER} Worth method involves getting the PW of all revenues and expenses over an infinite length of time.",
            "Capitalized"),
            (
            f"When comparing investment alternatives using PW, the one with the {BLANK_MARKER} positive equivalent worth is selected.",
            "greatest"),
            (
            f"For mutually exclusive project combinations, a {BLANK_MARKER} variable can represent acceptance (1) or rejection (0).",
            "binary"),
        ],
        "EE_Handout_7": [
            ("Which assembly mate (assembly relationship) locks two parts together with no relative movement allowed?",
             ["Revolute mate", "Slider mate", "Fastened mate", "Ball mate"], "Fastened mate"),
            ("Which depreciation method assumes that a constant amount is depreciated each year over the asset's life?",
             ["Sum-of-the-Years-Digit (SYD)", "Declining Balance (DB)", "Straight Line Method (SLM)",
              "Units of Production"], "Straight Line Method (SLM)"),
            ("Which type of computer memory is volatile and needs constant power to retain data?",
             ["ROM", "Flash Memory", "RAM", "EPROM"], "RAM"),
            (
            "Which research design is characterized by manipulating one or more independent variables and controlling extraneous variables to determine cause-and-effect?",
            ["Correlational Research", "Causal Research", "Experimental Research", "Developmental Research"],
            "Experimental Research"),
            (
            "Which network protocol's primary function is to turn an unreliable network into a reliable one, handling error recovery and flow control?",
            ["IP", "UDP", "ICMP", "TCP"], "TCP"),
            ("Which basic logic gate produces a HIGH output only when all of its inputs are HIGH?",
             ["OR Gate", "AND Gate", "NOT Gate", "NAND Gate"], "AND Gate"),
            (
            "Which operational amplifier circuit configuration provides a gain of unity (1) with no polarity reversal?",
            ["Inverting Amplifier", "Noninverting Amplifier", "Summing Amplifier", "Unity Follower"], "Unity Follower"),
            (
            "In control systems, what graphical representation uses nodes for variables and directed branches for system gains?",
            ["Block Diagram", "Bode Plot", "Signal Flow Graph (SFG)", "Root Locus"], "Signal Flow Graph (SFG)"),
            (
            "What type of analysis simulates the behavior of a physical structure when forces are applied, often used to predict stress and deformation?",
            ["Modal Analysis", "Tolerance Analysis", "Finite Element Analysis (FEA)", "Circuit Analysis"],
            "Finite Element Analysis (FEA)"),
            (
            "What concept accounts for the interest an investment earns, indicating that money has different values at different points in time?",
            ["Depreciation", "Inflation", "Time Value of Money", "Sunk Cost"], "Time Value of Money"),
        ],
        "EE_Handout_8": [
            ("What is the primary purpose of public sector projects?",
             ["To generate profit for the government", "To provide services to citizens for the public good",
              "To compete with private corporations", "To fund political campaigns"],
             "To provide services to citizens for the public good"),
            ("How is the capital used to finance public sector projects commonly acquired?",
             ["Primarily from private investors", "Exclusively from international loans", "From taxes, bonds, and fees",
              "Through stock market offerings"], "From taxes, bonds, and fees"),
            (
            "Compared to private projects, the interest rate (discount rate) used for public sector projects is typically:",
            ["Higher", "Lower", "The same", "Variable based on profit"], "Lower"),
            ("Which method is primarily used to evaluate projects and select from alternatives in the public sector?",
             ["Internal Rate of Return (IRR)", "Payback Period", "Benefit/Cost (B/C) ratio method",
              "Net Present Worth (NPW)"], "Benefit/Cost (B/C) ratio method"),
            ("For a public project to be considered economically acceptable using the B/C ratio, the ratio must be:",
             ["Greater than 2.0", "Exactly equal to 1.0", "Less than 1.0", "Greater than or equal to 1.0"],
             "Greater than or equal to 1.0"),
            ("In B/C analysis for public projects, who is considered the 'owner'?",
             ["The government agency", "The contractors", "The elected officials", "The public people themselves"],
             "The public people themselves"),
            ("What term is used to describe the negative consequences of a public project to the public?",
             ["Costs", "Externalities", "Disbenefits", "Losses"], "Disbenefits"),
            ("In the conventional B/C ratio calculation, how are disbenefits typically handled?",
             ["Added to the costs in the denominator", "Subtracted from the benefits in the numerator",
              "Ignored completely", "Multiplied by the benefits"], "Subtracted from the benefits in the numerator"),
            ("The B/C ratio compares the equivalent worth of benefits to the equivalent worth of:",
             ["Initial investment only", "Annual revenues", "Costs", "Disbenefits"], "Costs"),
            ("Which equivalent worth measure (PW, AW, or FW) can be used as the basis for calculating the B/C ratio?",
             ["Only Present Worth (PW)", "Only Annual Worth (AW)", "Only Future Worth (FW)", "Any of PW, AW, or FW"],
             "Any of PW, AW, or FW"),
        ],
        # --- Logic Circuits and Design ---
        "LCD_Handout_1": [
            ("What is a system that uses distinct symbols to represent a number called?", "Number system"),
            ("What term defines the number of different symbols (digits) used in a number system?", "Base"),
            ("What is the base of the Binary number system?", "TWO"),
            ("Which number system is the basic foundation of any computer machine?", "Binary Number System"),
            ("What is the base of the number system we commonly use, derived from counting on fingers?", "TEN"),
            ("Which number system uses base 8 and symbols 0 through 7?", "Octal Number System"),
            ("In the Hexadecimal system (base 16), what decimal value does the letter 'F' represent?", "fifthteen"),
            ("What method involves repeatedly dividing by the target base to convert from decimal?",
             "Successive/Repeated by Base (n) Method"),
            ("What method uses the position of digits and the base value to convert to decimal?",
             "Positional Value Method"),
            ("When converting from Binary to Octal, how many binary digits are typically grouped together?", "Three"),
        ],
        "LCD_Handout_2": [
            (
            "What is an arrangement of electronically-controlled switches that makes logical decisions?", "Logic gate"),
            ("What is a set of electronic circuits on one small plate of semiconductor material called?",  "Integrated circuit (IC)"),
            ("Which type of IC has an output voltage that is either LOW or HIGH?", "Digital IC"),
            ("What method uses a table to define a gate's function by listing all input/output combinations?",  "Truth Tables"),
            ("Which basic logic gate performs inversion or complementation?", "NOT Gate"),
            ("Which basic logic gate performs logical multiplication?", "AND Gate"),
            ("Which basic logic gate performs logical addition?", "OR Gate"),
            ("What term, related to buffers, specifies the number of standard loads an output can drive?", "Fan-out"),
            (  "What form of algebra, used in digital systems, allows variables to have only two possible values (0 or 1)?", "Boolean Algebra"),
            ("Which theorem states that the complement of a sum/product is the product/sum of the complements?",  "DeMorgan's Theorem"),
        ],
        "LCD_Handout_3": [
            ("What is the primary use of Karnaugh maps mentioned in the rules?", "Simplification of expressions"),
            ("Who was the telecommunications engineer credited with modifying the K-map?", "Maurice Karnaugh"),
            ("In a K-map, what are the cell coordinates?", "The input variables"),
            ("How many variables change when moving between adjacent cells horizontally or vertically?", "One variable"),
            ("What value should groups NOT include when simplifying?", "Cells with different values"),
            ("What does a larger group of 1s or 0s represent in the simplified term?", "A simpler term"),
            ("For a 3-variable map, how many cells does it contain?", "Eight"),
            ("In a 4-variable map, how many literals does a single square represent?", " Four"),
            ("In a 4-variable map, how many literals does a group of eight squares represent?", "One"),
            ("What can using 'don't care' conditions often guarantee in K-map simplification?",  "Further simplification"),
        ],
        "LCD_Handout_4": [
            ("How can a NAND gate be configured to function as a NOT gate?", "Connect inputs together"),
            ("According to the diagram, how is an AND gate implemented using only NAND gates?",
             "Use two connected NANDs"),
            ("According to the diagram, how is an OR gate implemented using only NAND gates?",
             "Use three connected NANDs"),
            ("If all inputs of a NAND gate are connected, what function does it perform?", "NOT Gate"),
            ("How can a NOR gate be configured to function as a NOT gate?", "Connect inputs together"),
            ("According to the diagram, how is an AND gate implemented using only NOR gates?",
             "Use three connected NORs"),
            ("According to the diagram, how is an OR gate implemented using only NOR gates?", "Use two connected NORs"),
            ("If all inputs of a NOR gate are connected, what function does it perform?", "NOT Gate"),
            ("What type of gate implementation uses exclusively NAND gates?", "NAND Implementation"),
            ("What type of gate implementation uses exclusively NOR gates?", "NOR Implementation"),
        ],
        "LCD_Handout_5": [
            (
            f"A {BLANK_MARKER} is a combinational circuit that modifies data presented in one type of binary code to another type of binary code.",
            "code converter"),
            (
            f"{BLANK_MARKER} codes follow the positional weighting principles; each position of the number represents a specific weight.",
            "Weighted"),
            (f"The {BLANK_MARKER} Code represents each decimal digit using a 4-bit code with weights 8, 4, 2, and 1.",
             "BCD"),
            (f"The {BLANK_MARKER} Code is a non-weighted code that uses a bias value of three.", "Excess-3"),
            (
            f"The {BLANK_MARKER} Code is a non-weighted code in which every transition from one value to the next value involves only one-bit change.",
            "Gray"),
            (
            f"{BLANK_MARKER} logic employs memory elements, making the output dependent on inputs and the present state of memory.",
            "Sequential"),
            (
            f"{BLANK_MARKER} sequential circuits achieve synchronization by using clock generators or simply, the clock.",
            "Synchronous"),
            (
            f"{BLANK_MARKER} are asynchronous building blocks of sequential circuits, meaning their outputs are constantly affected by inputs when enabled.",
            "Latches"),
            (
            f"{BLANK_MARKER} are building blocks of sequential circuits whose content changes only either at the rising or falling edge of the enable signal.",
            "Flip-Flops"),
            (f"The {BLANK_MARKER} latch is similar to an SR latch except when both inputs are 1, the output toggles.",
             "JK"),
        ],
        "LCD_Handout_6": [
            (
            "What type of circuit has multiple inputs and a single output, with selection inputs determining which input is connected to the output?",
            ["Demultiplexer", "Encoder", "Multiplexer", "Decoder"], "Multiplexer"),
            ("How many select lines are needed for a 4-to-1 multiplexer?", ["1", "2", "3", "4"], "2"),
            (
            "What type of circuit has a single input and multiple outputs, with selection inputs determining which output receives the input?",
            ["Multiplexer", "Demultiplexer", "Register", "Counter"], "Demultiplexer"),
            (
            "What is a sequential logic circuit capable of storage and transfer of data, often consisting of connected flip-flops?",
            ["Multiplexer", "Counter", "Shift Register", "Latch"], "Shift Register"),
            ("Which type of shift register accepts data serially and outputs it serially?",
             ["SIPO", "PISO", "SISO", "PIPO"], "SISO"),
            ("Which type of shift register accepts data serially and outputs it in parallel?",
             ["SIPO", "PISO", "SISO", "PIPO"], "SIPO"),
            (
            "Which type of counter connects the serial output of the last flip-flop back to the serial input of the first?",
            ["Johnson Counter", "Ring Counter", "Ripple Counter", "Synchronous Counter"], "Ring Counter"),
            ("What type of memory allows both read and write operations and requires power to maintain its data?",
             ["ROM", "EPROM", "RAM", "PROM"], "RAM"),
            ("Which type of RAM consists of latches and retains data as long as power is applied?",
             ["DRAM", "SDRAM", "SRAM", "RDRAM"], "SRAM"),
            ("Which type of ROM can be erased using ultraviolet light?", ["PROM", "EEPROM", "Flash Memory", "EPROM"],
             "EPROM"),
        ],
        # --- Computer System Architecture ---
        "CSA_Handout_1": [
            ("What is a device that can compute desired information through entering information?", "Computer"),
            ("What element of a computer system is the fundamental representation of facts and observations?", "Data"),
            ("What element consists of programs that define instructions executed by hardware?", "Software"),
            ("What basic hardware component processes all data and instructions?", "Microprocessor"),
            ("Which type of storage is mostly temporary and volatile, like RAM?", "Primary Storage"),
            ("Which type of storage includes HDD, Flash Drive, and SSD?", "Secondary Storage"),
            ("What term describes the design of computer components, data flow, and algorithms?", "Architecture"),
            ("Which computer classification refers to small, low-cost systems for one user?", "Microcomputers"),
            ("What law states that integrated circuit resources double every 18-24 months?", "Moore's Law"),
            ("Which solution to architecture complexity involves splitting a system into smaller chunks?",
             "Decomposition"),
        ],
        "CSA_Handout_2": [
            ("What defines the structure or layout of a computer file?", "File Format"),
            ("What is the name given to a specific kind of file?", "File Type"),
            ("What is the 1- to 4-letter character identifier for a specific file type called?", "File Extension"),
            ("What provides additional information about an item's content, like keywords or tags?", "Metadata"),
            ("Which file attribute prevents a file from being changed or written to?", "Read-only"),
            ("Which character encoding standard was originally developed by ANSI?", "ASCII"),
            ("Which image category includes photographs and paintings captured by scanners or cameras?",
             "Bitmap objects"),
            ("Which image format is extensively used on the Web for animated frame-by-frame images?", "GIF"),
            ("What is the process of converting analog sound to digital form called?", "Sampling"),
            ("Which data compression algorithm allows exact restoration of the original data?", "Lossless algorithm"),
        ],
        "CSA_Handout_3": [
            ("What is the collection of physical parts of a computer system called?", "Computer hardware"),
            ("What technology defined the 1st Generation of computer hardware?", "Vacuum Tubes"),
            ("What invention characterized the 2nd Generation, replacing vacuum tubes?", "Transistors"),
            ("What term refers to a collection of transistors integrated into a single chip?", "Integrated Circuit"),
            ( "What component within a microprocessor processes data and instructions?", "Central Processing Unit (CPU)"),
            ("Which component performs arithmetic and logical operations like ADD or AND?", "ALU"),
            ("What is the pathway used for data or instructions between computer elements called?", "Bus"),
            ("Which CPU architecture uses separate buses for instructions and data?", "Harvard Architecture"),
            ("Which type of Instruction Set Architecture (ISA) uses simple instructions divisible into low-level operations?", "RISC"),
            ("What processing method executes instructions from the processor via a logical pipeline?", "Pipelining"),
        ],
        "CSA_Handout_4": [
            ("What computer component holds instructions (code) and data?", "Memory"),
            ("Which type of memory needs constant power to retain data?", "Volatile memory"),
            ("Which type of memory keeps its contents even without power?", "Nonvolatile memory"),
            ("What does RAM stand for?", "Random Access Memory"),
            ("Which type of RAM is almost 20 times faster and more expensive than DRAM?", "Static RAM "),
            ("What type of memory can only be read from and holds information permanently?", "Read-Only Memory"),
            ("Which type of ROM can be erased with ultraviolet light?", "Erasable PROM "),
            ("What term describes the delay in data transmission through microprocessor circuits?","Computer bottle necking"),
            ("What is the name for the level of memory hierarchy between the processor and main memory?", "Cache"),
            ("What is the tendency of a processor to access the same memory locations repetitively called?", "Locality of Reference"),
        ],
        "CSA_Handout_5": [
            (
            f"A {BLANK_MARKER} is a combinational circuit that modifies data presented in one type of binary code to another type of binary code.",
            "code converter"),
            (
            f"{BLANK_MARKER} codes follow the positional weighting principles; each position of the number represents a specific weight.",
            "Weighted"),
            (f"The {BLANK_MARKER} Code represents each decimal digit using a 4-bit code with weights 8, 4, 2, and 1.",
             "BCD"),
            (f"The {BLANK_MARKER} Code is a non-weighted code that uses a bias value of three.", "Excess-3"),
            (
            f"The {BLANK_MARKER} Code is a non-weighted code in which every transition from one value to the next value involves only one-bit change.",
            "Gray"),
            (
            f"{BLANK_MARKER} logic employs memory elements, making the output dependent on inputs and the present state of memory.",
            "Sequential"),
            (
            f"{BLANK_MARKER} sequential circuits achieve synchronization by using clock generators or simply, the clock.",
            "Synchronous"),
            (
            f"{BLANK_MARKER} are asynchronous building blocks of sequential circuits, meaning their outputs are constantly affected by inputs when enabled.",
            "Latches"),
            (
            f"{BLANK_MARKER} are building blocks of sequential circuits whose content changes only either at the rising or falling edge of the enable signal.",
            "Flip-Flops"),
            (f"The {BLANK_MARKER} latch is similar to an SR latch except when both inputs are 1, the output toggles.",
             "JK"),
        ],
        "CSA_Handout_6": [
            (
            f"Devices like monitors and printers, which allow information output from the computer, are called {BLANK_MARKER} peripherals.",
            "Output"),
            (
            f"The amount of data transferred to or from an I/O device in a period, typically measured in bits per second, is the {BLANK_MARKER}.",
            "Data rate"),
            (f"I/O {BLANK_MARKER} refers to the total elapsed time to accomplish an input or output operation.",
             "response time (latency)"),
            (
            f"In {BLANK_MARKER} I/O mode, instructions written in a computer program initiate each data item transfer.",
            "Programmed"),
            (
            f"In {BLANK_MARKER} I/O mode, the interface generates a signal to stop the CPU's current task and service the I/O transfer.",
            "Interrupt Initiated"),
            (f"An {BLANK_MARKER} requires CPU immediate attention for events like keyboard input or power failure.",
             "interrupt"),
            (
            f"A technique of removing the CPU from the path and letting the peripheral device manage memory buses directly is called {BLANK_MARKER} (DMA).",
            "Direct Memory Access"),
            (f"The {BLANK_MARKER} serves as an intermediary interface between the CPU and a specific device.",
             "I/O controller"),
            (
            f"The I/O controller function of {BLANK_MARKER} involves combining multiple signals over the bus to reduce multiple bus usage.",
            "Multiplexing"),
            (
            f"A {BLANK_MARKER} is a small piece of software that tells the operating system how to communicate with a piece of hardware.",
            "device driver"),
        ],
        "CSA_Handout_7": [
            (
            "Which type of storage access requires reading or skipping all previous items to get to a specific data item?",
            ["Random access", "Direct access", "Serial access", "Parallel access"], "Serial access"),
            ("Which level in the hierarchy of storage is NOT immediately available to the CPU and is treated as I/O?",
             ["Primary Storage", "Cache Memory", "Registers", "Secondary Storage"], "Secondary Storage"),
            (
            "On a magnetic disk, what is the circle traced out by the read/write head in a particular position called?",
            ["Sector", "Cylinder", "Platter", "Track"], "Track"),
            (
            "Which component of disk access time refers to the time it takes for the head to move to the proper track?",
            ["Rotational Delay", "Seek Time", "Transfer Time", "Latency"], "Seek Time"),
            ("Which storage technology is based on NAND Flash chips and includes SSDs and flash drives?",
             ["Magnetic Disk", "Optical Disk", "Magnetic Tape", "Solid State Memory"], "Solid State Memory"),
            ("Which disk controller interface standard replaced PATA and features thinner, more flexible cables?",
             ["SCSI", "SAS", "SATA", "IDE"], "SATA"),
            (
            "Which performance enhancement technique involves the controller reading subsequent blocks before they are requested, assuming sequential access?",
            ["Buffer Chaining", "Larger blocks", "Pre-fetch (read ahead)", "Disk array"], "Pre-fetch (read ahead)"),
            ("Which disk access algorithm handles requests based strictly on their arrival order?",
             ["STF (Shortest Time First)", "SCAN", "FCFS (First Come First Served)", "C-LOOK"],
             "FCFS (First Come First Served)"),
            (
            "Which type of disk array (RAID implementation) stores the exact same data on two or more disks for redundancy?",
            ["Striped array", "Mirrored array", "Parity array", "Spanned array"], "Mirrored array"),
            (
            "Which type of cloud storage connects storage resources directly to the network, typically for file-level access?",
            ["SAN (Storage Attached Network)", "Direct Attached Storage (DAS)", "Cloud Backup",
             "NAS (Network Attached Storage)"], "NAS (Network Attached Storage)"),
        ],
        "CSA_Handout_8": [
            ("What allows a single computer to appear as multiple computers, each with its own OS and resources?",
             ["Multithreading", "Virtualization", "Cloud Computing", "Grid Computing"], "Virtualization"),
            ("What term describes tasks literally running at the same time, often utilizing multiple processors?",
             ["Concurrency", "Synchronization", "Parallelism", "Abstraction"], "Parallelism"),
            ("What problem occurs when two or more threads access shared data and try to change it simultaneously?",
             ["Data Race", "Deadlock", "Race Condition", "Synchronization Failure"], "Race Condition"),
            (
            "According to Flynn's Taxonomy, which category describes a parallel computer with a single instruction stream and multiple data streams?",
            ["SISD", "SIMD", "MISD", "MIMD"], "SIMD"),
            (
            "According to Flynn's Taxonomy, which category represents most modern supercomputers, with multiple instruction and multiple data streams?",
            ["SISD", "SIMD", "MISD", "MIMD"], "MIMD"),
            (
            "Which type of hardware multithreading switches between threads only on expensive stalls, like cache misses?",
            ["Fine-grained multithreading", "Simultaneous multithreading (SMT)", "Coarse-grained multithreading",
             "Hyperthreading"], "Coarse-grained multithreading"),
            (
            "What type of processing architecture collects data elements into large registers and operates on them sequentially using pipelined units?",
            ["Scalar Architecture", "Vector Architecture", "MISD Architecture", "Superscalar Architecture"],
            "Vector Architecture"),
            (
            "What type of high-performance computing system consists of multiple, often inexpensive, computers connected by a dedicated private network?",
            ["Grid Computing System", "Cloud System", "Beowulf Cluster", "Mainframe"], "Beowulf Cluster"),
            (
            "Which cloud computing model provides software applications that run on a server and are accessed by clients over the internet?",
            ["Infrastructure as a Service (IaaS)", "Platform as a Service (PaaS)", "Software as a Service (SaaS)",
             "Network as a Service (NaaS)"], "Software as a Service (SaaS)"),
            ("What is the term for a processor optimized for 2D/3D graphics, video, and visual computing?",
             ["CPU", "ALU", "GPU", "FPU"], "GPU"),
        ],
        # --- Methods of Research ---
        "MR_Handout_1": [
            ("What is the term for a process of planning, acquiring, analyzing, and disseminating relevant data?",
             "Research"),
            ("Which discipline embodies the science and technology of designing computer hardware and software?", "Computer Engineering"),
            (  "Name one factor mentioned that stimulates interest in studying research methods.", "Information overload"),
            (  "What is the term for the combination of structured, semi-structured, and unstructured data collected by organizations?",  "Big data"),
            ("What is one of the two (2) main attribute categories for a good research topic?", "Capability"),
            ("According to the research process model, what triggers the need to conduct research?", "Management dilemma"),
            ("What is the system of moral principles that governs a person's behavior and decisions in research?", "Ethics"),
            ("What quality pertains to being honest and having strong moral principles in research?", "Integrity"),
            ("What ethical principle involves protecting sensitive data collected during research?",  "Protect the confidentiality"),
            ("What term means that research results will be of similar value whatever the findings?", "Symmetry of potential outcomes"),
        ],
        "MR_Handout_2": [
            ("What section of the introduction presents the 'big picture' and context of the problem?",
             "Background of the Study"),
            ("What does citing recognized authors in the background help to do?", "Support and strengthen statements"),
            ("What should a research study avoid trying to do?", "Prove a point"),
            ("What is a simple way to create a research question, according to the text?",
             "Turn the purpose statement into a question"),
            ("What forms the basis of the research question?", "Purpose statement"),
            ("What part of the introduction describes the importance or the 'so what?' of the study?",
             "Significance of the Study"),
            ("What term identifies potential weaknesses of the study outside the researcher's control?", "Limitations"),
            ("What term addresses how the researcher narrows the scope of the study?", "Delimitations"),
            ("What characteristic should a study reflect, even if results differ from expectations?", "Integrity"),
            ("What are the usually simple terms linked with a hypothesis or purpose statement called?",
             "Research Objectives"),

        ],
        "MR_Handout_3": [
            ("What type of writing combines both summary and synthesis of key sources?", "Literature review"),
            ("What is a recap of a source's important information called?", "Summary"),
            ("What is a re-organization or reshuffling of information from sources called?", "Synthesis"),
            ("What purpose of a literature review involves finding where gaps exist in prior research?",
             "Reveal any gaps"),
            ("Which type of literature review examines literature selectively to support or refute an argument?",
             "Argumentative Review"),
            ("Which type of literature review is considered the most common in social sciences?", "Integrative Review"),
            ("What should you do if your literature review assignment is not specific about its form?",
             "Seek clarification"),
            ("What must back up your interpretation of available sources in a literature review?", "Evidence"),
            ("What should you avoid doing excessively as a substitute for your own summary and interpretation?",
             "Use extensive quotes"),
            ("What important practice allows readers to locate materials you used and increases your credibility?",
             "Proper citation"),
        ],
        "MR_Handout_4": [
            ("What are formulated to explain, predict, and understand phenomena?", "Theories"),
            ("What structure can hold or support a theory of a research study?", "Theoretical framework"),
            ("What anchors the entire study and forms the basis for the theoretical framework?", "Research problem"),
            ("What type of variable is changed or controlled in a study?", "Independent variable"),
            ("What type of variable is tested and measured in a study?", "Dependent variable"),
            (
            "What does a theoretical framework limit by focusing on specific variables?", "Scope of the relevant data"),
            ("What is the primary purpose of a theory mentioned in the text?",
             "To explain meaning, nature, and challenges"),
            (
            "What structure does the researcher believe best explains the natural progression of the phenomenon studied?",
            "Conceptual framework"),
            ("What does the conceptual framework present an integrated way of looking at?", "A problem under study"),
            ("From a statistical perspective, what does the conceptual framework describe?",
             "Relationship between main concepts"),
        ],
        "MR_Handout_5": [
            (f"In a {BLANK_MARKER} relationship, one variable directly or indirectly influences another.", "causal"),
            (
            f"In causal research, the subjects are selected systematically, which is helpful for higher levels of internal {BLANK_MARKER}.",
            "validity"),
            (f"In {BLANK_MARKER} research, the main interest is to determine whether two or more variables covary.",
             "correlational"),
            (
            f"In correlational research for prediction, the variable used to predict is called the {BLANK_MARKER} variable.",
            "predictor"),
            (
            f"In correlational research for prediction, the variable whose value is being predicted is called the {BLANK_MARKER} variable.",
            "criterion"),
            (
            f"{BLANK_MARKER} research has two defining characteristics: manipulation of independent variables and control over extraneous variables.",
            "Experimental"),
            (
            f"In experimental research, the variable whose values are chosen and set by the experimenter is the {BLANK_MARKER} variable.",
            "independent"),
            (
            f"In experimental research, the variable whose value is observed and measured is the {BLANK_MARKER} variable.",
            "dependent"),
            (
            f"{BLANK_MARKER} research is conducted systematically to assess changes in a system or environment over a period of time.",
            "Developmental"),
            (
            f"A {BLANK_MARKER} study is a developmental research method performed by observing a specific group for months or years.",
            "Longitudinal"),
        ],
        "MR_Handout_6": [
            (
            f"{BLANK_MARKER} is widely used in research as a means of gathering useful information about a population.",
            "Sampling"),
            (f"Investigating all population members under study is called conducting a {BLANK_MARKER}.", "census"),
            (
            f"In {BLANK_MARKER} random sampling, the entire sample is based on a draw where each unit has an equal probability of being selected.",
            "simple"),
            (f"In {BLANK_MARKER} random sampling, elements are divided into homogeneous groups called strata.",
             "Stratified"),
            (
            f"In {BLANK_MARKER} sampling, the population is divided into non-overlapping areas or clusters which are internally heterogeneous.",
            "Cluster"),
            (
            f"In {BLANK_MARKER} sampling, elements are selected for the convenience of the researcher.", "Convenience"),
            (f"In {BLANK_MARKER} sampling, survey subjects are selected based on referrals from other respondents.",
             "Snowball"),
            (
            f"The {BLANK_MARKER} theorem states that as sample size increases, the shape of the sampling distribution of means approximates a normal distribution.",
            "Central Limit"),
            (
            f"The standard deviation of the sampling distribution of means is called the standard {BLANK_MARKER} of the mean.",
            "error"),
            (
            f"According to the Central Limit Theorem, the mean of the sampling distribution of means will equal the population {BLANK_MARKER}.",
            "mean"),
        ],
        "MR_Handout_7": [
            (
            "What consists of a formalized and pre-specified set of questions designed to obtain responses from potential respondents?",
            ["Interview Guide", "Survey Form", "Questionnaire", "Observation Checklist"], "Questionnaire"),
            (
            "Which principle of wording involves using language appropriate to the respondents' educational level and culture?",
            ["Appropriateness of content", "How questions are worded", "Type and form of questions",
             "Sequencing of questions"], "How questions are worded"),
            ("Which type of question allows respondents to answer in any way they choose?",
             ["Closed question", "Multiple choice question", "Rating scale question", "Open-ended question"],
             "Open-ended question"),
            (
            "What type of question asks respondents to make choices among a set of alternatives provided by the researcher?",
            ["Open-ended question", "Closed question", "Leading question", "Loaded question"], "Closed question"),
            (
            "What type of question should be avoided because it lends itself to different possible responses to its subparts?",
            ["Ambiguous question", "Double-barreled question", "Leading question", "Recall-dependent question"],
            "Double-barreled question"),
            (
            "Which type of question might pressure respondents to give responses the researcher would like them to give?",
            ["Loaded question", "Ambiguous question", "Leading question", "Social desirability question"],
            "Leading question"),
            ("Which type of question is phrased in an emotionally charged manner?",
             ["Leading question", "Ambiguous question", "Double-barreled question", "Loaded question"],
             "Loaded question"),
            ("What approach to sequencing questions involves moving from general to specific questions?",
             ["Random approach", "Funnel approach", "Reverse approach", "Topical approach"], "Funnel approach"),
            ("What type of data includes personal information such as age, educational level, and marital status?",
             ["Measurement data", "Scaling data", "Classification data", "Response data"], "Classification data"),
            ("Where in the questionnaire is it generally best to ask for sensitive personal information like income?",
             ["At the beginning", "In the middle, randomly", "At the end", "In a separate section"], "At the end"),
        ],
        "MR_Handout_8": [
            ("Which measure of central tendency represents the most frequently occurring value in a dataset?",
             ["Mean", "Median", "Mode", "Range"], "Mode"),
            ("What is the middle value in an ordered array of numbers called?",
             ["Mean", "Mode", "Median", "Standard Deviation"], "Median"),
            (
            "Which measure of central tendency is computed by summing all numbers and dividing by the count of numbers?",
            ["Median", "Mode", "Range", "Mean"], "Mean"),
            (
            "What measures of location divide a set of data so that a certain fraction falls on or below that location?",
            ["Quartiles", "Percentiles", "Deciles", "Ranges"], "Percentiles"),
            ("Which quartile is equal to the 50th percentile and the median of the data?", ["Q1", "Q2", "Q3", "Q4"],
             "Q2"),
            (
            "What is the simplest measure of variability, calculated as the difference between the maximum and minimum values?",
            ["Variance", "Standard Deviation", "Range", "Interquartile Range"], "Range"),
            ("Which measure of variability represents the distance between the first and third quartiles (Q3 - Q1)?",
             ["Range", "Standard Deviation", "Variance", "Interquartile Range"], "Interquartile Range"),
            ("What is the average of the squared deviations from the mean for a set of numbers called?",
             ["Standard Deviation", "Variance", "Range", "Mode"], "Variance"),
            ("Which widely used measure of variability is calculated as the square root of the variance?",
             ["Range", "Interquartile Range", "Median", "Standard Deviation"], "Standard Deviation"),
            ("For which type of data is the mode an appropriate descriptive summary measure?",
             ["Continuous Data", "Interval Data", "Ratio Data", "Categorical Data"], "Categorical Data"),
        ],
        # --- Data and Digital Communication ---
        "DDC_Handout_1": [
            ("Which ancient long-distance communication method used smoke as a distress signal?", "Smoke Signals"),
            ("What technology revolutionized long-distance communication by sending electric signals over wires?",
             "Electrical Telegraph"),
            ("Which generation of mobile communication introduced SMS and GPRS?", "2nd Generation (2G)"),
            ("Which generation introduced key technologies like MIMO and OFDM?", "4th Generation (4G)"),
            ("What type of data refers to continuous information, like a human voice?", "Analog data"),
            ("What type of data takes on discrete values, like ones and zeros?", "Digital data"),
            ("In Shannon's model, what component converts information into an electrical message signal?",
             "Source encoder"),
            ("In Shannon's model, what is the path or link connecting the transmitter and receiver called?", "Channel"),
            ("Which network topology connects nodes serially in a loop?", "Ring topology"),
            (
            "Which network geographical coverage interconnects devices within an individual's reach, typically 10 meters?",
            "Personal area networks "),
        ],
        "DDC_Handout_2": [
            ("What type of signal includes speech, audio, and video and has infinite values?", "Analog signals"),
            ("What type of signal is predominantly binary (0s and 1s)?", "Digital signals"),
            ("What type of signal completes a pattern within a period and repeats that pattern?", "Periodic signal"),
            (
            "What signal terminology refers to the number of waves passing a point per time period (Hz)?", "Frequency"),
            ("What device modulates data into a signal and demodulates it back?", "Modem"),
            ("Which modulation technique varies the carrier amplitude based on the information signal?",
             "Amplitude modulation (AM)"),
            ("Which step in Analog-to-Digital Conversion approximates pulse amplitude to the nearest integer?",
             "Quantization"),
            ("Which step in Analog-to-Digital Conversion converts discrete signals into binary (1s and 0s)?",
             "Encoding)"),
            ("What channel impairment causes a decrease in signal strength as it travels?", "Attenuation"),
            ("What term describes unwanted signals superimposed on a desired signal?", "Noise"),
        ],
        "DDC_Handout_3": [
            ("Which dataflow transmission mode allows data to flow only in one direction?", "Simplex transmission"),
            ("Which dataflow transmission mode allows data flow in both directions, but not simultaneously?",
             "Half-duplex transmission (HDX)"),
            ("Which type of data transmission sends bits one after another in order?", "Serial data transmission"),
            ("What type of transmission media uses physical connections like wires or fiber optics?", "Guided media"),
            ("Name one example of guided transmission media mentioned.", "Twisted Pair"),
            ("What is the metal rod or dish that catches radio waves and turns them into electrical signals?",
             "Antenna"),
            ("What term describes the range of frequencies contained by a signal?", "Frequency Spectrum"),
            ("Which wave propagation method utilizes the ionosphere?", "Sky Wave"),
            ("What technique sends multiple signals over a single communication link simultaneously?",
             "Multiplexing (MUX)"),
            (
            "Which media access method prevents collisions by allowing only the computer holding a 'token' to transmit?",
            "Token passing"),
        ],
        "DDC_Handout_4": [
            ("What is an architecture used to interconnect two devices together?", "Hardware interface"),
            ("What characteristic deals with voltages and electrical issues in an interface standard?",
             "Electrical component"),
            ("Which digital interface is known for being hot-pluggable?", "Universal Serial Bus (USB)"),
            ("Which data link connection type transfers single characters or bytes with irregular timing?",
             "Asynchronous connection"),
            ("Which data link connection type transfers large sequences of characters with regular timing?",
             "Synchronous connection"),
            ("What term refers to the data-carrying capacity of a channel or medium?", "Bandwidth"),
            ("What term refers to the loss of signal energy as it propagates outwards?", "Attenuation"),
            ("What is the measure of how fast data can actually be sent through a network?", "Throughput"),
            ("What term measures the time it takes for data to get to its destination?", "Latency"),
            ("Which data transfer technique involves establishing a dedicated path before communication starts?",
             "Circuit switching"),
        ],
        "DDC_Handout_5": [
            (
            f"{BLANK_MARKER} are sets of established rules that dictate how to format, transmit, and receive data so computer network devices can communicate.",
            "Network protocols"),
            (f"The {BLANK_MARKER} (IP) provides a connectionless data transfer service over heterogeneous networks.",
             "Internet Protocol"),
            (f"IPv4 addresses are 32 bits long, while {BLANK_MARKER} addresses are 128 bits long.", "IPv6"),
            (f"The {BLANK_MARKER} (TCP) primary function is to turn an unreliable network into a reliable network.",
             "Transmission Control Protocol"),
            (f"The {BLANK_MARKER} (ICMP) performs error reporting for the Internet Protocol.",
             "Internet Control Message Protocol"),
            (f"The {BLANK_MARKER} (DHCP) is the most popular protocol that handles dynamic assignment of IP addresses.",
             "Dynamic Host Configuration Protocol"),
            (f"A {BLANK_MARKER} (VPN) uses tunneling protocols to maintain privacy over public infrastructure.",
             "Virtual Private Network"),
            (f"A {BLANK_MARKER} network consists of a series of interlinked nodes, called switches.", "switched"),
            (f"In {BLANK_MARKER}, messages are divided into packets of fixed or variable size before transmission.",
             "Packet Switching"),
            (f"In {BLANK_MARKER} networks, each packet is treated independently of all others.", "Datagram"),
        ],
        "DDC_Handout_6": [
            (f"{BLANK_MARKER} noise is always present in transmission media and increases with temperature.", "White"),
            (
            f"{BLANK_MARKER} noise is a noncontinuous, random burst of energy that is difficult to detect.", "Impulse"),
            (
            f"A {BLANK_MARKER} error indicates that only one bit of a given data unit is changed from 1 to 0 or vice versa.",
            "single-bit"),
            (f"A {BLANK_MARKER} error indicates that two or more bits in the data unit have changed.", "burst"),
            (f"The central concept in detecting or correcting errors by sending extra bits is {BLANK_MARKER}.",
             "Redundancy"),
            (f"The {BLANK_MARKER} Check adds a redundant bit to each character to create either even or odd parity.",
             "Parity"),
            (
            f"The {BLANK_MARKER} Check organizes data blocks as a two-dimensional array and appends parity bits to rows and columns.",
            "Two-Dimensional Parity"),
            (f"An Arithmetic {BLANK_MARKER} uses the sum of characters to be transmitted for error detection.",
             "Checksum"),
            (
            f"The {BLANK_MARKER} Checksum treats the data packet as a large polynomial and uses the remainder of binary division for error checking.",
            "Cyclic Redundancy"),
            (
            f"The {BLANK_MARKER} ARQ error control scheme involves the source sending a frame and waiting for an ACK or NAK before sending the next.",
            "Stop-and-Wait"),
        ],
        "DDC_Handout_7": [
            ("Which security goal ensures that data is kept private and accessed only by the intended recipient?",
             ["Integrity", "Availability", "Authentication", "Confidentiality"], "Confidentiality"),
            ("Which security goal ensures that data is transmitted from source to destination without alteration?",
             ["Confidentiality", "Integrity", "Availability", "Authentication"], "Integrity"),
            ("Which security goal ensures that information created and stored is accessible to authorized entities?",
             ["Confidentiality", "Integrity", "Availability", "Authentication"], "Availability"),
            ("Which type of attack involves unauthorized access to or interception of data?",
             ["Modification", "Snooping", "Masquerading", "Replaying"], "Snooping"),
            ("Which type of attack involves the attacker impersonating somebody else?",
             ["Snooping", "Modification", "Masquerading", "Repudiation"], "Masquerading"),
            (
            "Which attack involves preventing authorized users from accessing services, often by flooding the network?",
            ["Spoofing", "Man-in-the-middle", "Denial of Service (DoS)", "Phishing"], "Denial of Service (DoS)"),
            ("What is the process of concealing information from readable text into an unintelligible form called?",
             ["Decryption", "Authentication", "Encryption", "Hashing"], "Encryption"),
            ("In cryptography, what is the readable text called before it is encrypted?",
             ["Ciphertext", "Plaintext", "Keytext", "Cryptotext"], "Plaintext"),
            ("Which type of cryptosystem uses the same key for both encryption and decryption?",
             ["Asymmetric Cryptosystem", "Public-Key Cryptosystem", "Symmetric Cryptosystem", "Hybrid Cryptosystem"],
             "Symmetric Cryptosystem"),
            (
            "Which type of cryptosystem uses one key for encryption (public key) and a different key for decryption (private key)?",
            ["Symmetric Cryptosystem", "Shared-Key Cryptosystem", "Secret-Key Cryptosystem", "Public-Key Cryptosystem"],
            "Public-Key Cryptosystem"),
        ],
        # --- Fundamentals of Mixed Signals and Sensors ---
        "FMSS_Handout_1": [
            ("What type of amplifier has a very large gain when opposite signals are applied to its inputs?",
             "Differential Amplifier"),
            ("In a differential amplifier, what operation involves applying a signal to only one input?",
             "Single-ended operation"),
            (
            "What is a very high gain differential amplifier with high input impedance and low output impedance called?",
            "Operational Amplifier / Op-Amp"),
            ("Which op-amp input terminal is labeled with a '-' sign?", "Inverting input"),
            ("What property describes the gain of an op-amp without feedback?", "Infinite open-loop gain"),
            ("What is it called when you connect the output of a circuit back to its input?", "Feedback"),
            ("What happens when an op-amp's output voltage tries to exceed its power supply range?",
             "It saturates / Output Saturation"),
            ("In op-amp operation, what term describes applying signals to both inputs?",
             "Double-Ended (Differential) Input"),
            ("What feature describes an op-amp's ability to attenuate unwanted noise common to both inputs?",
             "Common-mode rejection"),
            ("Ideally, what is the output voltage of an op-amp in common-mode operation?", "0v / Zero"),
        ],
        "FMSS_Handout_2": [
            ("What type of amplifier has a very large gain when opposite signals are applied to its inputs?",
             "Differential Amplifier"),
            ("In a differential amplifier, what operation involves applying a signal to only one input?",
             "Single-ended operation"),
            (
            "What is a very high gain differential amplifier with high input impedance and low output impedance called?",
            "Operational Amplifier"),
            ("Which op-amp input terminal is labeled with a '-' sign?", "Inverting input"),
            ("What property describes the gain of an op-amp without feedback?", "Infinite open-loop gain"),
            ("What is it called when you connect the output of a circuit back to its input?", "Feedback"),
            ("What happens when an op-amp's output voltage tries to exceed its power supply range?",
             "Output Saturation"),
            ("In op-amp operation, what term describes applying signals to both inputs?",
             "Double-Ended (Differential) Input"),
            ("What feature describes an op-amp's ability to attenuate unwanted noise common to both inputs?",
             "Common-mode rejection"),
            ("Ideally, what is the output voltage of an op-amp in common-mode operation?", "0v"),
        ],
        "FMSS_Handout_3": [
            ("What is the ratio of common-mode gain to differential-mode gain in an op-amp called?",
             "Common-Mode Rejection Ratio "),
            ("What is the formula for differential voltage (Vd) in an op-amp?", "Vd = V+ - V-"),
            ("Which widely used op-amp circuit multiplies the input by a fixed gain and inverts the output?",
             "Inverting Amplifier"),
            ("In an inverting amplifier, what sets the fixed or constant gain?",
             "Input resistor (R1) and feedback resistor "),
            ("Which op-amp circuit acts as a constant-gain multiplier without inverting the input?",
             "Noninverting Amplifier"),
            ("What op-amp circuit provides a gain of unity (1) with no polarity reversal?", "Unity Follower"),
            ("Which op-amp circuit algebraically adds multiple input voltages, each multiplied by a gain factor?",
             "Summing Amplifier"),
            ("What op-amp circuit configuration results when a capacitor is used as the feedback component?",
             "Integrator"),
            ("What mathematical operation does the Integrator circuit perform on the input voltage over time?",
             "Integration"),
            ("What op-amp circuit provides an output proportional to the rate of change of the input voltage?",
             "Differentiator"),
        ],
        "FMSS_Handout_4": [
            (
            "What type of signal has a linear relationship between the electrical quantity and the value it represents?",
            "Analog signal"),
            ("What type of signal is expressed as discrete numbers (samples) associated with discrete times?",
             "Digital signals"),
            ("Which type of converter accepts a digital number and produces an analog signal?",
             "Digital-to-Analog converter"),
            ("Which type of converter accepts an analog signal and produces a digital number?",
             "Analog-to-Digital converter "),
            ("Which shift keying method modifies the amplitude of the carrier signal?", "Amplitude Shift Keying"),
            ("Which shift keying method modifies the frequency of the carrier signal?", "Frequency Shift Keying"),
            ("Which DAC approach uses a resistor string and a set of switches?", "Kelvin Divider"),
            ("Which ADC method uses sampling, quantizing, and encoding?", "Pulse Code Modulation "),
            ("What is the first technique used in PCM to collect sample data from a message signal?", "Sampling"),
            ("Which ADC approach uses a series of comparators connected to a priority encoder?", "Flash ADC"),
        ],
        "FMSS_Handout_5": [
            (f"A {BLANK_MARKER} senses the quantity that needs to be observed or measured.", "sensor"),
            (f"The variable that is measured is termed the {BLANK_MARKER}.", "measurand"),
            (
            f"The {BLANK_MARKER} defines the maximum and minimum values of the quantity that the sensor is designed to measure.",
            "Range/Span"),
            (f"{BLANK_MARKER} describes the maximum expected error associated with a measurement.", "Accuracy"),
            (
            f"{BLANK_MARKER} is the deviation of the sensor's output at any given point when approached from two different directions.",
            "Hysteresis"),
            (
            f"{BLANK_MARKER} change their resistance with temperature and use materials with high thermal coefficients.",
            "Thermistors"),
            (f"A {BLANK_MARKER} gauge measures force by observing the deformation produced (strain).", "Strain"),
            (
            f"{BLANK_MARKER} are transducers that convert one physical quantity into another, often to affect the outside world.",
            "Actuators"),
            (
            f"A {BLANK_MARKER} consists of an electric coil and a ferromagnetic slug that can move into or out of the coil.",
            "Solenoid"),
            (
            f"{BLANK_MARKER} motors move in discrete steps, and their speed of rotation is directly controlled by the input waveform.",
            "Stepper"),
        ],
        "FMSS_Handout_6": [
            ("What term refers to the variable that is measured by a sensor?",
             ["Measurement", "Span", "Transducer", "Measurand"], "Measurand"),
            (
            "Which specification defines the maximum and minimum values of the quantity that a sensor is designed to measure?",
            ["Accuracy", "Precision", "Resolution", "Range/Span"], "Range/Span"),
            ("What sensor specification describes the maximum expected error associated with a measurement?",
             ["Precision", "Accuracy", "Resolution", "Sensitivity"], "Accuracy"),
            (
            "What term describes the deviation of a sensor's output at a given point when approached from two different directions?",
            ["Linearity", "Deadband", "Hysteresis", "Error"], "Hysteresis"),
            (
            "Which of the following is a type of temperature sensor that uses materials with high thermal coefficients of resistance?",
            ["Resistive thermometer", "pn junction", "Thermistor", "Photovoltaic cell"], "Thermistor"),
            ("Which sensor type generates an electrical output when subjected to mechanical stress?",
             ["Strain gauge", "Piezoelectric", "Inductive sensor", "Photoconductive sensor"], "Piezoelectric"),
            (
            "Which displacement sensor type works based on resistance changes and is commonly found as controls in electronic equipment?",
            ["Inductive sensor", "Opto-switch", "Potentiometer", "Absolute position encoder"], "Potentiometer"),
            (
            "What type of device converts one physical quantity into another, specifically to affect the outside world (e.g., move something, change temperature)?",
            ["Sensor", "Measurand", "Actuator", "Controller"], "Actuator"),
            (
            "Which actuator consists of an electric coil and a ferromagnetic slug that is attracted towards the center when current passes through?",
            ["DC Motor", "Stepper Motor", "Solenoid", "Speaker"], "Solenoid"),
            (
            "Which light actuator is a semiconductor diode constructed to produce light when current passes through it?",
            ["LCD", "LED", "Incandescent lamp", "Fluorescent lamp"], "Light-emitting diodes"),
        ],

    }

    # Data Validation
    all_handout_keys_in_paths = list(HANDOUT_PATHS.keys())
    for key in all_handout_keys_in_paths:
        if key not in data:
            print(f"Warning: Game data missing for key '{key}'. Adding empty list.")
            data[key] = []

    return data


# --- Pygame Helper Function (Text Rendering) ---
def _render_text_generic(target_surface, text, font, color, center_pos=None, top_left_pos=None, wrap_width=None, antialias=True):
    """Renders text, handling wrapping and positioning. Returns bounding Rect."""
    if not text or not font: return None

    lines_surfaces = []
    max_line_width = 0
    total_height = 0

    try:
        line_height = font.get_height()
        direct_lines = str(text).split('\n')
        processed_lines = []
        for direct_line in direct_lines:
            if wrap_width and wrap_width > 0:
                words = direct_line.split(' ')
                current_line = ""
                for word in words:
                    if not word: continue
                    test_line = current_line + word + " "
                    test_surface = font.render(test_line, antialias, color)
                    test_width = test_surface.get_width()
                    if test_width <= wrap_width or not current_line:
                        current_line = test_line
                    else:
                        processed_lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    processed_lines.append(current_line.strip())
            else:
                processed_lines.append(direct_line)

        for line_text in processed_lines:
            line_surface = font.render(line_text, antialias, color)
            lines_surfaces.append(line_surface)
            max_line_width = max(max_line_width, line_surface.get_width())
            total_height += line_surface.get_height()

    except Exception as e:
        print(f"Error rendering text ('{str(text)[:50]}...'): {e}")
        traceback.print_exc()
        try:
            err_surf = pygame.font.Font(None, 20).render("[TextErr]", True, RED)
            pos = center_pos or top_left_pos or (10, 10)
            target_surface.blit(err_surf, pos)
        except: pass
        return None

    if not lines_surfaces: return None

    block_rect = None
    current_y_offset = 0
    start_y = 0
    if center_pos:
        start_y = center_pos[1] - total_height // 2
    elif top_left_pos:
        start_y = top_left_pos[1]

    for i, line_surface in enumerate(lines_surfaces):
        line_width = line_surface.get_width()
        line_height = line_surface.get_height()
        line_pos_x = 0
        if center_pos:
            line_pos_x = center_pos[0] - line_width // 2
        elif top_left_pos:
            line_pos_x = top_left_pos[0]

        line_rect = pygame.Rect(int(line_pos_x), int(start_y + current_y_offset), line_width, line_height)
        try:
            target_surface.blit(line_surface, line_rect.topleft)
        except Exception as blit_err:
            print(f"Error blitting text line: {blit_err}")
            traceback.print_exc()
            continue

        if i == 0:
            block_rect = line_rect.copy()
        elif block_rect:
            block_rect.union_ip(line_rect)

        current_y_offset += line_height

    return block_rect


# --- PygameHangman Class ---
class PygameHangman:
    """Manages the Hangman game (Prelim Period)."""
    def __init__(self, handout_key):
        self.handout_key = handout_key
        self.all_game_data = load_game_data_by_handout()
        self.game_name = "Hangman Challenge"
        self.is_fullscreen = False # Start in fullscreen mode

        # Load items first
        self.items_for_session = []
        self.total_items_in_session = 0
        self._load_session_items()

        # Initialize state variables AFTER loading items
        self._initialize_state()

        # Pygame Init
        try:
            if not pygame.get_init(): pygame.init()
            print("Pygame initialized for Hangman.")
        except Exception as e: messagebox.showerror("Pygame Error", f"Init Error: {e}"); print(f"Fatal Pygame Init Error: {e}"); traceback.print_exc(); sys.exit(1)

        # Load Fonts
        self._load_fonts()

        # Setup Screen
        self._setup_screen()

        # Load Hangman Images
        self.hangman_images = []
        self._load_images_safely()



        # Initialize keyboard
        self.keyboard_visible = False
        self._init_keyboard()

        # Start first round if items were loaded successfully
        if not self.items_for_session:
             print("Error: No valid Hangman items loaded. Cannot start first round.")
             # State already reflects this from _initialize_state
        else:
             self._next_round()

    def _init_keyboard(self):
        """Initialize the custom in-game keyboard"""
        self.keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]
        
        # Fixed keyboard position at bottom center
        keyboard_width = 600
        keyboard_height = 150
        self.keyboard_rect = pygame.Rect(
            SCREEN_WIDTH//2 - keyboard_width//2, 
            SCREEN_HEIGHT - keyboard_height - 20, 
            keyboard_width, 
            keyboard_height
        )
        
        self._update_keyboard_buttons()

    def _update_keyboard_buttons(self):
        """Update keyboard button positions"""
        self.keyboard_buttons = {}
        button_width = 50
        button_height = 40
        button_margin = 5
        
        for row_idx, row in enumerate(self.keyboard_rows):
            row_width = len(row) * (button_width + button_margin) - button_margin
            start_x = self.keyboard_rect.centerx - row_width // 2
            
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (button_width + button_margin)
                y = self.keyboard_rect.top + row_idx * (button_height + button_margin)
                rect = pygame.Rect(x, y, button_width, button_height)
                self.keyboard_buttons[key] = rect

    def toggle_keyboard(self):
        """Toggle the custom in-game keyboard visibility"""
        self.keyboard_visible = not self.keyboard_visible

    def _handle_keyboard_click(self, pos):
        """Handle clicks on the custom keyboard"""
        if not self.keyboard_visible:
            return False
            
        # Check for button clicks only
        for key, rect in self.keyboard_buttons.items():
            if rect.collidepoint(pos):
                self._process_guess(key.lower())
                return True
                
        return False

    def _draw_keyboard(self):
        """Draw the custom in-game keyboard"""
        if not self.keyboard_visible:
            return
            
        # Draw keyboard background
        pygame.draw.rect(self.screen, (200, 200, 200), self.keyboard_rect)
        pygame.draw.rect(self.screen, BLACK, self.keyboard_rect, 2)
        
        # Draw buttons
        for key, rect in self.keyboard_buttons.items():
            color = (150, 150, 150) if rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw key text
            key_surface = self.info_font.render(key, True, WHITE)
            key_rect = key_surface.get_rect(center=rect.center)
            self.screen.blit(key_surface, key_rect)

    def _draw_game_elements(self):
        """Draws the regular game elements (hint, word, hangman, etc.)."""
        # Calculate content offset based on keyboard visibility
        content_offset = 100 if self.keyboard_visible else 0
        
        # --- Top Bar Info ---
        display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
        _render_text_generic(self.screen, display_handout_name, self.title_font, BLACK, top_left_pos=(20, 15))
        
        # --- ESC Button (top-right corner) ---
        esc_button_width, esc_button_height = 80, 40
        esc_button_x = SCREEN_WIDTH - esc_button_width - 20
        esc_button_y = 15
        self.esc_button_rect = pygame.Rect(esc_button_x, esc_button_y, esc_button_width, esc_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        esc_color = (200, 100, 100) if self.esc_button_rect.collidepoint(mouse_pos) else (150, 70, 70)
        pygame.draw.rect(self.screen, esc_color, self.esc_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.esc_button_rect, 2, border_radius=8)
        _render_text_generic(self.screen, "", self.info_font, WHITE, center_pos=self.esc_button_rect.center)
        
        if self.total_items_in_session > 0:
            round_text = f"Round: {min(self.current_round_index + 1, self.total_items_in_session)} / {self.total_items_in_session}"
            _render_text_generic(self.screen, round_text, self.score_font, BLUE, top_left_pos=(SCREEN_WIDTH - 200, 15))

        # --- Main Game Area - Adjusted for keyboard ---
        # Hangman Image
        image_index = max(0, min(self.incorrect_guesses_total_for_drawing, MAX_MISTAKES_DRAW_HANGMAN))
        hangman_img_rect = None
        if 0 <= image_index < len(self.hangman_images):
            try:
                hangman_img = self.hangman_images[image_index]
                img_top_y = 80
                img_center_x = SCREEN_WIDTH * 0.75
                hangman_img_rect = hangman_img.get_rect(centerx=int(img_center_x), top=img_top_y)
                hangman_img_rect.clamp_ip(self.screen.get_rect())
                self.screen.blit(hangman_img, hangman_img_rect.topleft)
            except Exception as e:
                print(f"Error blitting Hangman image index {image_index}: {e}")
                traceback.print_exc()
                pygame.draw.rect(self.screen, RED, hangman_img_rect or (SCREEN_WIDTH*0.6, 80, 150, 250), 3)
        else:
            print(f"Error: Invalid hangman image index {image_index} (List size: {len(self.hangman_images)})")

        # Hint and Word Display - Adjusted position
        if self.current_word:
            question_area_width = (hangman_img_rect.left - 40) if hangman_img_rect else (SCREEN_WIDTH // 2 - 40)
            _render_text_generic(self.screen, f"Hint: {self.current_question}", self.question_font, HINT_COLOR,
                                 top_left_pos=(30, 80),
                                 wrap_width=max(100, question_area_width))

            display_word = ""
            for char in self.current_word:
                if char.isalpha():
                    display_word += f"{char} " if char in self.guessed_letters else "_ "
                elif char == '-':
                    display_word += "- "
                else:
                    display_word += f"{char} " if char in self.guessed_letters else "_ "
            
            # Adjust word display position based on keyboard visibility
            word_display_y = SCREEN_HEIGHT - 200 - content_offset
            _render_text_generic(self.screen, display_word.strip(), self.word_font, BLACK,
                                 center_pos=(SCREEN_WIDTH // 2, word_display_y))

            if self.guessed_letters:
                guessed_text = "Guessed: " + ", ".join(sorted(list(self.guessed_letters)))
                _render_text_generic(self.screen, guessed_text, self.info_font, BLACK,
                                     center_pos=(SCREEN_WIDTH // 2, word_display_y + 50),
                                     wrap_width=SCREEN_WIDTH - 60)

        # --- Bottom Area Info - Adjusted for keyboard ---
        bottom_area_y = SCREEN_HEIGHT - 120 - content_offset
        
        attempts_text = f"Attempts Left: {self.total_attempts_left}"
        attempts_color = ATTEMPTS_COLOR_NORMAL
        if self.total_attempts_left <= 1: attempts_color = ATTEMPTS_COLOR_CRITICAL
        elif self.total_attempts_left <= TOTAL_SESSION_ATTEMPTS // 2: attempts_color = ATTEMPTS_COLOR_LOW
        _render_text_generic(self.screen, attempts_text, self.attempts_font, attempts_color, top_left_pos=(30, bottom_area_y))

        if self.message:
            msg_color = DARK_GREEN if ("Congratulations" in self.message or "Complete!" in self.message or "Correct!" in self.message) else \
                        (DARK_RED if ("Game Over" in self.message or "Incorrect!" in self.message or "Error" in self.message) else BLACK)
            _render_text_generic(self.screen, self.message, self.msg_font, msg_color,
                                 center_pos=(SCREEN_WIDTH // 2, bottom_area_y + 40),
                                 wrap_width=SCREEN_WIDTH - 80)

        # --- Keyboard Button - Adjusted position ---
        kb_w, kb_h = 150, 40
        kb_x = SCREEN_WIDTH - kb_w - 20
        kb_y = bottom_area_y - 60
        self.keyboard_button_rect = pygame.Rect(kb_x, kb_y, kb_w, kb_h)

        kb_color = (200, 200, 200) if self.keyboard_button_rect.collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(self.screen, kb_color, self.keyboard_button_rect, border_radius=10)
        _render_text_generic(self.screen, "Keyboard", self.info_font, (0, 0, 0),
                             center_pos=self.keyboard_button_rect.center)

        # Footer Text - Adjusted position
        footer_y = SCREEN_HEIGHT - 25 - content_offset
        esc_action = "Quit" if not self.is_fullscreen else "Exit Fullscreen"
        if self.round_complete_flag:
            footer_text = f"Press SPACE for next round | ESC to {esc_action} | F1 Help"
        else:
            footer_text = f"Guess a letter (A-Z) | ESC to {esc_action} | F1 Help"
        _render_text_generic(self.screen, footer_text, self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, footer_y))

    def run(self):
        """Runs the main event loop. Returns GAME_QUIT or GAME_ERROR."""
        print(f"\nStarting Pygame {self.game_name} Session loop...")
        running = True
        game_status = GAME_ERROR # Default return status

        # If init failed to load items, end screen is already set
        if self.show_end_screen and "Error" in self.end_screen_message:
             print(f"Starting {self.game_name} directly in error end screen.")
             # The loop will run but only show the end screen

        while running:
            try:
                # --- Event Handling ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print(f"{self.game_name}: QUIT event received.")
                        game_status = GAME_QUIT
                        running = False; break

                    # --- Mouse Events ---
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if ESC button was clicked
                        if hasattr(self, "esc_button_rect") and self.esc_button_rect.collidepoint(event.pos):
                            print(f"ESC button clicked ({self.game_name}): Quitting game.")
                            game_status = GAME_QUIT
                            running = False
                            continue
                            
                        if event.button == 1: # Left-click
                            # Check if keyboard button was clicked
                            if hasattr(self, "keyboard_button_rect") and self.keyboard_button_rect.collidepoint(event.pos):
                                self.toggle_keyboard()
                                continue
                                
                            # Handle keyboard clicks if visible
                            if self.keyboard_visible and self._handle_keyboard_click(event.pos):
                                continue

                            # Handle end screen buttons
                            if self.show_end_screen:
                                if self.play_again_rect and self.play_again_rect.collidepoint(event.pos):
                                    print("Play Again button clicked.")
                                    self._reset_game()
                                elif self.back_rect and self.back_rect.collidepoint(event.pos):
                                    print("Back button clicked.")
                                    game_status = GAME_QUIT
                                    running = False

                    # --- Keyboard Input ---
                    if event.type == pygame.KEYDOWN:
                        key, uni = event.key, event.unicode

                        # --- ESC Key (Always Active) ---
                        if key == pygame.K_ESCAPE:
                            if self.is_fullscreen:
                                try:
                                    print(f"ESC pressed ({self.game_name}): Switching to windowed.")
                                    self.is_fullscreen = False
                                    self._setup_screen() # Recreate screen in windowed
                                except pygame.error as e:
                                    print(f"Error switching to windowed: {e}. Quitting.")
                                    game_status = GAME_ERROR
                                    running = False; break
                            else:
                                print(f"ESC pressed ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False; break
                        # --- End ESC ---

                        # --- Input specific to End Screen ---
                        elif self.show_end_screen:
                             # Optional: Could add keybinds like P for Play Again, B for Back
                             pass # Currently handled by mouse clicks only

                        # --- Input specific to Help Screen ---
                        elif self.show_help:
                            if key == pygame.K_F1: # Toggle help off
                                self.show_help = False
                            # Ignore other keys when help is shown

                        # --- Input specific to Active Game ---
                        else:
                            if key == pygame.K_F1: # Toggle help on
                                self.show_help = True
                            elif self.round_complete_flag and key == pygame.K_SPACE:
                                self._next_round()
                            elif not self.round_complete_flag and uni.isalpha() and len(uni) == 1:
                                self._process_guess(uni)
                        # --- End Active Game Input ---

                if not running: break # Exit main loop

                # --- Drawing ---
                self._draw()

                # --- Frame Rate Control ---
                self.clock.tick(30)

            # --- Error Handling for Main Loop ---
            except Exception as e:
                print(f"Error in {self.game_name} game loop: {e}")
                traceback.print_exc()
                messagebox.showerror(f"{self.game_name} Runtime Error", f"An error occurred:\n{e}\n\nCheck console.")
                game_status = GAME_ERROR
                running = False # Stop the loop

        # --- Post-Loop ---
        print(f"Exiting Pygame {self.game_name} loop with status: {game_status}")
        return game_status # Return QUIT or ERROR status
    



    def _initialize_state(self):
        """Initializes or resets the game state variables."""
        self.current_round_index = -1
        self.current_question = ""
        self.current_word = ""
        self.guessed_letters = set()
        self.total_attempts_left = MAX_MISTAKES_DRAW_HANGMAN
        self.incorrect_guesses_total_for_drawing = 0 # Visual counter for current word
        self.session_game_over = False # Game lost state
        self.session_win = False       # Game won state
        self.message = ""
        self.round_complete_flag = False # Waiting for SPACE after correct word
        self.show_help = False
        # --- NEW End Screen State ---
        self.show_end_screen = False
        self.end_screen_message = ""
        self.play_again_rect = None
        self.back_rect = None

        # Handle case where loading failed
        if not self.items_for_session:
            self.session_game_over = True # Treat as immediate game over
            self.show_end_screen = True   # Go directly to end screen
            self.end_screen_message = "Error: No questions found!"
            self.message = "No Hangman questions found for this handout!" # For console/initial state

    def _load_fonts(self):
        """Loads Pygame fonts."""
        try:
            self.title_font = pygame.font.SysFont('Arial', TITLE_FONT_SIZE, bold=True)
            self.question_font = pygame.font.SysFont('Verdana', QUESTION_FONT_SIZE)
            self.word_font = pygame.font.SysFont('Courier New', WORD_FONT_SIZE, bold=True)
            self.guess_font = pygame.font.SysFont('Arial', GUESS_FONT_SIZE)
            self.msg_font = pygame.font.SysFont('Arial', MSG_FONT_SIZE, bold=True)
            self.info_font = pygame.font.SysFont('Arial', INFO_FONT_SIZE)
            self.score_font = pygame.font.SysFont('Arial', SCORE_FONT_SIZE, bold=True)
            self.attempts_font = pygame.font.SysFont('Arial', ATTEMPTS_FONT_SIZE, bold=True)
            self.end_screen_font = pygame.font.SysFont('Arial', END_SCREEN_FONT_SIZE, bold=True) # New
            print("Hangman Fonts loaded.")
        except Exception as e:
             print(f"Warning: Font loading error - {e}. Using defaults.")
             self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE + 4)
             self.question_font = pygame.font.Font(None, QUESTION_FONT_SIZE + 4)
             self.word_font = pygame.font.Font(None, WORD_FONT_SIZE + 6)
             self.guess_font = pygame.font.Font(None, GUESS_FONT_SIZE + 4)
             self.msg_font = pygame.font.Font(None, MSG_FONT_SIZE + 6)
             self.info_font = pygame.font.Font(None, INFO_FONT_SIZE + 4)
             self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE + 4)
             self.attempts_font = pygame.font.Font(None, ATTEMPTS_FONT_SIZE + 4)
             self.end_screen_font = pygame.font.Font(None, END_SCREEN_FONT_SIZE + 4) # New

    def _setup_screen(self):
        """Sets up the Pygame screen and clock (borderless 1024x600)."""
        try:
            # Force borderless 1024x600 mode
            SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 600
            os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window on screen
            flags = pygame.NOFRAME  # Borderless window mode
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

            display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
            pygame.display.set_caption(f"{self.game_name} - {display_handout_name}")
            self.clock = pygame.time.Clock()
            print(f"{self.game_name} Screen set up in borderless mode (1024x600).")

        except Exception as e:
            messagebox.showerror("Pygame Display Error", f"Display Error: {e}")
            print(f"Fatal Display Error: {e}")
            traceback.print_exc()
            if pygame.get_init():
                pygame.quit()
            sys.exit(1)

    def _load_images_safely(self):
        """Loads hangman images safely with placeholders."""
        image_load_successful = True
        missing_images = []
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_dir = os.getcwd()

        images_subdir = os.path.join(script_dir, "images")
        image_folder = images_subdir if os.path.isdir(images_subdir) else script_dir

        print(f"Loading Hangman images from: {image_folder}")
        self.hangman_images = []
        for i in range(MAX_MISTAKES_DRAW_HANGMAN + 1):
            img_path = os.path.join(image_folder, f"hangman{i}.png")
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.hangman_images.append(img)
                except pygame.error as e:
                    print(f"Error loading image '{img_path}': {e}")
                    missing_images.append(f"hangman{i}.png (load err)")
                    self.hangman_images.append(self._create_placeholder_image(i,"Load Err"))
                    image_load_successful = False
            else:
                print(f"Warning: Image not found '{img_path}'")
                missing_images.append(f"hangman{i}.png")
                self.hangman_images.append(self._create_placeholder_image(i,"Missing"))
                image_load_successful = False

        if len(self.hangman_images) != MAX_MISTAKES_DRAW_HANGMAN + 1:
             print(f"Critical Error: Image list length mismatch. Expected {MAX_MISTAKES_DRAW_HANGMAN + 1}, got {len(self.hangman_images)}")
             while len(self.hangman_images) < MAX_MISTAKES_DRAW_HANGMAN + 1:
                 self.hangman_images.append(self._create_placeholder_image(len(self.hangman_images), "Append Err"))

      
    def _create_placeholder_image(self, index, reason="Missing"):
        """Creates a gray placeholder Surface for missing images."""
        img_width, img_height = 150, 250
        placeholder = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
        placeholder.fill(GRAY + (200,))
        pygame.draw.rect(placeholder, BLACK, placeholder.get_rect(), 2)
        try:
            font = self.info_font if hasattr(self, 'info_font') and self.info_font else pygame.font.Font(None, INFO_FONT_SIZE + 4)
            txt_s = font.render(f'Img {index}', True, BLACK)
            txt_r = txt_s.get_rect(center=(img_width // 2, img_height // 2 - 10))
            placeholder.blit(txt_s, txt_r)
            rsn_s = font.render(reason, True, DARK_RED)
            rsn_r = rsn_s.get_rect(center=(img_width // 2, img_height // 2 + 15))
            placeholder.blit(rsn_s, rsn_r)
        except Exception as e:
             print(f"Error rendering placeholder text for image {index}: {e}")
        return placeholder

    def _load_session_items(self):
        """Loads, validates, shuffles, and selects Hangman items."""
        print(f"Loading Hangman items for: {self.handout_key}")
        self.items_for_session = []
        qa_list = self.all_game_data.get(self.handout_key, [])
        valid_items = []
        for item in qa_list:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                q, a = item
                proc_a = a.strip().upper() if isinstance(a, str) else ''
                if isinstance(q, str) and q.strip() and proc_a:
                    if all(c.isalnum() or c == '-' for c in proc_a):
                         valid_items.append((q.strip(), proc_a))
                    else:
                         print(f"Skipping Hangman item (Invalid Chars in Answer): Q='{q[:30]}...' A='{a}'")
            else:
                print(f"Skipping invalid Hangman data format: {item}")

        random.shuffle(valid_items)
        self.items_for_session = valid_items[:MAX_ITEMS_PER_SESSION]
        self.total_items_in_session = len(self.items_for_session)
        print(f"Loaded {self.total_items_in_session} valid Hangman items.")

    def _reset_game(self):
        """Resets the game to play again with the same handout."""
        print(f"Resetting {self.game_name}...")
        # Re-shuffle items for variety? Optional. If so, call _load_session_items again.
        # For now, just reset the state using the existing items_for_session list.
        self._initialize_state()
        # Ensure items are still loaded if needed (if _initialize_state doesn't handle empty list case)
        if not self.items_for_session:
            print("Error: Cannot reset game, no items loaded.")
            # Trigger end screen immediately with error
            self.session_game_over = True
            self.show_end_screen = True
            self.end_screen_message = "Error: No questions found!"
            self.message = "No Hangman questions found for this handout!"
        else:
            # Start the first round
            self._next_round()


    def _next_round(self):
        """Sets up the next word/question."""
        if self.session_game_over or self.session_win: return

        self.current_round_index += 1
        self.round_complete_flag = False
        self.message = ""

        # Check if all rounds completed successfully
        if self.current_round_index >= self.total_items_in_session:
            print("All Hangman rounds completed successfully!")
            self.session_win = True
            self.show_end_screen = True # Trigger end screen on win
            self.end_screen_message = "Congratulations! You Win!"
            self.message = f"Congratulations! Finished all {self.total_items_in_session} rounds!" # For console log
            self.current_question = ""; self.current_word = ""; self.guessed_letters = set()
            return

        # Start the next round
        print(f"\n--- Starting Hangman Round {self.current_round_index + 1} / {self.total_items_in_session} ---")
        self.guessed_letters = set()
        self.incorrect_guesses_total_for_drawing = 0 # Reset visual counter
        try:
            self.current_question, self.current_word = self.items_for_session[self.current_round_index]
            print(f"Q: {self.current_question}, A: {self.current_word}")
        except IndexError:
             print(f"Error accessing Hangman round index {self.current_round_index}.")
             self.session_game_over = True
             self.show_end_screen = True # Trigger end screen on error
             self.end_screen_message = "Error loading round data."
             self.message = "Error loading next round data."
             self.current_question = ""; self.current_word = ""


    def _process_guess(self, guess_char):
        """Handles player's letter guess."""
        if self.session_game_over or self.session_win or self.round_complete_flag or self.show_help or self.show_end_screen:
            return

        guess = guess_char.upper()

        if not guess.isalpha() or len(guess) != 1:
            self.message = "Please guess a single letter (A-Z)."
            return
        if guess in self.guessed_letters:
            self.message = f"You already guessed '{guess}'. Try another."
            return

        self.guessed_letters.add(guess)
        self.message = ""

        is_correct_guess = any(letter == guess for letter in self.current_word if letter.isalpha())

        if not is_correct_guess:
            self.incorrect_guesses_total_for_drawing += 1
            self.total_attempts_left -= 1
            print(f"Incorrect: '{guess}'. Session attempts left: {self.total_attempts_left}")

            if self.incorrect_guesses_total_for_drawing >= MAX_MISTAKES_DRAW_HANGMAN:
                self.total_attempts_left = 0
                self.session_game_over = True
                self.show_end_screen = True # Trigger end screen on loss
                self.end_screen_message = f"Game Over! The word was: {self.current_word}"
                self.message = self.end_screen_message # Update message for console/draw
                print(f"SESSION GAME OVER ({self.game_name}). Last word was: {self.current_word}")
            else:
                self.message = f"Incorrect! ({self.total_attempts_left} attempts left)"

        else:
            print(f"Correct: '{guess}'.")
            self.message = "Correct!"
            word_fully_guessed = all(letter in self.guessed_letters for letter in self.current_word if letter.isalpha())

            if word_fully_guessed:
                print(f"Round {self.current_round_index + 1} complete!")
                self.round_complete_flag = True # Wait for SPACE

                # Check if last word (triggers win in _next_round or run loop check)
                if self.current_round_index + 1 >= self.total_items_in_session:
                    self.message = f"Round Complete! You finished all {self.total_items_in_session} rounds!"
                    # Win state and end screen are handled after SPACE or in run loop check
                else:
                    self.message = f"Round Complete! Press SPACE for the next word."

    def _draw_help_overlay(self):
        """Draws the help screen overlay."""
        try:
            overlay_alpha = 200
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            help_title = f"{self.game_name} - Help"
            help_lines = [
                f"Guess the word related to the hint ({self.total_items_in_session} total word(s)).",
                f"You have {TOTAL_SESSION_ATTEMPTS} total incorrect guesses for the entire session.",
                "Solve all words before running out of attempts!",
                "",
                "Controls:",
                "  A-Z : Guess a letter",
                "  SPACE : Go to Next Round (after solving)",
                "  ESC : Exit Fullscreen / Quit Game",
                "  F1 : Toggle this Help screen",
            ]
            title_rect = _render_text_generic(overlay, help_title, self.msg_font, YELLOW, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20))
            current_y = title_rect.bottom + 30 if title_rect else SCREEN_HEIGHT // 4 + 10
            line_height = self.guess_font.get_height() if self.guess_font else 25
            for line in help_lines:
                line_rect = _render_text_generic(overlay, line, self.guess_font, WHITE, center_pos=(SCREEN_WIDTH // 2, int(current_y + line_height // 2)), wrap_width=SCREEN_WIDTH * 0.85)
                current_y = line_rect.bottom + 10 if line_rect else current_y + line_height + 10
            _render_text_generic(overlay, "Press F1 again to close", self.info_font, GRAY, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(overlay, (0, 0))
        except Exception as e: print(f"Error drawing Hangman help overlay: {e}"); traceback.print_exc()

    def _draw_end_screen(self):
        """Draws the 'Play Again' / 'Back' screen."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(END_SCREEN_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        # Display end message (Win/Lose/Error)
        msg_color = YELLOW if "Congratulations" in self.end_screen_message else RED
        _render_text_generic(self.screen, self.end_screen_message, self.msg_font, msg_color,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
                             wrap_width=SCREEN_WIDTH * 0.9)

        # --- Draw Buttons ---
        button_width, button_height = 220, 65 # Slightly bigger buttons
        button_y = SCREEN_HEIGHT * 0.60
        play_again_x = SCREEN_WIDTH // 2 - button_width // 2 - 90 # Adjust spacing
        back_x = SCREEN_WIDTH // 2 + button_width // 2 + 90

        # Define Rects (store them if not already defined)
        if not self.play_again_rect:
             self.play_again_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_again_rect.center = (play_again_x, button_y)

        if not self.back_rect:
            self.back_rect = pygame.Rect(0, 0, button_width, button_height)
        self.back_rect.center = (back_x, button_y)

        # Hover effect
        mouse_pos = pygame.mouse.get_pos()
        play_bg = END_SCREEN_BUTTON_HOVER_BG if self.play_again_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG
        back_bg = END_SCREEN_BUTTON_HOVER_BG if self.back_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG

        # Draw "Play Again" Button
        pygame.draw.rect(self.screen, play_bg, self.play_again_rect, border_radius=10)
        _render_text_generic(self.screen, "Play Again", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.play_again_rect.center)

        # Draw "Back" Button
        pygame.draw.rect(self.screen, back_bg, self.back_rect, border_radius=10)
        _render_text_generic(self.screen, "Back", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.back_rect.center)

        # Draw ESC instruction at bottom
        _render_text_generic(self.screen, "Press ESC to Quit/Exit Fullscreen", self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))


    def _draw(self):
        """Draws the game screen based on the current state."""
        try:
            self.screen.fill(LIGHT_BLUE) # Background color

            # --- Check State and Draw Accordingly ---
            if self.show_end_screen:
                self._draw_end_screen() # Draw the final screen
            elif self.show_help:
                # Draw normal game elements first, then overlay help
                self._draw_game_elements()
                self._draw_help_overlay()
            else:
                # Draw normal game elements
                self._draw_game_elements()
                # Draw keyboard if visible
                if self.keyboard_visible:
                    self._draw_keyboard()

            pygame.display.flip() # Update the entire screen

        except Exception as e:
            print(f"Error during Hangman draw loop: {e}")
            traceback.print_exc()
            try: # Attempt error draw
                self.screen.fill(RED)
                _render_text_generic(self.screen, "DRAW ERROR!", self.msg_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
                _render_text_generic(self.screen, "Check Console. Press ESC.", self.info_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                pygame.display.flip()
            except: pass


# --- PygameHangman Class - Add ESC Button ---
    def _draw_game_elements(self):
        """Draws the regular game elements (hint, word, hangman, etc.)."""
        # --- Top Bar Info ---
        display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
        _render_text_generic(self.screen, display_handout_name, self.title_font, BLACK, top_left_pos=(20, 15))
        
        # --- ESC Button (top-right corner) ---
        esc_button_width, esc_button_height = 80, 40
        esc_button_x = SCREEN_WIDTH - esc_button_width - 20
        esc_button_y = 15
        self.esc_button_rect = pygame.Rect(esc_button_x, esc_button_y, esc_button_width, esc_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        esc_color = (200, 100, 100) if self.esc_button_rect.collidepoint(mouse_pos) else (150, 70, 70)
        pygame.draw.rect(self.screen, esc_color, self.esc_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.esc_button_rect, 2, border_radius=8)
        _render_text_generic(self.screen, "", self.info_font, WHITE, center_pos=self.esc_button_rect.center)
        
        if self.total_items_in_session > 0: # Avoid division by zero if no items
            round_text = f"Round: {min(self.current_round_index + 1, self.total_items_in_session)} / {self.total_items_in_session}"
            _render_text_generic(self.screen, round_text, self.score_font, BLUE, top_left_pos=(SCREEN_WIDTH - 200, 15))

    # ... rest of the existing _draw_game_elements code remains the same ...

        # --- Main Game Area ---
        # Hangman Image
        image_index = max(0, min(self.incorrect_guesses_total_for_drawing, MAX_MISTAKES_DRAW_HANGMAN))
        hangman_img_rect = None
        if 0 <= image_index < len(self.hangman_images):
            try:
                hangman_img = self.hangman_images[image_index]
                img_top_y = 80
                img_center_x = SCREEN_WIDTH * 0.75
                hangman_img_rect = hangman_img.get_rect(centerx=int(img_center_x), top=img_top_y)
                hangman_img_rect.clamp_ip(self.screen.get_rect())
                self.screen.blit(hangman_img, hangman_img_rect.topleft)
            except Exception as e:
                print(f"Error blitting Hangman image index {image_index}: {e}")
                traceback.print_exc()
                pygame.draw.rect(self.screen, RED, hangman_img_rect or (SCREEN_WIDTH*0.6, 80, 150, 250), 3)
        else:
            print(f"Error: Invalid hangman image index {image_index} (List size: {len(self.hangman_images)})")

        # Hint and Word Display
        if self.current_word:
            question_area_width = (hangman_img_rect.left - 40) if hangman_img_rect else (SCREEN_WIDTH // 2 - 40)
            _render_text_generic(self.screen, f"Hint: {self.current_question}", self.question_font, HINT_COLOR,
                                 top_left_pos=(30, 80),
                                 wrap_width=max(100, question_area_width))

            display_word = ""
            for char in self.current_word:
                if char.isalpha():
                    display_word += f"{char} " if char in self.guessed_letters else "_ "
                elif char == '-':
                    display_word += "- "
                else:
                    display_word += f"{char} " if char in self.guessed_letters else "_ "
            _render_text_generic(self.screen, display_word.strip(), self.word_font, BLACK,
                                 center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200))

            if self.guessed_letters:
                guessed_text = "Guessed: " + ", ".join(sorted(list(self.guessed_letters)))
                _render_text_generic(self.screen, guessed_text, self.info_font, BLACK,
                                     center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150),
                                     wrap_width=SCREEN_WIDTH - 60)

        # --- Bottom Area Info ---
        attempts_text = f"Attempts Left: {self.total_attempts_left}"
        attempts_color = ATTEMPTS_COLOR_NORMAL
        if self.total_attempts_left <= 1: attempts_color = ATTEMPTS_COLOR_CRITICAL
        elif self.total_attempts_left <= TOTAL_SESSION_ATTEMPTS // 2: attempts_color = ATTEMPTS_COLOR_LOW
        _render_text_generic(self.screen, attempts_text, self.attempts_font, attempts_color, top_left_pos=(30, SCREEN_HEIGHT - 120))

        if self.message:
            msg_color = DARK_GREEN if ("Congratulations" in self.message or "Complete!" in self.message or "Correct!" in self.message) else \
                        (DARK_RED if ("Game Over" in self.message or "Incorrect!" in self.message or "Error" in self.message) else BLACK)
            _render_text_generic(self.screen, self.message, self.msg_font, msg_color,
                                 center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
                                 wrap_width=SCREEN_WIDTH - 80)

        # --- Keyboard Button (bottom-right corner) ---
        kb_w, kb_h = 150, 40
        kb_x = SCREEN_WIDTH - kb_w - 20
        kb_y = SCREEN_HEIGHT - kb_h - 80
        self.keyboard_button_rect = pygame.Rect(kb_x, kb_y, kb_w, kb_h)

        mouse_pos = pygame.mouse.get_pos()
        kb_color = (200, 200, 200) if self.keyboard_button_rect.collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(self.screen, kb_color, self.keyboard_button_rect, border_radius=10)
        _render_text_generic(self.screen, "Keyboard", self.info_font, (0, 0, 0),
                             center_pos=self.keyboard_button_rect.center)

        # Footer Text
        esc_action = "Quit" if not self.is_fullscreen else "Exit Fullscreen"
        if self.round_complete_flag:
            footer_text = f"Press SPACE for next round | ESC to {esc_action} | F1 Help"
        else:
            footer_text = f"Guess a letter (A-Z) | ESC to {esc_action} | F1 Help"
        _render_text_generic(self.screen, footer_text, self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))


    def run(self):
        """Runs the main event loop. Returns GAME_QUIT or GAME_ERROR."""
        print(f"\nStarting Pygame {self.game_name} Session loop...")
        running = True
        game_status = GAME_ERROR # Default return status

        # If init failed to load items, end screen is already set
        if self.show_end_screen and "Error" in self.end_screen_message:
             print(f"Starting {self.game_name} directly in error end screen.")
             # The loop will run but only show the end screen

        while running:
            try:
                # --- Event Handling ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print(f"{self.game_name}: QUIT event received.")
                        game_status = GAME_QUIT
                        running = False; break

                    # --- Mouse Events for Keyboard Dragging/Resizing ---
                    if event.type == pygame.MOUSEBUTTONDOWN:

                                # Check if ESC button was clicked
                        if hasattr(self, "esc_button_rect") and self.esc_button_rect.collidepoint(event.pos):
                            print(f"ESC button clicked ({self.game_name}): Quitting game.")
                            game_status = GAME_QUIT
                            running = False
                            continue
                        if event.button == 1: # Left-click
                            # Check if keyboard button was clicked
                            if hasattr(self, "keyboard_button_rect") and self.keyboard_button_rect.collidepoint(event.pos):
                                self.toggle_keyboard()
                                continue
                                
                            # Handle keyboard clicks, dragging, and resizing if visible
                            if self.keyboard_visible and self._handle_keyboard_click(event.pos):
                                continue

                            # Handle end screen buttons
                            if self.show_end_screen:
                                if self.play_again_rect and self.play_again_rect.collidepoint(event.pos):
                                    print("Play Again button clicked.")
                                    self._reset_game()
                                elif self.back_rect and self.back_rect.collidepoint(event.pos):
                                    print("Back button clicked.")
                                    game_status = GAME_QUIT
                                    running = False

                    elif event.type == pygame.MOUSEMOTION:
                        # Handle keyboard dragging and resizing
                        if self.keyboard_visible:
                            if self.keyboard_dragging:
                                self._handle_keyboard_drag(event.pos)
                            elif self.keyboard_resizing:
                                self._handle_keyboard_resize(event.pos)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1: # Left-click release
                            self.keyboard_dragging = False
                            self.keyboard_resizing = False

                    # --- Keyboard Input ---
                    if event.type == pygame.KEYDOWN:
                        key, uni = event.key, event.unicode

                        # --- ESC Key (Always Active) ---
                        if key == pygame.K_ESCAPE:
                            if self.is_fullscreen:
                                try:
                                    print(f"ESC pressed ({self.game_name}): Switching to windowed.")
                                    self.is_fullscreen = False
                                    self._setup_screen() # Recreate screen in windowed
                                except pygame.error as e:
                                    print(f"Error switching to windowed: {e}. Quitting.")
                                    game_status = GAME_ERROR
                                    running = False; break
                            else:
                                print(f"ESC pressed ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False; break
                        # --- End ESC ---

                        # --- Input specific to End Screen ---
                        elif self.show_end_screen:
                             # Optional: Could add keybinds like P for Play Again, B for Back
                             pass # Currently handled by mouse clicks only

                        # --- Input specific to Help Screen ---
                        elif self.show_help:
                            if key == pygame.K_F1: # Toggle help off
                                self.show_help = False
                            # Ignore other keys when help is shown

                        # --- Input specific to Active Game ---
                        else:
                            if key == pygame.K_F1: # Toggle help on
                                self.show_help = True
                            elif self.round_complete_flag and key == pygame.K_SPACE:
                                self._next_round()
                            elif not self.round_complete_flag and uni.isalpha() and len(uni) == 1:
                                self._process_guess(uni)
                        # --- End Active Game Input ---

                if not running: break # Exit main loop

                # --- Drawing ---
                self._draw()

                # --- Frame Rate Control ---
                self.clock.tick(30)

            # --- Error Handling for Main Loop ---
            except Exception as e:
                print(f"Error in {self.game_name} game loop: {e}")
                traceback.print_exc()
                messagebox.showerror(f"{self.game_name} Runtime Error", f"An error occurred:\n{e}\n\nCheck console.")
                game_status = GAME_ERROR
                running = False # Stop the loop

        # --- Post-Loop ---
        print(f"Exiting Pygame {self.game_name} loop with status: {game_status}")
        return game_status # Return QUIT or ERROR status


# --- PygameWordScramble Class ---
class PygameWordScramble:
    """Manages the Word Scramble game (Midterm Period)."""
    def __init__(self, handout_key):
        self.handout_key = handout_key
        self.all_game_data = load_game_data_by_handout()
        self.game_name = "Word Scramble"
        self.is_fullscreen = False

        self.items_for_session = []
        self.total_items_in_session = 0
        self._load_session_items()

        self._initialize_state()

        try:
            if not pygame.get_init(): pygame.init()
            print("Pygame initialized for Word Scramble.")
        except Exception as e: messagebox.showerror("Pygame Error", f"Init Error: {e}"); print(f"Fatal Pygame Init Error: {e}"); traceback.print_exc(); sys.exit(1)

        self._load_fonts()
        self._setup_screen()

        # Initialize keyboard
        self.keyboard_visible = False
        self._init_keyboard()

        if not self.items_for_session:
             print("Error: No valid Word Scramble items loaded.")
        else:
             self._next_round()

    def _init_keyboard(self):
        """Initialize the custom in-game keyboard"""
        self.keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', 'BACK', 'ENTER']
        ]
        
        # Keyboard state for dragging and resizing
        self.keyboard_dragging = False
        self.keyboard_resizing = False
        self.keyboard_drag_offset = (0, 0)
        self.keyboard_resize_start = (0, 0)
        self.keyboard_start_size = (0, 0)
        
        # Initial keyboard position and size
        self.keyboard_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT - 200, 600, 150)
        self.resize_handle_size = 15
        self.resize_handle_rect = pygame.Rect(0, 0, self.resize_handle_size, self.resize_handle_size)
        
        # Preferred launch position:
        # place keyboard just above the input_rect (so it sits nicely for typing)
        # NOTE: _initialize_state defines self.input_rect before this method is called in __init__
        try:
            launch_x = SCREEN_WIDTH//2 - self.keyboard_rect.width // 2
            launch_y = self.input_rect.top - self.keyboard_rect.height + 440
            # keep on-screen
            launch_x = max(0, min(launch_x, SCREEN_WIDTH - self.keyboard_rect.width))
            launch_y = max(0, min(launch_y, SCREEN_HEIGHT - self.keyboard_rect.height))
            self.keyboard_launch_pos = (launch_x, launch_y)
        except Exception:
            # fallback sensible default
            self.keyboard_launch_pos = (self.keyboard_rect.x, SCREEN_HEIGHT - self.keyboard_rect.height - 20)

        self._update_keyboard_buttons()

    def _update_keyboard_buttons(self):
        """Update keyboard button positions based on current keyboard rect"""
        self.keyboard_buttons = {}
        button_width = 50
        button_height = 40
        button_margin = 5
        
        for row_idx, row in enumerate(self.keyboard_rows):
            row_width = len(row) * (button_width + button_margin) - button_margin
            start_x = self.keyboard_rect.centerx - row_width // 2
            
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (button_width + button_margin)
                y = self.keyboard_rect.top + row_idx * (button_height + button_margin)
                rect = pygame.Rect(x, y, button_width, button_height)
                self.keyboard_buttons[key] = rect
        
        # Update resize handle position
        self.resize_handle_rect.bottomright = self.keyboard_rect.bottomright

    def toggle_keyboard(self):
        """Toggle the custom in-game keyboard visibility"""
        self.keyboard_visible = not self.keyboard_visible
        if self.keyboard_visible:
            # snap to saved launch position when opening
            try:
                self.keyboard_rect.topleft = self.keyboard_launch_pos
            except Exception:
                # fallback to centered bottom if something is wrong
                self.keyboard_rect.topleft = (SCREEN_WIDTH//2 - self.keyboard_rect.width // 2, SCREEN_HEIGHT - self.keyboard_rect.height - 20)
            self._update_keyboard_buttons()

    def _handle_keyboard_click(self, pos):
        """Handle clicks on the custom keyboard"""
        if not self.keyboard_visible:
            return False
            
        # Check for resize handle first
        if self.resize_handle_rect.collidepoint(pos):
            self.keyboard_resizing = True
            self.keyboard_resize_start = pos
            self.keyboard_start_size = (self.keyboard_rect.width, self.keyboard_rect.height)
            return True
            
        # Check for drag on keyboard background (but not on buttons)
        if self.keyboard_rect.collidepoint(pos):
            # Check if click is on a button
            for rect in self.keyboard_buttons.values():
                if rect.collidepoint(pos):
                    break
            else:  # No button was clicked, so it's a background click for dragging
                self.keyboard_dragging = True
                self.keyboard_drag_offset = (pos[0] - self.keyboard_rect.x, pos[1] - self.keyboard_rect.y)
                return True
            
        # Check for button clicks
        for key, rect in self.keyboard_buttons.items():
            if rect.collidepoint(pos):
                if not hasattr(self, "player_input"):
                    self.player_input = ""
                if key == 'BACK':
                    self.player_input = self.player_input[:-1]
                elif key == 'ENTER':
                    self._check_answer()
                    self.keyboard_visible = False
                elif key == '-':
                    self.player_input += '-'
                else:
                    self.player_input += key.lower()
                return True
                
        return False

    def _handle_keyboard_drag(self, pos):
        """Handle keyboard dragging"""
        if self.keyboard_dragging:
            new_x = pos[0] - self.keyboard_drag_offset[0]
            new_y = pos[1] - self.keyboard_drag_offset[1]
            
            # Keep keyboard within screen bounds
            new_x = max(0, min(new_x, SCREEN_WIDTH - self.keyboard_rect.width))
            new_y = max(0, min(new_y, SCREEN_HEIGHT - self.keyboard_rect.height))
            
            self.keyboard_rect.topleft = (new_x, new_y)
            self._update_keyboard_buttons()

    def _handle_keyboard_resize(self, pos):
        """Handle keyboard resizing"""
        if self.keyboard_resizing:
            dx = pos[0] - self.keyboard_resize_start[0]
            dy = pos[1] - self.keyboard_resize_start[1]
            
            new_width = max(400, self.keyboard_start_size[0] + dx)
            new_height = max(100, self.keyboard_start_size[1] + dy)
            
            # Keep within screen bounds
            new_width = min(new_width, SCREEN_WIDTH - self.keyboard_rect.x)
            new_height = min(new_height, SCREEN_HEIGHT - self.keyboard_rect.y)
            
            self.keyboard_rect.width = new_width
            self.keyboard_rect.height = new_height
            self._update_keyboard_buttons()

    def _draw_keyboard(self):
        """Draw the custom in-game keyboard"""
        if not self.keyboard_visible:
            return
            
        # Draw keyboard background
        pygame.draw.rect(self.screen, (200, 200, 200), self.keyboard_rect)
        pygame.draw.rect(self.screen, BLACK, self.keyboard_rect, 2)
        
        # Draw buttons
        for key, rect in self.keyboard_buttons.items():
            color = (150, 150, 150) if rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw key text
            key_surface = self.info_font.render(key, True, WHITE)
            key_rect = key_surface.get_rect(center=rect.center)
            self.screen.blit(key_surface, key_rect)
        
        # Draw resize handle
        pygame.draw.rect(self.screen, (50, 50, 50), self.resize_handle_rect)
        pygame.draw.rect(self.screen, BLACK, self.resize_handle_rect, 1)

    def _initialize_state(self):
        self.current_round_index = -1
        self.current_question = ""
        self.current_word = ""
        self.scrambled_word = ""
        self.player_input = ""
        self.input_active = True
        self.input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 200, 500, 50)
        self.score = 0
        self.total_attempts_left = TOTAL_SESSION_ATTEMPTS
        self.session_game_over = False
        self.session_finished = False # Use this for Win state now
        self.round_complete_flag = False
        self.message = ""
        self.show_help = False
        # --- End Screen State ---
        self.show_end_screen = False
        self.end_screen_message = ""
        self.play_again_rect = None
        self.back_rect = None

        if not self.items_for_session:
            self.session_game_over = True
            self.show_end_screen = True
            self.end_screen_message = "Error: No words found!"
            self.message = "No Word Scramble words found for this handout!"

    def _load_fonts(self):
        try:
            self.title_font = pygame.font.SysFont('Arial', TITLE_FONT_SIZE, bold=True)
            self.question_font = pygame.font.SysFont('Verdana', QUESTION_FONT_SIZE)
            self.scrambled_font = pygame.font.SysFont('Courier New', SCRAMBLED_WORD_FONT_SIZE, bold=True)
            self.input_font = pygame.font.SysFont('Arial', INPUT_FONT_SIZE)
            self.msg_font = pygame.font.SysFont('Arial', MSG_FONT_SIZE, bold=True)
            self.info_font = pygame.font.SysFont('Arial', INFO_FONT_SIZE)
            self.score_font = pygame.font.SysFont('Arial', SCORE_FONT_SIZE, bold=True)
            self.attempts_font = pygame.font.SysFont('Arial', ATTEMPTS_FONT_SIZE, bold=True)
            self.guess_font = pygame.font.SysFont('Arial', GUESS_FONT_SIZE)
            self.end_screen_font = pygame.font.SysFont('Arial', END_SCREEN_FONT_SIZE, bold=True) # New
            print("Word Scramble Fonts loaded.")
        except Exception as e:
             print(f"Warning: Font loading error - {e}. Using defaults.")
             self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE + 4)
             self.question_font = pygame.font.Font(None, QUESTION_FONT_SIZE + 4)
             self.scrambled_font = pygame.font.Font(None, SCRAMBLED_WORD_FONT_SIZE + 6)
             self.input_font = pygame.font.Font(None, INPUT_FONT_SIZE + 4)
             self.msg_font = pygame.font.Font(None, MSG_FONT_SIZE + 6)
             self.info_font = pygame.font.Font(None, INFO_FONT_SIZE + 4)
             self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE + 4)
             self.attempts_font = pygame.font.Font(None, ATTEMPTS_FONT_SIZE + 4)
             self.guess_font = pygame.font.Font(None, GUESS_FONT_SIZE + 4)
             self.end_screen_font = pygame.font.Font(None, END_SCREEN_FONT_SIZE + 4) # New

    def _setup_screen(self):
        """Sets up the Pygame screen and clock (borderless 1024x600)."""
        try:
            # Force borderless 1024x600 mode
            SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 600
            os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window on screen
            flags = pygame.NOFRAME  # Borderless window mode
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

            display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
            pygame.display.set_caption(f"{self.game_name} - {display_handout_name}")
            self.clock = pygame.time.Clock()
            print(f"{self.game_name} Screen set up in borderless mode (1024x600).")

        except Exception as e:
            messagebox.showerror("Pygame Display Error", f"Display Error: {e}")
            print(f"Fatal Display Error: {e}")
            traceback.print_exc()
            if pygame.get_init():
                pygame.quit()
            sys.exit(1)

    def _scramble_word(self, word):
        """Scrambles the letters of a word, preserving structure."""
        if not word: return ""
        word_upper = word.upper()
        parts = []
        current_part = ""
        for char in word_upper:
            if char.isalnum():
                current_part += char
            else:
                if current_part:
                    parts.append(current_part)
                parts.append(char)
                current_part = ""
        if current_part:
            parts.append(current_part)

        scrambled_parts = []
        for part in parts:
            if part.isalnum():
                 word_list = list(part)
                 original_part = part
                 attempts = 0
                 max_attempts = 20
                 while attempts < max_attempts:
                      random.shuffle(word_list)
                      scrambled_attempt = "".join(word_list)
                      if len(original_part) <= 2 or scrambled_attempt != original_part:
                          scrambled_parts.append(scrambled_attempt)
                          break
                      attempts += 1
                 else:
                      scrambled_parts.append("".join(word_list))
                      if len(original_part) > 2: print(f"Warning: Scramble difference fail for '{original_part}'")
            else:
                 scrambled_parts.append(part)
        return "".join(scrambled_parts)

    def _load_session_items(self):
        """Loads and validates Word Scramble items."""
        print(f"Loading Word Scramble items for: {self.handout_key}")
        self.items_for_session = []
        qa_list = self.all_game_data.get(self.handout_key, [])
        valid_items = []
        for item in qa_list:
             if isinstance(item, (list, tuple)) and len(item) == 2:
                 q, a = item
                 proc_a = a.strip().upper() if isinstance(a, str) else ''
                 if isinstance(q, str) and q.strip() and proc_a:
                     scrambleable_length = sum(1 for c in proc_a if c.isalnum())
                     allowed_chars = all(c.isalnum() or c in ['-', ' '] for c in proc_a)
                     if allowed_chars and scrambleable_length >= 2:
                         valid_items.append((q.strip(), proc_a))
                     else:
                         print(f"Skipping Scramble item (Invalid Chars/Length): Q='{q[:30]}...' A='{a}'")
             else:
                print(f"Skipping invalid Scramble data format: {item}")

        random.shuffle(valid_items)
        self.items_for_session = valid_items[:MAX_ITEMS_PER_SESSION]
        self.total_items_in_session = len(self.items_for_session)
        print(f"Loaded {self.total_items_in_session} valid Word Scramble items.")

    def _reset_game(self):
        """Resets the game to play again."""
        print(f"Resetting {self.game_name}...")
        self._initialize_state()
        if not self.items_for_session:
             print("Error: Cannot reset game, no items loaded.")
             self.session_game_over = True
             self.show_end_screen = True
             self.end_screen_message = "Error: No words found!"
             self.message = "No Word Scramble words found for this handout!"
        else:
            self._next_round()

    def _next_round(self):
        """Sets up the next word."""
        if self.session_game_over or self.session_finished: return

        self.current_round_index += 1
        self.round_complete_flag = False
        self.player_input = ""
        self.message = ""
        self.input_active = True

        if self.current_round_index >= self.total_items_in_session:
            print("All Word Scramble rounds completed successfully!")
            self.session_finished = True # Mark as Win
            self.show_end_screen = True # Trigger end screen
            self.end_screen_message = "Congratulations! You Win!"
            self.message = f"Congratulations! Finished all {self.total_items_in_session} words! Final Score: {self.score}"
            self.current_question = ""; self.current_word = ""; self.scrambled_word = ""
            return

        print(f"\n--- Starting Word Scramble Round {self.current_round_index + 1} / {self.total_items_in_session} ---")
        try:
            self.current_question, self.current_word = self.items_for_session[self.current_round_index]
            self.scrambled_word = self._scramble_word(self.current_word)
            print(f"Hint: {self.current_question}\nWord: {self.current_word}\nScrambled: {self.scrambled_word}")
        except IndexError:
             print(f"Error accessing Word Scramble round index {self.current_round_index}.")
             self.session_game_over = True; self.show_end_screen = True
             self.end_screen_message = "Error loading round data."
             self.message = "Error loading next round data."
             self.current_question = ""; self.current_word = ""; self.scrambled_word = ""
        except Exception as e:
            print(f"Error during next round setup: {e}"); traceback.print_exc()
            self.session_game_over = True; self.show_end_screen = True
            self.end_screen_message = "Error setting up the round."

    def _check_answer(self):
        """Compares player's input to the correct word."""
        if self.session_finished or self.session_game_over or self.round_complete_flag or self.show_help or self.show_end_screen:
            return

        player_answer = self.player_input.strip().upper()
        correct_answer = self.current_word

        print(f"Checking answer: Input='{player_answer}', Correct='{correct_answer}'")

        if player_answer == correct_answer:
            self.score += 1
            self.message = "Correct! Press SPACE for the next word."
            print(f"Correct! Score: {self.score}")
            self.round_complete_flag = True
            self.input_active = False
            # Win condition is checked in _next_round or run loop
            if self.current_round_index + 1 >= self.total_items_in_session:
                # Update message but let _next_round handle state transition
                 self.message = f"Correct! You finished all {self.total_items_in_session} words! Final Score: {self.score}"

        else:
            print("Incorrect guess.")
            self.total_attempts_left -= 1
            print(f"Incorrect guess. Session attempts left: {self.total_attempts_left}")

            if self.total_attempts_left <= 0:
                self.total_attempts_left = 0
                self.session_game_over = True
                self.show_end_screen = True # Trigger end screen on loss
                self.input_active = False
                self.end_screen_message = f"Game Over! The word was: {self.current_word}"
                self.message = self.end_screen_message
                print(f"SESSION GAME OVER ({self.game_name}). Last word was: {self.current_word}")
            else:
                self.message = f"Incorrect. Try again! ({self.total_attempts_left} attempts left)"

    def _draw_help_overlay(self):
        """Draws the help overlay."""
        try:
            overlay_alpha = 200; overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, overlay_alpha))
            help_title = f"{self.game_name} - Help"
            help_lines = [
                f"Unscramble the word based on the hint ({self.total_items_in_session} total word(s)).",
                f"You have {TOTAL_SESSION_ATTEMPTS} total incorrect guesses for the entire session.",
                "Submitting an incorrect word uses one attempt.",
                "Solve all words before running out of attempts!",
                "", "Controls:", "  A-Z, 0-9, -, Space : Type your answer", "  BACKSPACE : Delete last character",
                "  ENTER / KP_ENTER : Submit answer", "  SPACE : Go to Next Word (only after solving)",
                "  ESC : Exit Fullscreen / Quit Game", "  F1 : Toggle this Help screen",
                "  MOUSE CLICK : Activate/Deactivate input box",
            ]
            title_rect = _render_text_generic(overlay, help_title, self.msg_font, YELLOW, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20))
            current_y = title_rect.bottom + 30 if title_rect else SCREEN_HEIGHT // 4 + 10
            line_height = self.guess_font.get_height() if self.guess_font else 25
            for line in help_lines:
                line_rect = _render_text_generic(overlay, line, self.guess_font, WHITE, center_pos=(SCREEN_WIDTH // 2, int(current_y + line_height // 2)), wrap_width=SCREEN_WIDTH * 0.85)
                current_y = line_rect.bottom + 10 if line_rect else current_y + line_height + 10
            _render_text_generic(overlay, "Press F1 again to close", self.info_font, GRAY, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(overlay, (0, 0))
        except Exception as e: print(f"Error drawing WordScramble help overlay: {e}"); traceback.print_exc()

    def _draw_end_screen(self):
        """Draws the 'Play Again' / 'Back' screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(END_SCREEN_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        msg_color = YELLOW if "Congratulations" in self.end_screen_message else RED
        _render_text_generic(self.screen, self.end_screen_message, self.msg_font, msg_color,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
                             wrap_width=SCREEN_WIDTH * 0.9)

        score_text = f"Final Score: {self.score}"
        _render_text_generic(self.screen, score_text, self.score_font, WHITE,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        button_width, button_height = 220, 65
        button_y = SCREEN_HEIGHT * 0.60
        play_again_x = SCREEN_WIDTH // 2 - button_width // 2 - 90
        back_x = SCREEN_WIDTH // 2 + button_width // 2 + 90

        if not self.play_again_rect:
             self.play_again_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_again_rect.center = (play_again_x, button_y)
        if not self.back_rect:
            self.back_rect = pygame.Rect(0, 0, button_width, button_height)
        self.back_rect.center = (back_x, button_y)

        mouse_pos = pygame.mouse.get_pos()
        play_bg = END_SCREEN_BUTTON_HOVER_BG if self.play_again_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG
        back_bg = END_SCREEN_BUTTON_HOVER_BG if self.back_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG

        pygame.draw.rect(self.screen, play_bg, self.play_again_rect, border_radius=10)
        _render_text_generic(self.screen, "Play Again", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.play_again_rect.center)
        pygame.draw.rect(self.screen, back_bg, self.back_rect, border_radius=10)
        _render_text_generic(self.screen, "Back", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.back_rect.center)

        _render_text_generic(self.screen, "Press ESC to Quit/Exit Fullscreen", self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))


    def _draw(self):
        """Draws the game screen based on state."""
        try:
            self.screen.fill(LIGHT_BLUE) # Background

            if self.show_end_screen:
                self._draw_end_screen()
            elif self.show_help:
                self._draw_game_elements()
                self._draw_help_overlay()
            else:
                self._draw_game_elements()
                # Draw keyboard if visible
                if self.keyboard_visible:
                    self._draw_keyboard()

            pygame.display.flip() # Update screen

        except Exception as e:
            print(f"Error during Word Scramble draw loop: {e}")
            traceback.print_exc()
            try: # Attempt error draw
                self.screen.fill(RED)
                _render_text_generic(self.screen, "DRAW ERROR!", self.msg_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
                _render_text_generic(self.screen, "Check Console. Press ESC.", self.info_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                pygame.display.flip()
            except: pass

# --- PygameWordScramble Class - Add ESC Button ---
    def _draw_game_elements(self):
        """Draws the regular game elements."""
        # Top Bar
        display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
        _render_text_generic(self.screen, display_handout_name, self.title_font, BLACK, top_left_pos=(20, 15))
        
        # --- ESC Button (top-right corner) ---
        esc_button_width, esc_button_height = 80, 40
        esc_button_x = SCREEN_WIDTH - esc_button_width - 20
        esc_button_y = 15
        self.esc_button_rect = pygame.Rect(esc_button_x, esc_button_y, esc_button_width, esc_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        esc_color = (200, 100, 100) if self.esc_button_rect.collidepoint(mouse_pos) else (150, 70, 70)
        pygame.draw.rect(self.screen, esc_color, self.esc_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.esc_button_rect, 2, border_radius=8)
        _render_text_generic(self.screen, "", self.info_font, WHITE, center_pos=self.esc_button_rect.center)
        
        if self.total_items_in_session > 0:
            score_text = f"Score: {self.score}"
            round_text = f"Word: {min(self.current_round_index + 1, self.total_items_in_session)} / {self.total_items_in_session}"
            _render_text_generic(self.screen, score_text, self.score_font, BLUE, top_left_pos=(SCREEN_WIDTH - 150, 15))
            _render_text_generic(self.screen, round_text, self.score_font, BLUE, top_left_pos=(SCREEN_WIDTH - 150, 45))

    # ... rest of the existing _draw_game_elements code remains the same ...

        # Main Game Area (Hint, Scrambled Word, Input Box)
        if self.current_word:
            _render_text_generic(self.screen, f"Hint: {self.current_question}", self.question_font, HINT_COLOR,
                                 center_pos=(SCREEN_WIDTH // 2, 100), wrap_width=SCREEN_WIDTH * 0.9)
            _render_text_generic(self.screen, self.scrambled_word, self.scrambled_font, BLACK,
                                 center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

            # Input Box (only draw if round is active)
            if not self.round_complete_flag:
                input_box_color = INPUT_BOX_COLOR_ACTIVE if self.input_active else INPUT_BOX_COLOR_INACTIVE
                pygame.draw.rect(self.screen, input_box_color, self.input_rect)
                pygame.draw.rect(self.screen, BLACK, self.input_rect, 2)
                if self.input_font:
                    try:
                        input_surface = self.input_font.render(self.player_input, True, INPUT_TEXT_COLOR)
                        text_x = self.input_rect.x + 10
                        text_y = self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2
                        clip_rect = self.input_rect.inflate(-20, 0)
                        self.screen.set_clip(clip_rect)
                        self.screen.blit(input_surface, (text_x, text_y))
                        self.screen.set_clip(None)
                    except Exception as e:
                         print(f"Error rendering input text '{self.player_input}': {e}")

        # Bottom Area
        attempts_text = f"Attempts Left: {self.total_attempts_left}"
        attempts_color = ATTEMPTS_COLOR_NORMAL
        if self.total_attempts_left <= 1: attempts_color = ATTEMPTS_COLOR_CRITICAL
        elif self.total_attempts_left <= TOTAL_SESSION_ATTEMPTS // 2: attempts_color = ATTEMPTS_COLOR_LOW
        _render_text_generic(self.screen, attempts_text, self.attempts_font, attempts_color, top_left_pos=(30, SCREEN_HEIGHT - 120))

        if self.message:
             msg_color = DARK_GREEN if ("Correct" in self.message or "Congratulations" in self.message) else \
                         (DARK_RED if ("Incorrect" in self.message or "Game Over" in self.message or "Error" in self.message) else BLACK)
             _render_text_generic(self.screen, self.message, self.msg_font, msg_color,
                                  center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
                                  wrap_width=SCREEN_WIDTH - 80)
        kb_w, kb_h = 150, 40
        kb_x = SCREEN_WIDTH - kb_w - 20
        kb_y = SCREEN_HEIGHT - kb_h - 80
        self.keyboard_button_rect = pygame.Rect(kb_x, kb_y, kb_w, kb_h)

        mouse_pos = pygame.mouse.get_pos()
        kb_color = (200, 200, 200) if self.keyboard_button_rect.collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(self.screen, kb_color, self.keyboard_button_rect, border_radius=10)
        _render_text_generic(self.screen, "Keyboard", self.info_font, (0, 0, 0),
                             center_pos=self.keyboard_button_rect.center)
        # Footer Text
        esc_action = "Quit" if not self.is_fullscreen else "Exit Fullscreen"
        if self.round_complete_flag:
            footer_text = f"Press SPACE for next word | ESC to {esc_action} | F1 Help"
        else:
            footer_text = f"Type answer and press ENTER | ESC to {esc_action} | F1 Help"
        _render_text_generic(self.screen, footer_text, self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))


    def run(self):
        """Runs the main event loop. Returns GAME_QUIT or GAME_ERROR."""
        print(f"\nStarting Pygame {self.game_name} Session loop...")
        running = True
        game_status = GAME_ERROR

        if self.show_end_screen and "Error" in self.end_screen_message:
             print(f"Starting {self.game_name} directly in error end screen.")

        while running:
            try:
                # Event Handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_status = GAME_QUIT
                        running = False; break

                    # --- Mouse Events for Keyboard Dragging/Resizing ---
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left-click
                            # Check if ESC button was clicked
                            if hasattr(self, "esc_button_rect") and self.esc_button_rect.collidepoint(event.pos):
                                print(f"ESC button clicked ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False
                                continue


                        if event.button == 1: # Left-click

                            # Check if keyboard button was clicked
                            if hasattr(self, "keyboard_button_rect") and self.keyboard_button_rect.collidepoint(event.pos):
                                self.toggle_keyboard()
                                continue
                                
                            # Handle keyboard clicks, dragging, and resizing if visible
                            if self.keyboard_visible and self._handle_keyboard_click(event.pos):
                                continue

                            # Handle end screen buttons
                            if self.show_end_screen:
                                if self.play_again_rect and self.play_again_rect.collidepoint(event.pos):
                                    print("Play Again button clicked.")
                                    self._reset_game()
                                elif self.back_rect and self.back_rect.collidepoint(event.pos):
                                    print("Back button clicked.")
                                    game_status = GAME_QUIT
                                    running = False

                    elif event.type == pygame.MOUSEMOTION:
                        # Handle keyboard dragging and resizing
                        if self.keyboard_visible:
                            if self.keyboard_dragging:
                                self._handle_keyboard_drag(event.pos)
                            elif self.keyboard_resizing:
                                self._handle_keyboard_resize(event.pos)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1: # Left-click release
                            # If we were dragging, finalize and save launch position
                            if getattr(self, "keyboard_dragging", False):
                                self.keyboard_dragging = False
                                # save current keyboard rect as the launch position
                                try:
                                    self.keyboard_launch_pos = (self.keyboard_rect.x, self.keyboard_rect.y)
                                except Exception:
                                    pass
                                self._update_keyboard_buttons()
                            # If we were resizing, finalize and save launch position (pos & size)
                            if getattr(self, "keyboard_resizing", False):
                                self.keyboard_resizing = False
                                try:
                                    self.keyboard_launch_pos = (self.keyboard_rect.x, self.keyboard_rect.y)
                                except Exception:
                                    pass
                                self._update_keyboard_buttons()

                    # Keyboard Input
                    if event.type == pygame.KEYDOWN:
                        key, uni = event.key, event.unicode

                        if key == pygame.K_ESCAPE: # ESC Handling
                            if self.is_fullscreen:
                                try:
                                    print(f"ESC pressed ({self.game_name}): Switching to windowed.")
                                    self.is_fullscreen = False
                                    self._setup_screen()
                                except pygame.error as e:
                                    print(f"Error switching to windowed: {e}. Quitting.")
                                    game_status = GAME_ERROR
                                    running = False; break
                            else:
                                print(f"ESC pressed ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False; break

                        elif self.show_end_screen: # End Screen Keys (Optional)
                             pass # Using mouse clicks primarily

                        elif self.show_help: # Help Screen Keys
                            if key == pygame.K_F1: self.show_help = False

                        else: # Active Game Keys
                            if key == pygame.K_F1: self.show_help = True
                            elif self.round_complete_flag and key == pygame.K_SPACE:
                                self._next_round()
                            elif self.input_active and not self.round_complete_flag:
                                if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                                    self._check_answer()
                                elif key == pygame.K_BACKSPACE:
                                    self.player_input = self.player_input[:-1]
                                elif uni.isalnum() or uni in ['-', ' ']:
                                    self.player_input += uni

                if not running: break

                # Drawing
                self._draw()
                self.clock.tick(30)

            # Error Handling
            except Exception as e:
                print(f"Error in {self.game_name} game loop: {e}")
                traceback.print_exc()
                messagebox.showerror(f"{self.game_name} Error", f"An error occurred:\n{e}\n\nCheck console.")
                game_status = GAME_ERROR
                running = False

        print(f"Exiting Pygame {self.game_name} loop with status: {game_status}")
        return game_status



# --- PygameFillInBlank Class ---
class PygameFillInBlank:
    """Manages the Fill-in-the-Blank game (Pre-Final Period)."""
    def __init__(self, handout_key):
        self.handout_key = handout_key
        self.all_game_data = load_game_data_by_handout()
        self.game_name = "Fill-in-the-Blank"
        self.is_fullscreen = False

        self.items_for_session = []
        self.total_items_in_session = 0
        self._load_session_items()

        self._initialize_state()

        try:
            if not pygame.get_init(): pygame.init()
            print("Pygame initialized for Fill-in-the-Blank.")
        except Exception as e:
            messagebox.showerror("Pygame Error", f"Init Error: {e}")
            print(f"Fatal Pygame Init Error: {e}")
            traceback.print_exc()
            sys.exit(1)

        self._load_fonts()
        self._setup_screen()

        # Initialize keyboard
        self.keyboard_visible = False
        self._init_keyboard()

        if not self.items_for_session:
             print("Error: No valid Fill-in-the-Blank items loaded.")
        else:
             self._next_round()

    def _init_keyboard(self):
        """Initialize the custom in-game keyboard"""
        self.keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '-', 'BACK', 'ENTER']
        ]
        
        # Keyboard state for dragging and resizing
        self.keyboard_dragging = False
        self.keyboard_resizing = False
        self.keyboard_drag_offset = (0, 0)
        self.keyboard_resize_start = (0, 0)
        self.keyboard_start_size = (0, 0)
        
        # Initial keyboard position and size
        self.keyboard_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT - 200, 600, 150)
        self.resize_handle_size = 15
        self.resize_handle_rect = pygame.Rect(0, 0, self.resize_handle_size, self.resize_handle_size)

        # Preferred launch position:
        # place keyboard just BELOW the input_rect (so it sits down, as requested)
        try:
            launch_x = SCREEN_WIDTH//2 - self.keyboard_rect.width // 2
            launch_y = self.input_rect.bottom + 10
            # keep on-screen
            launch_x = max(0, min(launch_x, SCREEN_WIDTH - self.keyboard_rect.width))
            launch_y = max(0, min(launch_y, SCREEN_HEIGHT - self.keyboard_rect.height))
            self.keyboard_launch_pos = (launch_x, launch_y)
        except Exception:
            # fallback sensible default
            self.keyboard_launch_pos = (self.keyboard_rect.x, SCREEN_HEIGHT - self.keyboard_rect.height - 20)

        self._update_keyboard_buttons()

    def _update_keyboard_buttons(self):
        """Update keyboard button positions based on current keyboard rect"""
        self.keyboard_buttons = {}
        button_width = 50
        button_height = 40
        button_margin = 5
        
        for row_idx, row in enumerate(self.keyboard_rows):
            row_width = len(row) * (button_width + button_margin) - button_margin
            start_x = self.keyboard_rect.centerx - row_width // 2
            
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (button_width + button_margin)
                y = self.keyboard_rect.top + row_idx * (button_height + button_margin)
                rect = pygame.Rect(x, y, button_width, button_height)
                self.keyboard_buttons[key] = rect
        
        # Update resize handle position
        self.resize_handle_rect.bottomright = self.keyboard_rect.bottomright

    def toggle_keyboard(self):
        """Toggle the custom in-game keyboard visibility"""
        self.keyboard_visible = not self.keyboard_visible
        if self.keyboard_visible:
            # snap to saved launch position when opening
            try:
                self.keyboard_rect.topleft = self.keyboard_launch_pos
            except Exception:
                # fallback to centered bottom if something is wrong
                self.keyboard_rect.topleft = (SCREEN_WIDTH//2 - self.keyboard_rect.width // 2, SCREEN_HEIGHT - self.keyboard_rect.height - 20)
            self._update_keyboard_buttons()

    def _handle_keyboard_click(self, pos):
        """Handle clicks on the custom keyboard"""
        if not self.keyboard_visible:
            return False
            
        # Check for resize handle first
        if self.resize_handle_rect.collidepoint(pos):
            self.keyboard_resizing = True
            self.keyboard_resize_start = pos
            self.keyboard_start_size = (self.keyboard_rect.width, self.keyboard_rect.height)
            return True
            
        # Check for drag on keyboard background (but not on buttons)
        if self.keyboard_rect.collidepoint(pos):
            # Check if click is on a button
            for rect in self.keyboard_buttons.values():
                if rect.collidepoint(pos):
                    break
            else:  # No button was clicked, so it's a background click for dragging
                self.keyboard_dragging = True
                self.keyboard_drag_offset = (pos[0] - self.keyboard_rect.x, pos[1] - self.keyboard_rect.y)
                return True
            
        # Check for button clicks
        for key, rect in self.keyboard_buttons.items():
            if rect.collidepoint(pos):
                if key == 'BACK':
                    self.player_input = self.player_input[:-1]
                elif key == 'ENTER':
                    self._check_answer()
                    self.keyboard_visible = False
                elif key == '-':
                    self.player_input += '-'
                else:
                    self.player_input += key.lower()
                return True
                
        return False

    def _handle_keyboard_drag(self, pos):
        """Handle keyboard dragging"""
        if self.keyboard_dragging:
            new_x = pos[0] - self.keyboard_drag_offset[0]
            new_y = pos[1] - self.keyboard_drag_offset[1]
            
            # Keep keyboard within screen bounds
            new_x = max(0, min(new_x, SCREEN_WIDTH - self.keyboard_rect.width))
            new_y = max(0, min(new_y, SCREEN_HEIGHT - self.keyboard_rect.height))
            
            self.keyboard_rect.topleft = (new_x, new_y)
            self._update_keyboard_buttons()

    def _handle_keyboard_resize(self, pos):
        """Handle keyboard resizing"""
        if self.keyboard_resizing:
            dx = pos[0] - self.keyboard_resize_start[0]
            dy = pos[1] - self.keyboard_resize_start[1]
            
            new_width = max(400, self.keyboard_start_size[0] + dx)
            new_height = max(100, self.keyboard_start_size[1] + dy)
            
            # Keep within screen bounds
            new_width = min(new_width, SCREEN_WIDTH - self.keyboard_rect.x)
            new_height = min(new_height, SCREEN_HEIGHT - self.keyboard_rect.y)
            
            self.keyboard_rect.width = new_width
            self.keyboard_rect.height = new_height
            self._update_keyboard_buttons()

    def _draw_keyboard(self):
        """Draw the custom in-game keyboard"""
        if not self.keyboard_visible:
            return
            
        # Draw keyboard background
        pygame.draw.rect(self.screen, (200, 200, 200), self.keyboard_rect)
        pygame.draw.rect(self.screen, BLACK, self.keyboard_rect, 2)
        
        # Draw buttons
        for key, rect in self.keyboard_buttons.items():
            color = (150, 150, 150) if rect.collidepoint(pygame.mouse.get_pos()) else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw key text
            key_surface = self.info_font.render(key, True, WHITE)
            key_rect = key_surface.get_rect(center=rect.center)
            self.screen.blit(key_surface, key_rect)
        
        # Draw resize handle
        pygame.draw.rect(self.screen, (50, 50, 50), self.resize_handle_rect)
        pygame.draw.rect(self.screen, BLACK, self.resize_handle_rect, 1)

    def _initialize_state(self):
        self.current_round_index = -1
        self.current_sentence_template = ""
        self.current_answer = ""
        self.display_sentence = ""
        self.player_input = ""
        self.input_active = True
        self.input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 180, 500, 50)
        self.score = 0
        self.total_attempts_left = TOTAL_SESSION_ATTEMPTS
        self.session_game_over = False
        self.session_finished = False # Win state
        self.round_complete_flag = False
        self.message = ""
        self.show_help = False
        # --- End Screen State ---
        self.show_end_screen = False
        self.end_screen_message = ""
        self.play_again_rect = None
        self.back_rect = None

        if not self.items_for_session:
            self.session_game_over = True
            self.show_end_screen = True
            self.end_screen_message = f"Error: No questions using '{BLANK_MARKER}' found!"
            self.message = f"No questions using '{BLANK_MARKER}' found for this handout!"

    def _load_fonts(self):
        try:
            self.title_font = pygame.font.SysFont('Arial', TITLE_FONT_SIZE, bold=True)
            self.sentence_font = pygame.font.SysFont('Verdana', SENTENCE_FONT_SIZE)
            self.input_font = pygame.font.SysFont('Arial', INPUT_FONT_SIZE)
            self.msg_font = pygame.font.SysFont('Arial', MSG_FONT_SIZE, bold=True)
            self.info_font = pygame.font.SysFont('Arial', INFO_FONT_SIZE)
            self.score_font = pygame.font.SysFont('Arial', SCORE_FONT_SIZE, bold=True)
            self.attempts_font = pygame.font.SysFont('Arial', ATTEMPTS_FONT_SIZE, bold=True)
            self.guess_font = pygame.font.SysFont('Arial', GUESS_FONT_SIZE)
            self.end_screen_font = pygame.font.SysFont('Arial', END_SCREEN_FONT_SIZE, bold=True) # New
            print("Fill-in-the-Blank Fonts loaded.")
        except Exception as e:
             print(f"Warning: Font loading error - {e}. Using defaults.")
             self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE + 4)
             self.sentence_font = pygame.font.Font(None, SENTENCE_FONT_SIZE + 4)
             self.input_font = pygame.font.Font(None, INPUT_FONT_SIZE + 4)
             self.msg_font = pygame.font.Font(None, MSG_FONT_SIZE + 6)
             self.info_font = pygame.font.Font(None, INFO_FONT_SIZE + 4)
             self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE + 4)
             self.attempts_font = pygame.font.Font(None, ATTEMPTS_FONT_SIZE + 4)
             self.guess_font = pygame.font.Font(None, GUESS_FONT_SIZE + 4)
             self.end_screen_font = pygame.font.Font(None, END_SCREEN_FONT_SIZE + 4) # New

    def _setup_screen(self):
        try:
            flags = pygame.FULLSCREEN if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
            display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
            pygame.display.set_caption(f"{self.game_name} - {display_handout_name}")
            self.clock = pygame.time.Clock()
            mode = "fullscreen" if self.is_fullscreen else "windowed"
            print(f"{self.game_name} Screen set up in {mode} mode ({SCREEN_WIDTH}x{SCREEN_HEIGHT}).")
        except Exception as e:
            messagebox.showerror("Pygame Display Error", f"Display Error: {e}")
            print(f"Fatal Display Error: {e}")
            traceback.print_exc()
            if pygame.get_init(): pygame.quit()
            sys.exit(1)

    def _load_session_items(self):
        """Loads and validates Fill-in-the-Blank items."""
        print(f"Loading Fill-in-the-Blank items for: {self.handout_key}")
        self.items_for_session = []
        qa_list = self.all_game_data.get(self.handout_key, [])
        valid_items = []
        for item in qa_list:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                sentence_template, answer = item
                proc_answer = answer.strip().upper() if isinstance(answer, str) else ''
                if isinstance(sentence_template, str) and BLANK_MARKER in sentence_template and proc_answer:
                    if all(c.isalnum() or c in ['-', ' '] for c in proc_answer):
                        valid_items.append((sentence_template.strip(), proc_answer))
                    else:
                        print(f"Skipping FillBlank item (Invalid Chars): S='{sentence_template[:50]}...' A='{answer}'")
            else:
                print(f"Skipping invalid FillBlank data format: {item}")

        random.shuffle(valid_items)
        self.items_for_session = valid_items[:MAX_ITEMS_PER_SESSION]
        self.total_items_in_session = len(self.items_for_session)
        print(f"Loaded {self.total_items_in_session} valid Fill-in-the-Blank items.")

    def _reset_game(self):
        """Resets the game to play again."""
        print(f"Resetting {self.game_name}...")
        self._initialize_state()
        if not self.items_for_session:
             print("Error: Cannot reset game, no items loaded.")
             self.session_game_over = True
             self.show_end_screen = True
             self.end_screen_message = f"Error: No questions using '{BLANK_MARKER}' found!"
             self.message = f"No questions using '{BLANK_MARKER}' found for this handout!"
        else:
            self._next_round()

    def _next_round(self):
        """Sets up the next sentence."""
        if self.session_game_over or self.session_finished: return

        self.current_round_index += 1
        self.round_complete_flag = False
        self.player_input = ""
        self.message = ""
        self.input_active = True

        if self.current_round_index >= self.total_items_in_session:
            print("All Fill-in-the-Blank rounds completed successfully!")
            self.session_finished = True # Win state
            self.show_end_screen = True # Trigger end screen
            self.end_screen_message = "Congratulations! You Win!"
            self.message = f"Congratulations! Finished all {self.total_items_in_session} items! Final Score: {self.score}"
            self.current_sentence_template = ""; self.current_answer = ""; self.display_sentence = ""
            return

        print(f"\n--- Starting Fill-in-the-Blank Round {self.current_round_index + 1} / {self.total_items_in_session} ---")
        try:
            self.current_sentence_template, self.current_answer = self.items_for_session[self.current_round_index]
            blank_len_visual = max(5, min(len(self.current_answer) + 2, 20))
            blank_replacement = " " + ("_" * blank_len_visual) + " "
            self.display_sentence = self.current_sentence_template.replace(BLANK_MARKER, blank_replacement)
            print(f"Template: {self.current_sentence_template}")
            print(f"Answer: {self.current_answer}")
            print(f"Display: {self.display_sentence}")
        except IndexError:
             print(f"Error accessing Fill-in-the-Blank round index {self.current_round_index}.")
             self.session_game_over = True; self.show_end_screen = True
             self.end_screen_message = "Error loading round data."
             self.message = "Error loading next round data."
             self.current_sentence_template = ""; self.current_answer = ""; self.display_sentence = ""
        except Exception as e:
             print(f"Error processing next round: {e}"); traceback.print_exc()
             self.session_game_over = True; self.show_end_screen = True
             self.end_screen_message = "Error processing round data."

    def _check_answer(self):
        """Compares player's input to the correct answer."""
        if self.session_finished or self.session_game_over or self.round_complete_flag or self.show_help or self.show_end_screen:
            return

        player_answer = self.player_input.strip().upper()
        correct_answer = self.current_answer

        print(f"Checking answer: Input='{player_answer}', Correct='{correct_answer}'")

        if player_answer == correct_answer:
            self.score += 1
            self.message = "Correct! Press SPACE for the next item."
            print(f"Correct! Score: {self.score}")
            self.round_complete_flag = True
            self.input_active = False
            self.display_sentence = self.current_sentence_template.replace(BLANK_MARKER, f" **{correct_answer}** ")
            if self.current_round_index + 1 >= self.total_items_in_session:
                self.message = f"Correct! You finished all {self.total_items_in_session} items! Final Score: {self.score}"
        else:
            print("Incorrect guess.")
            self.total_attempts_left -= 1
            print(f"Incorrect guess. Session attempts left: {self.total_attempts_left}")

            if self.total_attempts_left <= 0:
                self.total_attempts_left = 0
                self.session_game_over = True
                self.show_end_screen = True # Trigger end screen on loss
                self.input_active = False
                self.display_sentence = self.current_sentence_template.replace(BLANK_MARKER, f" [{self.current_answer}] ")
                self.end_screen_message = f"Game Over! The answer was: {self.current_answer}"
                self.message = self.end_screen_message
                print(f"SESSION GAME OVER ({self.game_name}). Last answer was: {self.current_answer}")
            else:
                self.message = f"Incorrect. Try again! ({self.total_attempts_left} attempts left)"

    def _draw_help_overlay(self):
        """Draws the help overlay."""
        try:
            overlay_alpha = 200; overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, overlay_alpha))
            help_title = f"{self.game_name} - Help"
            help_lines = [
                f"Complete the sentence by filling in the blank ({self.total_items_in_session} total item(s)).",
                f"You have {TOTAL_SESSION_ATTEMPTS} total incorrect guesses for the entire session.",
                "Submitting an incorrect answer uses one attempt.", "Complete all items before running out of attempts!", "", "Controls:",
                "  A-Z, 0-9, -, Space : Type your answer", "  BACKSPACE : Delete last character",
                "  ENTER / KP_ENTER : Submit answer", "  SPACE : Go to Next Item (only after solving)",
                "  ESC : Exit Fullscreen / Quit Game", "  F1 : Toggle this Help screen",
                "  MOUSE CLICK : Activate/Deactivate input box",
            ]
            title_rect = _render_text_generic(overlay, help_title, self.msg_font, YELLOW, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20))
            current_y = title_rect.bottom + 30 if title_rect else SCREEN_HEIGHT // 4 + 10
            line_height = self.guess_font.get_height() if self.guess_font else 25
            for line in help_lines:
                line_rect = _render_text_generic(overlay, line, self.guess_font, WHITE, center_pos=(SCREEN_WIDTH // 2, int(current_y + line_height // 2)), wrap_width=SCREEN_WIDTH * 0.85)
                current_y = line_rect.bottom + 10 if line_rect else current_y + line_height + 10
            _render_text_generic(overlay, "Press F1 again to close", self.info_font, GRAY, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(overlay, (0, 0))
        except Exception as e: print(f"Error drawing FillBlank help overlay: {e}"); traceback.print_exc()

    def _draw_end_screen(self):
        """Draws the 'Play Again' / 'Back' screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(END_SCREEN_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        msg_color = YELLOW if "Congratulations" in self.end_screen_message else RED
        _render_text_generic(self.screen, self.end_screen_message, self.msg_font, msg_color,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
                             wrap_width=SCREEN_WIDTH * 0.9)

        score_text = f"Final Score: {self.score}"
        _render_text_generic(self.screen, score_text, self.score_font, WHITE,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        button_width, button_height = 220, 65
        button_y = SCREEN_HEIGHT * 0.60
        play_again_x = SCREEN_WIDTH // 2 - button_width // 2 - 90
        back_x = SCREEN_WIDTH // 2 + button_width // 2 + 90

        if not self.play_again_rect:
             self.play_again_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_again_rect.center = (play_again_x, button_y)
        if not self.back_rect:
            self.back_rect = pygame.Rect(0, 0, button_width, button_height)
        self.back_rect.center = (back_x, button_y)

        mouse_pos = pygame.mouse.get_pos()
        play_bg = END_SCREEN_BUTTON_HOVER_BG if self.play_again_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG
        back_bg = END_SCREEN_BUTTON_HOVER_BG if self.back_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG

        pygame.draw.rect(self.screen, play_bg, self.play_again_rect, border_radius=10)
        _render_text_generic(self.screen, "Play Again", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.play_again_rect.center)
        pygame.draw.rect(self.screen, back_bg, self.back_rect, border_radius=10)
        _render_text_generic(self.screen, "Back", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.back_rect.center)

        _render_text_generic(self.screen, "Press ESC to Quit/Exit Fullscreen", self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

    def _draw(self):
        """Draws the game screen based on state."""
        try:
            self.screen.fill(FILL_IN_BG) # Use specific background

            if self.show_end_screen:
                self._draw_end_screen()
            elif self.show_help:
                self._draw_game_elements()
                self._draw_help_overlay()
            else:
                self._draw_game_elements()
                # Draw keyboard if visible
                if self.keyboard_visible:
                    self._draw_keyboard()

            pygame.display.flip() # Update screen

        except Exception as e:
            print(f"Error during Fill-in-the-Blank draw loop: {e}")
            traceback.print_exc()
            try: # Attempt error message draw
                self.screen.fill(RED)
                _render_text_generic(self.screen, "DRAW ERROR!", self.msg_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
                _render_text_generic(self.screen, "Check Console. Press ESC.", self.info_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                pygame.display.flip()
            except: pass

# --- PygameFillInBlank Class - Add ESC Button ---
    def _draw_game_elements(self):
        """Draws the regular game elements."""
        # Top Bar
        display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
        _render_text_generic(self.screen, display_handout_name, self.title_font, BLACK, top_left_pos=(20, 15))
        
        # --- ESC Button (top-right corner) ---
        esc_button_width, esc_button_height = 80, 40
        esc_button_x = SCREEN_WIDTH - esc_button_width - 20
        esc_button_y = 15
        self.esc_button_rect = pygame.Rect(esc_button_x, esc_button_y, esc_button_width, esc_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        esc_color = (200, 100, 100) if self.esc_button_rect.collidepoint(mouse_pos) else (150, 70, 70)
        pygame.draw.rect(self.screen, esc_color, self.esc_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.esc_button_rect, 2, border_radius=8)
        _render_text_generic(self.screen, "", self.info_font, WHITE, center_pos=self.esc_button_rect.center)
        
        if self.total_items_in_session > 0:
            score_text = f"Score: {self.score}"
            round_text = f"Item: {min(self.current_round_index + 1, self.total_items_in_session)} / {self.total_items_in_session}"
            _render_text_generic(self.screen, score_text, self.score_font, PURPLE, top_left_pos=(SCREEN_WIDTH - 150, 15))
            _render_text_generic(self.screen, round_text, self.score_font, PURPLE, top_left_pos=(SCREEN_WIDTH - 150, 45))

        # ... rest of the existing _draw_game_elements code remains the same ...

        # Main Game Area (Sentence and Input Box)
        if self.display_sentence:
             _render_text_generic(self.screen, self.display_sentence, self.sentence_font, BLACK,
                                  center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50),
                                  wrap_width=SCREEN_WIDTH * 0.9)

             # Input Box (only if round is active)
             if not self.round_complete_flag:
                 input_box_color = INPUT_BOX_COLOR_ACTIVE if self.input_active else INPUT_BOX_COLOR_INACTIVE
                 pygame.draw.rect(self.screen, input_box_color, self.input_rect)
                 pygame.draw.rect(self.screen, BLACK, self.input_rect, 2)
                 if self.input_font:
                    try:
                        input_surface = self.input_font.render(self.player_input, True, INPUT_TEXT_COLOR)
                        text_x = self.input_rect.x + 10
                        text_y = self.input_rect.y + (self.input_rect.height - input_surface.get_height()) // 2
                        clip_rect = self.input_rect.inflate(-20, 0)
                        self.screen.set_clip(clip_rect)
                        self.screen.blit(input_surface, (text_x, text_y))
                        self.screen.set_clip(None)
                    except Exception as e:
                        print(f"Error rendering input text '{self.player_input}': {e}")

        # Bottom Area
        attempts_text = f"Attempts Left: {self.total_attempts_left}"
        attempts_color = ATTEMPTS_COLOR_NORMAL
        if self.total_attempts_left <= 1: attempts_color = ATTEMPTS_COLOR_CRITICAL
        elif self.total_attempts_left <= TOTAL_SESSION_ATTEMPTS // 2: attempts_color = ATTEMPTS_COLOR_LOW
        _render_text_generic(self.screen, attempts_text, self.attempts_font, attempts_color, top_left_pos=(30, SCREEN_HEIGHT - 120))

        if self.message:
             msg_color = DARK_GREEN if ("Correct" in self.message or "Congratulations" in self.message) else \
                         (DARK_RED if ("Incorrect" in self.message or "Game Over" in self.message or "Error" in self.message) else BLACK)
             _render_text_generic(self.screen, self.message, self.msg_font, msg_color,
                                  center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
                                  wrap_width=SCREEN_WIDTH - 80)
        kb_w, kb_h = 150, 40
        kb_x = SCREEN_WIDTH - kb_w - 20
        kb_y = SCREEN_HEIGHT - kb_h - 80
        self.keyboard_button_rect = pygame.Rect(kb_x, kb_y, kb_w, kb_h)

        mouse_pos = pygame.mouse.get_pos()
        kb_color = (200, 200, 200) if self.keyboard_button_rect.collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(self.screen, kb_color, self.keyboard_button_rect, border_radius=10)
        _render_text_generic(self.screen, "Keyboard", self.info_font, (0, 0, 0),
                             center_pos=self.keyboard_button_rect.center)
        # Footer Text
        esc_action = "Quit" if not self.is_fullscreen else "Exit Fullscreen"
        if self.round_complete_flag:
            footer_text = f"Press SPACE for next item | ESC to {esc_action} | F1 Help"
        else:
            footer_text = f"Type your answer and press ENTER | ESC to {esc_action} | F1 Help"
        _render_text_generic(self.screen, footer_text, self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))


    def run(self):
        """Runs the main event loop. Returns GAME_QUIT or GAME_ERROR."""
        print(f"\nStarting Pygame {self.game_name} Session loop...")
        running = True
        game_status = GAME_ERROR

        if self.show_end_screen and "Error" in self.end_screen_message:
             print(f"Starting {self.game_name} directly in error end screen.")

        while running:
            try:
                # Event Handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_status = GAME_QUIT
                        running = False; break

                    # --- Mouse Events for Keyboard Dragging/Resizing ---
                    if event.type == pygame.MOUSEBUTTONDOWN:

                        if event.button == 1: # Left-click
                            # Check if ESC button was clicked
                            if hasattr(self, "esc_button_rect") and self.esc_button_rect.collidepoint(event.pos):
                                print(f"ESC button clicked ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False
                                continue

                        if event.button == 1: # Left-click
                            # Check if keyboard button was clicked
                            if hasattr(self, "keyboard_button_rect") and self.keyboard_button_rect.collidepoint(event.pos):
                                self.toggle_keyboard()
                                continue
                                
                            # Handle keyboard clicks, dragging, and resizing if visible
                            if self.keyboard_visible and self._handle_keyboard_click(event.pos):
                                continue

                            # Handle end screen buttons
                            if self.show_end_screen:
                                if self.play_again_rect and self.play_again_rect.collidepoint(event.pos):
                                    print("Play Again button clicked.")
                                    self._reset_game()
                                elif self.back_rect and self.back_rect.collidepoint(event.pos):
                                    print("Back button clicked.")
                                    game_status = GAME_QUIT
                                    running = False

                    elif event.type == pygame.MOUSEMOTION:
                        # Handle keyboard dragging and resizing
                        if self.keyboard_visible:
                            if self.keyboard_dragging:
                                self._handle_keyboard_drag(event.pos)
                            elif self.keyboard_resizing:
                                self._handle_keyboard_resize(event.pos)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1: # Left-click release
                            # If we were dragging, finalize and save launch position
                            if getattr(self, "keyboard_dragging", False):
                                self.keyboard_dragging = False
                                try:
                                    self.keyboard_launch_pos = (self.keyboard_rect.x, self.keyboard_rect.y)
                                except Exception:
                                    pass
                                self._update_keyboard_buttons()
                            # If we were resizing, finalize and save launch position (pos & size)
                            if getattr(self, "keyboard_resizing", False):
                                self.keyboard_resizing = False
                                try:
                                    self.keyboard_launch_pos = (self.keyboard_rect.x, self.keyboard_rect.y)
                                except Exception:
                                    pass
                                self._update_keyboard_buttons()

                    # Keyboard Input
                    if event.type == pygame.KEYDOWN:
                        key, uni = event.key, event.unicode

                        if key == pygame.K_ESCAPE: # ESC Handling
                            if self.is_fullscreen:
                                try:
                                    print(f"ESC pressed ({self.game_name}): Switching to windowed.")
                                    self.is_fullscreen = False
                                    self._setup_screen()
                                except pygame.error as e:
                                    print(f"Error switching to windowed: {e}. Quitting.")
                                    game_status = GAME_ERROR
                                    running = False; break
                            else:
                                print(f"ESC pressed ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False; break

                        elif self.show_end_screen: # End Screen Keys
                             pass # Using mouse clicks

                        elif self.show_help: # Help Screen Keys
                            if key == pygame.K_F1: self.show_help = False

                        else: # Active Game Keys
                            if key == pygame.K_F1: self.show_help = True
                            elif self.round_complete_flag and key == pygame.K_SPACE:
                                self._next_round()
                            elif self.input_active and not self.round_complete_flag:
                                if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                                    self._check_answer()
                                elif key == pygame.K_BACKSPACE:
                                    self.player_input = self.player_input[:-1]
                                elif uni.isalnum() or uni in ['-', ' ']:
                                    self.player_input += uni

                if not running: break

                # Drawing
                self._draw()
                self.clock.tick(30)

            # Error Handling
            except Exception as e:
                print(f"Error in {self.game_name} game loop: {e}")
                traceback.print_exc()
                messagebox.showerror(f"{self.game_name} Error", f"An error occurred:\n{e}\n\nCheck console.")
                game_status = GAME_ERROR
                running = False

        print(f"Exiting Pygame {self.game_name} loop with status: {game_status}")
        return game_status


# --- PygameOddOneOut Class ---
class PygameOddOneOut:
    """Manages the Odd One Out game (Final Period)."""
    def __init__(self, handout_key):
        self.handout_key = handout_key
        self.all_game_data = load_game_data_by_handout()
        self.game_name = "Odd One Out"
        self.is_fullscreen = False

        self.items_for_session = []
        self.total_items_in_session = 0
        self._load_session_items()

        self._initialize_state()

        try:
            if not pygame.get_init(): pygame.init()
            print("Pygame initialized for Odd One Out.")
        except Exception as e: messagebox.showerror("Pygame Error", f"Init Error: {e}"); print(f"Fatal Pygame Init Error: {e}"); traceback.print_exc(); sys.exit(1)

        self._load_fonts()
        self._setup_screen()

        if not self.items_for_session:
             print("Error: No valid Odd One Out items loaded.")
        else:
             self._next_round()

    def _initialize_state(self):
        self.current_round_index = -1
        self.current_hint = ""
        self.current_options = []
        self.correct_answer = ""
        self.shuffled_options = []
        self.option_rects = {}
        self.option_states = {}
        self.score = 0
        self.total_attempts_left = TOTAL_SESSION_ATTEMPTS
        self.session_game_over = False
        self.session_finished = False # Win state
        self.round_complete_flag = False # Round decided (choice made)
        self.message = ""
        self.show_help = False
        # --- End Screen State ---
        self.show_end_screen = False
        self.end_screen_message = ""
        self.play_again_rect = None
        self.back_rect = None

        if not self.items_for_session:
            self.session_game_over = True
            self.show_end_screen = True
            self.end_screen_message = "Error: No Odd One Out questions found!"
            self.message = "No Odd One Out questions found for this handout!"


    def _load_fonts(self):
        try:
            self.title_font = pygame.font.SysFont('Arial', TITLE_FONT_SIZE, bold=True)
            self.hint_font = pygame.font.SysFont('Verdana', QUESTION_FONT_SIZE)
            self.option_font = pygame.font.SysFont('Arial', OPTION_FONT_SIZE)
            self.msg_font = pygame.font.SysFont('Arial', MSG_FONT_SIZE, bold=True)
            self.info_font = pygame.font.SysFont('Arial', INFO_FONT_SIZE)
            self.score_font = pygame.font.SysFont('Arial', SCORE_FONT_SIZE, bold=True)
            self.attempts_font = pygame.font.SysFont('Arial', ATTEMPTS_FONT_SIZE, bold=True)
            self.guess_font = pygame.font.SysFont('Arial', GUESS_FONT_SIZE)
            self.end_screen_font = pygame.font.SysFont('Arial', END_SCREEN_FONT_SIZE, bold=True) # New
            print("Odd One Out Fonts loaded.")
        except Exception as e:
             print(f"Warning: Font loading error - {e}. Using defaults.")
             self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE + 4)
             self.hint_font = pygame.font.Font(None, QUESTION_FONT_SIZE + 4)
             self.option_font = pygame.font.Font(None, OPTION_FONT_SIZE + 4)
             self.msg_font = pygame.font.Font(None, MSG_FONT_SIZE + 6)
             self.info_font = pygame.font.Font(None, INFO_FONT_SIZE + 4)
             self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE + 4)
             self.attempts_font = pygame.font.Font(None, ATTEMPTS_FONT_SIZE + 4)
             self.guess_font = pygame.font.Font(None, GUESS_FONT_SIZE + 4)
             self.end_screen_font = pygame.font.Font(None, END_SCREEN_FONT_SIZE + 4) # New


    def _setup_screen(self):
        """Sets up the Pygame screen and clock (borderless 1024x600)."""
        try:
            # Force borderless 1024x600 mode
            SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 600
            os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window on screen
            flags = pygame.NOFRAME  # Borderless window mode
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

            display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
            pygame.display.set_caption(f"{self.game_name} - {display_handout_name}")
            self.clock = pygame.time.Clock()
            print(f"{self.game_name} Screen set up in borderless mode (1024x600).")

        except Exception as e:
            messagebox.showerror("Pygame Display Error", f"Display Error: {e}")
            print(f"Fatal Display Error: {e}")
            traceback.print_exc()
            if pygame.get_init():
                pygame.quit()
            sys.exit(1)

    def _load_session_items(self):
        """Loads and validates Odd One Out items."""
        print(f"Loading Odd One Out items for: {self.handout_key}")
        self.items_for_session = []
        data_list = self.all_game_data.get(self.handout_key, [])
        valid_items = []
        for item in data_list:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                hint, options, correct_answer = item
                if isinstance(hint, str) and hint.strip() and \
                   isinstance(options, list) and len(options) >= 3 and \
                   isinstance(correct_answer, str) and correct_answer.strip():
                    options_upper = [str(opt).strip().upper() for opt in options]
                    correct_upper = correct_answer.strip().upper()
                    if correct_upper in options_upper:
                        valid_items.append((hint.strip(), [str(o).strip() for o in options], correct_answer.strip()))
                    else:
                        print(f"Skipping OddOneOut (Answer not in Options): H='{hint}' A='{correct_answer}' Opts={options}")
            else:
                print(f"Skipping invalid OddOneOut data format: {item}")

        random.shuffle(valid_items)
        self.items_for_session = valid_items[:MAX_ITEMS_PER_SESSION]
        self.total_items_in_session = len(self.items_for_session)
        print(f"Loaded {self.total_items_in_session} valid Odd One Out items.")

    def _reset_game(self):
        """Resets the game to play again."""
        print(f"Resetting {self.game_name}...")
        self._initialize_state()
        if not self.items_for_session:
             print("Error: Cannot reset game, no items loaded.")
             self.session_game_over = True
             self.show_end_screen = True
             self.end_screen_message = "Error: No Odd One Out questions found!"
             self.message = "No Odd One Out questions found for this handout!"
        else:
            self._next_round()

    def _next_round(self):
        """Sets up the next question/options."""
        if self.session_game_over or self.session_finished: return

        self.current_round_index += 1
        self.round_complete_flag = False # Player hasn't chosen yet
        self.message = ""
        self.option_rects = {}
        self.option_states = {}

        if self.current_round_index >= self.total_items_in_session:
            print("All Odd One Out rounds completed successfully!")
            self.session_finished = True # Win state
            self.show_end_screen = True # Trigger end screen
            self.end_screen_message = "Congratulations! You Win!"
            self.message = f"Congratulations! Finished all {self.total_items_in_session} items! Final Score: {self.score}"
            self.current_hint = ""; self.current_options = []; self.correct_answer = ""; self.shuffled_options = []
            return

        print(f"\n--- Starting Odd One Out Round {self.current_round_index + 1} / {self.total_items_in_session} ---")
        try:
            self.current_hint, self.current_options, self.correct_answer = self.items_for_session[self.current_round_index]
            self.shuffled_options = self.current_options[:]
            random.shuffle(self.shuffled_options)
            for option in self.shuffled_options:
                self.option_states[option] = "normal"
            print(f"Hint: {self.current_hint}")
            print(f"Correct Answer: {self.correct_answer}")
            print(f"Shuffled Display Order: {self.shuffled_options}")
        except IndexError:
             print(f"Error accessing Odd One Out round index {self.current_round_index}.")
             self.session_game_over = True; self.show_end_screen = True
             self.end_screen_message = "Error loading round data."
             self.message = "Error loading next round data."
             self.current_hint = ""; self.current_options = []; self.correct_answer = ""; self.shuffled_options = []
        except Exception as e:
             print(f"Error processing next Odd One Out round: {e}"); traceback.print_exc()
             self.session_game_over = True; self.show_end_screen = True
             self.end_screen_message = "Error processing round data."

    def _process_click(self, mouse_pos):
        """Checks if a click hit an option button and evaluates."""
        if self.session_finished or self.session_game_over or self.round_complete_flag or self.show_help or self.show_end_screen:
            return

        clicked_option = None
        for option_text, rect in self.option_rects.items():
            if rect.collidepoint(mouse_pos):
                clicked_option = option_text
                break

        if clicked_option:
            print(f"Player clicked on: '{clicked_option}'")
            is_correct = (clicked_option.strip().upper() == self.correct_answer.strip().upper())
            self.round_complete_flag = True # Mark round as decided

            if is_correct:
                self.score += 1
                self.message = "Correct! Press SPACE for the next item."
                print(f"Correct! Score: {self.score}")
                self.option_states[clicked_option] = "correct"
                if self.current_round_index + 1 >= self.total_items_in_session:
                    self.message = f"Correct! You finished all {self.total_items_in_session} items! Final Score: {self.score}"
            else:
                print("Incorrect choice.")
                self.total_attempts_left -= 1
                print(f"Incorrect choice. Session attempts left: {self.total_attempts_left}")
                self.option_states[clicked_option] = "incorrect"

                # Highlight the actual correct answer
                correct_answer_key = next((key for key in self.option_states if key.strip().upper() == self.correct_answer.strip().upper()), None)
                if correct_answer_key:
                    self.option_states[correct_answer_key] = "correct"
                else:
                    print(f"Error: Correct answer '{self.correct_answer}' not found in option states!")

                if self.total_attempts_left <= 0:
                    self.total_attempts_left = 0
                    self.session_game_over = True
                    self.show_end_screen = True # Trigger end screen on loss
                    self.end_screen_message = f"Game Over! The odd one was: '{self.correct_answer}'."
                    self.message = self.end_screen_message
                    print(f"SESSION GAME OVER ({self.game_name}). Last answer was: {self.correct_answer}")
                else:
                    self.message = f"Incorrect. The odd one was '{self.correct_answer}'. ({self.total_attempts_left} attempts left). Press SPACE."


    def _draw_help_overlay(self):
        """Draws the help overlay."""
        try:
            overlay_alpha = 200; overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, overlay_alpha))
            help_title = f"{self.game_name} - Help"
            help_lines = [
                f"Find the item that doesn't belong ({self.total_items_in_session} total item(s)).",
                f"You have {TOTAL_SESSION_ATTEMPTS} total incorrect choices for the entire session.",
                "Clicking the wrong option uses one attempt.", "Complete all items before running out of attempts!", "", "Controls:",
                "  MOUSE CLICK : Select an option", "  SPACE : Go to Next Item (only after selecting)",
                "  ESC : Exit Fullscreen / Quit Game", "  F1 : Toggle this Help screen",
            ]
            title_rect = _render_text_generic(overlay, help_title, self.msg_font, YELLOW, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 30))
            current_y = title_rect.bottom + 30 if title_rect else SCREEN_HEIGHT // 4
            line_height = self.guess_font.get_height() if self.guess_font else 25
            for line in help_lines:
                line_rect = _render_text_generic(overlay, line, self.guess_font, WHITE, center_pos=(SCREEN_WIDTH // 2, int(current_y + line_height // 2)), wrap_width=SCREEN_WIDTH * 0.85)
                current_y = line_rect.bottom + 10 if line_rect else current_y + line_height + 10
            _render_text_generic(overlay, "Press F1 again to close", self.info_font, GRAY, center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(overlay, (0, 0))
        except Exception as e: print(f"Error drawing OddOneOut help overlay: {e}"); traceback.print_exc()

    def _draw_end_screen(self):
        """Draws the 'Play Again' / 'Back' screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(END_SCREEN_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        msg_color = YELLOW if "Congratulations" in self.end_screen_message else RED
        _render_text_generic(self.screen, self.end_screen_message, self.msg_font, msg_color,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3),
                             wrap_width=SCREEN_WIDTH * 0.9)

        score_text = f"Final Score: {self.score}"
        _render_text_generic(self.screen, score_text, self.score_font, WHITE,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        button_width, button_height = 220, 65
        button_y = SCREEN_HEIGHT * 0.60
        play_again_x = SCREEN_WIDTH // 2 - button_width // 2 - 90
        back_x = SCREEN_WIDTH // 2 + button_width // 2 + 90

        if not self.play_again_rect:
             self.play_again_rect = pygame.Rect(0, 0, button_width, button_height)
        self.play_again_rect.center = (play_again_x, button_y)
        if not self.back_rect:
            self.back_rect = pygame.Rect(0, 0, button_width, button_height)
        self.back_rect.center = (back_x, button_y)

        mouse_pos = pygame.mouse.get_pos()
        play_bg = END_SCREEN_BUTTON_HOVER_BG if self.play_again_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG
        back_bg = END_SCREEN_BUTTON_HOVER_BG if self.back_rect.collidepoint(mouse_pos) else END_SCREEN_BUTTON_BG

        pygame.draw.rect(self.screen, play_bg, self.play_again_rect, border_radius=10)
        _render_text_generic(self.screen, "Play Again", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.play_again_rect.center)
        pygame.draw.rect(self.screen, back_bg, self.back_rect, border_radius=10)
        _render_text_generic(self.screen, "Back", self.end_screen_font, END_SCREEN_BUTTON_TEXT_COLOR, center_pos=self.back_rect.center)

        _render_text_generic(self.screen, "Press ESC to Quit/Exit Fullscreen", self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

    def _draw(self):
        """Draws the game screen based on state."""
        try:
            self.screen.fill(ODD_ONE_OUT_BG) # Specific background

            if self.show_end_screen:
                self._draw_end_screen()
            elif self.show_help:
                self._draw_game_elements()
                self._draw_help_overlay()
            else:
                self._draw_game_elements()

            pygame.display.flip() # Update screen

        except Exception as e:
            print(f"Error during Odd One Out draw loop: {e}")
            traceback.print_exc()
            try: # Attempt error draw
                self.screen.fill(RED)
                _render_text_generic(self.screen, "DRAW ERROR!", self.msg_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
                _render_text_generic(self.screen, "Check Console. Press ESC.", self.info_font, WHITE, center_pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
                pygame.display.flip()
            except: pass

# --- PygameOddOneOut Class - Add ESC Button ---
    def _draw_game_elements(self):
        """Draws the regular game elements."""
        # Top Bar
        display_handout_name = self.handout_key.replace("_", " ").replace("-", " - ")
        _render_text_generic(self.screen, display_handout_name, self.title_font, BLACK, top_left_pos=(20, 15))
        
        # --- ESC Button (top-right corner) ---
        esc_button_width, esc_button_height = 80, 40
        esc_button_x = SCREEN_WIDTH - esc_button_width - 20
        esc_button_y = 15
        self.esc_button_rect = pygame.Rect(esc_button_x, esc_button_y, esc_button_width, esc_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        esc_color = (200, 100, 100) if self.esc_button_rect.collidepoint(mouse_pos) else (150, 70, 70)
        pygame.draw.rect(self.screen, esc_color, self.esc_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.esc_button_rect, 2, border_radius=8)
        _render_text_generic(self.screen, "", self.info_font, WHITE, center_pos=self.esc_button_rect.center)
        
        if self.total_items_in_session > 0:
            score_text = f"Score: {self.score}"
            round_text = f"Item: {min(self.current_round_index + 1, self.total_items_in_session)} / {self.total_items_in_session}"
            _render_text_generic(self.screen, score_text, self.score_font, DARK_RED, top_left_pos=(SCREEN_WIDTH - 150, 15))
            _render_text_generic(self.screen, round_text, self.score_font, DARK_RED, top_left_pos=(SCREEN_WIDTH - 150, 45))

        # ... rest of the existing _draw_game_elements code remains the same ...

        # Main Game Area (Hint and Options)
        if self.current_hint:
            hint_y_pos = 80
            _render_text_generic(self.screen, f"Category: {self.current_hint}", self.hint_font, HINT_COLOR,
                                 center_pos=(SCREEN_WIDTH // 2, hint_y_pos),
                                 wrap_width=SCREEN_WIDTH * 0.9)

            # Option Buttons
            option_start_y = hint_y_pos + 60
            option_height = 50
            option_width = SCREEN_WIDTH * 0.6
            option_spacing = 15
            option_center_x = SCREEN_WIDTH // 2
            self.option_rects.clear() # Clear old rects before drawing

            for i, option_text in enumerate(self.shuffled_options):
                rect_y = option_start_y + i * (option_height + option_spacing)
                option_rect = pygame.Rect(0, 0, option_width, option_height)
                option_rect.center = (option_center_x, rect_y + option_height // 2)

                state = self.option_states.get(option_text, "normal")
                bg_color = OPTION_BG_NORMAL
                text_color = OPTION_TEXT_COLOR

                if self.round_complete_flag: # Show result colors after choice
                    if state == "correct": bg_color = OPTION_BG_CORRECT; text_color = OPTION_TEXT_COLOR_RESULT
                    elif state == "incorrect": bg_color = OPTION_BG_INCORRECT; text_color = OPTION_TEXT_COLOR_RESULT

                pygame.draw.rect(self.screen, bg_color, option_rect, border_radius=5)
                pygame.draw.rect(self.screen, BLACK, option_rect, width=2, border_radius=5)
                _render_text_generic(self.screen, option_text, self.option_font, text_color,
                                     center_pos=option_rect.center, wrap_width=option_rect.width * 0.95)

                # Store rect only if round is active for clicking
                if not self.round_complete_flag:
                    self.option_rects[option_text] = option_rect

        # Bottom Area
        attempts_text = f"Attempts Left: {self.total_attempts_left}"
        attempts_color = ATTEMPTS_COLOR_NORMAL
        if self.total_attempts_left <= 1: attempts_color = ATTEMPTS_COLOR_CRITICAL
        elif self.total_attempts_left <= TOTAL_SESSION_ATTEMPTS // 2: attempts_color = ATTEMPTS_COLOR_LOW
        _render_text_generic(self.screen, attempts_text, self.attempts_font, attempts_color, top_left_pos=(30, SCREEN_HEIGHT - 120))

        if self.message:
             msg_color = DARK_GREEN if ("Correct" in self.message or "Congratulations" in self.message) else \
                         (DARK_RED if ("Incorrect" in self.message or "Game Over" in self.message or "Error" in self.message) else BLACK)
             msg_y = SCREEN_HEIGHT - 80
             _render_text_generic(self.screen, self.message, self.msg_font, msg_color,
                                  center_pos=(SCREEN_WIDTH // 2, msg_y), wrap_width=SCREEN_WIDTH - 80)

        # Footer Text
        esc_action = "Quit" if not self.is_fullscreen else "Exit Fullscreen"
        footer_y = SCREEN_HEIGHT - 25
        if self.round_complete_flag:
            footer_text = f"Press SPACE for next item | ESC to {esc_action} | F1 Help"
        else:
            footer_text = f"Click the item that doesn't belong | ESC to {esc_action} | F1 Help"
        _render_text_generic(self.screen, footer_text, self.info_font, GRAY,
                             center_pos=(SCREEN_WIDTH // 2, footer_y))

    def run(self):
        """Runs the main event loop. Returns GAME_QUIT or GAME_ERROR."""
        print(f"\nStarting Pygame {self.game_name} Session loop...")
        running = True
        game_status = GAME_ERROR

        if self.show_end_screen and "Error" in self.end_screen_message:
             print(f"Starting {self.game_name} directly in error end screen.")

        while running:
            try:
                # Event Handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_status = GAME_QUIT
                        running = False; break

                    # Keyboard Input
                    if event.type == pygame.KEYDOWN:
                        key = event.key

                        if key == pygame.K_ESCAPE: # ESC Handling
                            if self.is_fullscreen:
                                try:
                                    print(f"ESC pressed ({self.game_name}): Switching to windowed.")
                                    self.is_fullscreen = False
                                    self._setup_screen()
                                except pygame.error as e:
                                    print(f"Error switching to windowed: {e}. Quitting.")
                                    game_status = GAME_ERROR
                                    running = False; break
                            else:
                                print(f"ESC pressed ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False; break

                        elif self.show_end_screen: # End Screen Keys
                             pass # Using mouse clicks

                        elif self.show_help: # Help Screen Keys
                            if key == pygame.K_F1: self.show_help = False

                        else: # Active Game Keys
                            if key == pygame.K_F1: self.show_help = True
                            elif self.round_complete_flag and key == pygame.K_SPACE:
                                self._next_round()
                            # No other active game key inputs for OddOneOut

                    # Mouse Input
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left-click
                            # Check if ESC button was clicked
                            if hasattr(self, "esc_button_rect") and self.esc_button_rect.collidepoint(event.pos):
                                print(f"ESC button clicked ({self.game_name}): Quitting game.")
                                game_status = GAME_QUIT
                                running = False
                                continue
                        if event.button == 1: # Left Click
                            if self.show_end_screen: # End Screen Clicks
                                if self.play_again_rect and self.play_again_rect.collidepoint(event.pos):
                                    print("Play Again button clicked.")
                                    self._reset_game()
                                elif self.back_rect and self.back_rect.collidepoint(event.pos):
                                    print("Back button clicked.")
                                    game_status = GAME_QUIT
                                    running = False
                            elif not self.show_help and not self.round_complete_flag: # Active Game Clicks
                                self._process_click(event.pos)


                if not running: break

                # Drawing
                self._draw()
                self.clock.tick(30)

            # Error Handling
            except Exception as e:
                print(f"Error in {self.game_name} game loop: {e}")
                traceback.print_exc()
                messagebox.showerror(f"{self.game_name} Error", f"An error occurred:\n{e}\n\nCheck console.")
                game_status = GAME_ERROR
                running = False

        print(f"Exiting Pygame {self.game_name} loop with status: {game_status}")
        return game_status



# --- Main Application GUI (Tkinter Part) ---
class GameMode:
   


    """Manages the main Tkinter window for subject and handout selection."""
    def __init__(self, master):
        self.master = master
        check_dpad_file(self.master)
        self.master.attributes("-fullscreen", True)
        self.buttons = []       
        self.current_index = 0  
        self.subject_buttons = []  
        self.current_window_buttons = []  
        self.button_stack = []  
        

        self.master.title("Game Mode")
        self.master.config(bg="#32C1CD")
        
        self.is_tkinter_fullscreen = False
        try:
            self._maximize_tkinter_window()
        except tk.TclError:
            print("Warning: Could not maximize Tkinter window. Using default size.")
            self.master.geometry("1024x768")

        
        self.subjects = [
            "Computer-Aided Drafting", "Feedback and Control System", "Engineering Economics",
            "Logic Circuits and Design", "Computer System Architecture", "Methods of Research",
            "Data and Digital Communication", "Fundamentals of Mixed Signals and Sensors"
        ]
        self.handouts_dict = {
             "Prelim": { "Computer-Aided Drafting": ["CAD_Handout_1", "CAD_Handout_2", "CAD_Handout_2-1", "CAD_Handout_2-2"], "Feedback and Control System": ["FCS_Handout_1", "FCS_Handout_2"], "Engineering Economics": ["EE_Handout_1", "EE_Handout_2"], "Logic Circuits and Design": ["LCD_Handout_1", "LCD_Handout_2"], "Computer System Architecture": ["CSA_Handout_1", "CSA_Handout_2"], "Methods of Research": ["MR_Handout_1", "MR_Handout_2"], "Data and Digital Communication": ["DDC_Handout_1", "DDC_Handout_2"], "Fundamentals of Mixed Signals and Sensors": ["FMSS_Handout_1", "FMSS_Handout_2"] },
             "Midterm": { "Computer-Aided Drafting": ["CAD_Handout_3", "CAD_Handout_4"], "Feedback and Control System": ["FCS_Handout_3", "FCS_Handout_4"], "Engineering Economics": ["EE_Handout_3", "EE_Handout_4"], "Logic Circuits and Design": ["LCD_Handout_3", "LCD_Handout_4"], "Computer System Architecture": ["CSA_Handout_3", "CSA_Handout_4"], "Methods of Research": ["MR_Handout_3", "MR_Handout_4"], "Data and Digital Communication": ["DDC_Handout_3", "DDC_Handout_4"], "Fundamentals of Mixed Signals and Sensors": ["FMSS_Handout_3", "FMSS_Handout_4"] },
             "Pre-Final": { "Computer-Aided Drafting": ["CAD_Handout_5", "CAD_Handout_6"], "Feedback and Control System": ["FCS_Handout_5", "FCS_Handout_6"], "Engineering Economics": ["EE_Handout_5", "EE_Handout_6"], "Logic Circuits and Design": ["LCD_Handout_5"], "Computer System Architecture": ["CSA_Handout_5", "CSA_Handout_6"], "Methods of Research": ["MR_Handout_5", "MR_Handout_6"], "Data and Digital Communication": ["DDC_Handout_5", "DDC_Handout_6"], "Fundamentals of Mixed Signals and Sensors": ["FMSS_Handout_5"] },
             "Final": { "Computer-Aided Drafting": ["CAD_Handout_7", "CAD_Handout_7-1"], "Feedback and Control System": ["FCS_Handout_7"], "Engineering Economics": ["EE_Handout_7", "EE_Handout_8"], "Logic Circuits and Design": ["LCD_Handout_6"], "Computer System Architecture": ["CSA_Handout_7", "CSA_Handout_8"], "Methods of Research": ["MR_Handout_7", "MR_Handout_8"], "Data and Digital Communication": ["DDC_Handout_7"], "Fundamentals of Mixed Signals and Sensors": ["FMSS_Handout_6"] }
        }

        self.master.grid_rowconfigure(0, weight=1); [self.master.grid_rowconfigure(i, weight=2) for i in range(1, 5)]; self.master.grid_rowconfigure(5, weight=1)
        self.master.grid_columnconfigure(0, weight=1); self.master.grid_columnconfigure(1, weight=1)

        self.create_subject_buttons()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.enable_dpad_navigation(self.master)

    def open_stimo_mode(self):
        import subprocess, sys, os
        print("[GameMode] Switching back to STIMO Mode...")
        try:
            # Clean up GPIO buttons before switching
            self.cleanup_gpio_buttons()
            
            self.master.destroy()
            main_path = os.path.join(os.path.dirname(__file__), "main.py")
            subprocess.Popen([sys.executable, main_path, "--stimo"])
            print("[GameMode] STIMO Mode launched successfully.")
        except Exception as e:
            print("[GameMode] Failed to launch STIMO Mode:", e)

    def back_to_launcher(self):
        print("[GameMode] Back to Launcher button clicked.")
        self.master.destroy()  # Closes Game Mode window

        try:
            import pygetwindow as gw
            for window in gw.getWindowsWithTitle("STIMO Launcher"):
                window.restore()
                window.activate()
                break
        except Exception as e:
            print("[GameMode] Could not restore STIMO Launcher:", e)

    def _maximize_tkinter_window(self):
        """Maximizes the Tkinter window."""
        try:
            if sys.platform == "win32":
                self.master.state('zoomed')  # Maximized window for Windows
            else:
                self.master.geometry(f"{self.master.winfo_screenwidth()}x{self.master.winfo_screenheight()}+0+0")
            print("Tkinter window maximized.")
        except tk.TclError:
            print("Warning: Could not maximize Tkinter window. Using default size.")
            self.master.geometry("1024x768")

    def exit_tkinter_fullscreen(self, event=None):
        if self.is_tkinter_fullscreen:
            print("Exiting Tkinter fullscreen mode (ESC).")
            self.master.attributes('-fullscreen', False)
            self.is_tkinter_fullscreen = False

    def on_closing(self):
        print("Close button clicked. Closing Gaming Mode window...")
        try:
            # Clean up GPIO buttons
            self.cleanup_gpio_buttons()
            
            if self.master and self.master.winfo_exists() and self.is_tkinter_fullscreen:
                self.master.attributes('-fullscreen', False)
        except: pass
        if pygame.get_init(): pygame.quit(); print("Pygame quit during closing.")
        if self.master and self.master.winfo_exists():
            self.master.destroy()
            print("Gaming Mode window closed.")
        else:
            print("Gaming Mode window already destroyed.")

    def _center_toplevel(self, window, width, height):
        window.update_idletasks()
        ws = window.winfo_screenwidth(); hs = window.winfo_screenheight()
        x = max(0, (ws // 2) - (width // 2)); y = max(0, (hs // 2) - (height // 2))
        window.geometry(f'{width}x{height}+{x}+{y}')
        window.lift()

    def open_period_selection(self, subject, parent_window=None):
        w, h = 380, 450
        period_window = tk.Toplevel(self.master)
        period_window.overrideredirect(True)
        period_window.config(bg="#E1F8DC")
        period_window.resizable(False, False)
        period_window.transient(self.master)

        period_window.update_idletasks()
        period_window.deiconify()

        sw = period_window.winfo_screenwidth()
        sh = period_window.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        period_window.geometry(f"{w}x{h}+{x}+{y}")

        period_window.lift()
        period_window.focus_force()
        period_window.grab_set()

        tk.Label(
            period_window,
            text=f"Select Period for:\n{subject}",
            font=('Arial', 15, 'bold'),
            wraplength=350,
            justify=tk.CENTER,
            bg="#E1F8DC",
            fg="#32C1CD"
        ).pack(pady=(25, 15))

        periods = ["Prelim", "Midterm", "Pre-Final", "Final"]
        info = {
            "Prelim": {"c": "#FFDAB9", "g": "Hangman"},
            "Midterm": {"c": "#FFB6C1", "g": "Word Scramble"},
            "Pre-Final": {"c": "#ADD8E6", "g": "Fill-in-Blank"},
            "Final": {"c": "#FFFACD", "g": "Odd One Out"}
        }

        frame = tk.Frame(period_window, bg="#E1F8DC")
        frame.pack(pady=10, fill=tk.X, padx=20)

        # Stack handling
        self.button_stack.append((self.current_window_buttons, self.current_index))
        self.current_window_buttons = []
        self.current_index = 0

        for p in periods:
            i = info.get(p, {"c": GRAY, "g": "N/A"})
            btn = tk.Button(
                frame,
                text=f"{p}\n({i['g']})",
                font=('Arial', 13, 'bold'),
                width=20,
                height=2,
                bg=i['c'],
                fg="black",
                relief="raised",
                borderwidth=2,
                cursor="hand2",
                command=lambda period=p, subj=subject, win=period_window: [
                    win.withdraw(),
                    self.open_handout_list(period, subj, parent_window=win)
                ]
            )
            btn.default_bg = i['c']
            btn.pack(pady=8)
            self.current_window_buttons.append(btn)

        self.highlight_button(self.current_index)
        self.enable_dpad_navigation(period_window)

        # Hook D-pad
        set_dpad_target(period_window)
        check_dpad_file(period_window)

        if parent_window:
            back_btn = tk.Button(
                period_window,
                text="Back",
                font=('Arial', 12, 'bold'),
                bg="#FFCCCB",
                fg="black",
                relief="raised",
                cursor="hand2",
                command=lambda: [
                    period_window.destroy(),
                    parent_window.deiconify(),
                    self.restore_previous_buttons(),
                    set_dpad_target(parent_window),
                    check_dpad_file(parent_window),
                    parent_window.focus_force(),     # ✅ grab focus
                    parent_window.grab_set()   
                ]
            )
            back_btn.pack(pady=(10, 20))
            back_btn.default_bg = "#FFCCCB"
            self.current_window_buttons.append(back_btn)

        period_window.grab_set()
        period_window.focus_set()
        period_window.wait_window()




    def open_handout_list(self, period, subject, parent_window=None):
        handouts = self.handouts_dict.get(period, {}).get(subject, [])
        h_window = tk.Toplevel(self.master)
        h_window.overrideredirect(True)
        h_window.config(bg="#FFFACD")

        w, h = 450, 520
        sw, sh = h_window.winfo_screenwidth(), h_window.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        h_window.geometry(f"{w}x{h}+{x}+{y}")

        # Title
        tk.Label(
            h_window,
            text=f"{subject}\n{period} Handouts",
            font=('Arial', 15, 'bold'),
            justify=tk.CENTER,
            bg="#FFFACD",
            fg="#DAA520"
        ).pack(pady=(20, 10))

        frame = tk.Frame(h_window, bg="#FFFACD")
        frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        # Stack handling
        self.button_stack.append((self.current_window_buttons, self.current_index))
        self.current_window_buttons = []
        self.current_index = 0

        if not handouts:
            tk.Label(
                frame,
                text="No handouts listed.",
                font=("Arial", 11, 'italic'),
                fg="grey",
                bg="#FFFACD"
            ).pack(pady=20)
        else:
            for h_key in handouts:
                disp = h_key.replace("_", " ").replace("-", " - ")
                if len(disp) > 40:
                    disp = disp[:37] + "..."
                btn = tk.Button(
                    frame,
                    text=disp,
                    font=("Arial", 11),
                    width=35,
                    height=1,
                    bg="#B0E0E6",
                    fg="black",
                    relief="groove",
                    borderwidth=1,
                    cursor="hand2",
                    anchor="w",
                    command=lambda key=h_key, p=period, win=h_window: [
                        win.withdraw(),
                        self.choose_action(key, p, parent_window=win)
                    ]
                )
                btn.default_bg = "#B0E0E6"
                btn.pack(pady=4, fill=tk.X)
                self.current_window_buttons.append(btn)

        if self.current_window_buttons:
            self.highlight_button(self.current_index)

        self.enable_dpad_navigation(h_window)

        # Hook D-pad
        set_dpad_target(h_window)
        check_dpad_file(h_window)

        if parent_window:
            back_btn = tk.Button(
                h_window,
                text="Back",
                font=('Arial', 12, 'bold'),
                bg="#FFCCCB",
                fg="black",
                relief="raised",
                cursor="hand2",
                command=lambda: [
                    h_window.destroy(),
                    parent_window.deiconify(),
                    self.restore_previous_buttons(),
                    set_dpad_target(parent_window),
                    check_dpad_file(parent_window),
                    parent_window.focus_force(),     # ✅ grab focus
                    parent_window.grab_set() 
                ]
            )
            back_btn.pack(pady=(10, 20))
            back_btn.default_bg = "#FFCCCB"
            self.current_window_buttons.append(back_btn)

        h_window.focus_force()
        h_window.grab_set()
        h_window.wait_window()

    def enable_dpad_navigation(self, window):
        # Bind arrow keys + enter
        window.bind("<Up>", lambda e: self.move_highlight(-1))
        window.bind("<Down>", lambda e: self.move_highlight(1))
        window.bind("<Return>", lambda e: self.activate_current())

    def move_highlight(self, direction):
        if not self.current_window_buttons:
            return
        
        self.current_index = (self.current_index + direction) % len(self.current_window_buttons)
        self.highlight_button(self.current_index)

    def highlight_button(self, index):
        for i, btn in enumerate(self.current_window_buttons):
            if i == index:
                btn.config(bg="yellow")  # highlighted
            else:
                btn.config(bg=btn.default_bg)  # reset to original color

    def activate_current(self):
        if not self.current_window_buttons:
            return
        self.current_window_buttons[self.current_index].invoke()

    def restore_previous_buttons(self):
        """Restore buttons from the stack when going back"""
        if self.button_stack:
            self.current_window_buttons, self.current_index = self.button_stack.pop()
            if self.current_window_buttons:
                self.highlight_button(self.current_index)

    def create_subject_buttons(self):
        self.current_window_buttons = []  # reset for this screen
        self.subject_buttons = []  # initialize subject buttons list
        button_bg="#A4FBA6"; hover_bg="#76E5B6"; fg="#1c1c1c"; font=('Arial', 20, 'bold'); w=35; h=4; cols=2
        for i, subject in enumerate(self.subjects):
            row = (i // cols) + 1; col = i % cols
            button = tk.Button(self.master, text=subject, width=w, height=h, font=font, bg=button_bg, fg=fg,
                            relief="raised", borderwidth=3, wraplength=300, cursor="hand2",
                            command=lambda s=subject: self.open_period_selection(s, self.master))
            button.default_bg = button_bg  # save default bg
            button.grid(row=row, column=col, padx=40, pady=25, sticky="nsew")
            self.current_window_buttons.append(button)
            self.subject_buttons.append(button)  # Store in subject_buttons list
        
        # Highlight first button
        if self.current_window_buttons:
            self.highlight_button(0)

    def choose_action(self, handout_key, period, parent_window=None):
        w, h = 380, 320
        choice_window = tk.Toplevel(self.master)
        choice_window.overrideredirect(True)
        choice_window.config(bg="#F5F5DC")
        choice_window.resizable(False, False)

        sw, sh = choice_window.winfo_screenwidth(), choice_window.winfo_screenheight()
        x, y = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
        choice_window.geometry(f"{w}x{h}+{x}+{y}")

        choice_window.lift()
        choice_window.focus_force()
        choice_window.grab_set()

        main_frame = tk.Frame(choice_window, bg="#F5F5DC")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        disp_txt = handout_key.replace("_", " ").replace("-", " - ")
        tk.Label(
            main_frame,
            text=f"Selected Handout:\n{disp_txt}\n\nWhat would you like to do?",
            font=('Arial', 13, 'bold'),
            bg="#F5F5DC",
            justify=tk.CENTER,
            wraplength=350
        ).pack(pady=(0, 20))

        button_frame = tk.Frame(main_frame, bg="#F5F5DC")
        button_frame.pack(pady=10, fill="x")

        self.button_stack.append((self.current_window_buttons, self.current_index))
        self.current_window_buttons = []
        self.current_index = 0

        # View button
        btn_view = tk.Button(
            button_frame,
            text="View Handout",
            font=('Arial', 12, 'bold'),
            width=15,
            height=2,
            bg="#98FB98",
            fg="black",
            relief="raised",
            cursor="hand2",
            command=lambda win=choice_window: [
            win.destroy(),
            set_dpad_target(self.master),   # ✅ Repoint D-pad
            view_handout(handout_key)]
        )
        btn_view.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        btn_view.default_bg = "#98FB98"
        self.current_window_buttons.append(btn_view)

        game_info = {"Prelim": ("Hangman", "#FFDAB9"),
                    "Midterm": ("Word Scramble", "#FFB6C1"),
                    "Pre-Final": ("Fill-in-Blank", "#ADD8E6"),
                    "Final": ("Odd One Out", "#FFFACD")}
        g_name, g_color = game_info.get(period, ("N/A", "grey"))
        g_state = tk.NORMAL if g_name != "N/A" else tk.DISABLED

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        btn_game = tk.Button(
            button_frame,
            text=f"Play {g_name}",
            font=('Arial', 12, 'bold'),
            width=15,
            height=2,
            bg=g_color,
            fg="black",
            relief="raised",
            cursor="hand2",
            state=g_state,
            command=lambda key=handout_key, p=period, win=choice_window: [
                win.destroy(), set_dpad_target(self.master),  self.start_selected_game(p, key)
            ]
        )
        btn_game.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        btn_game.default_bg = g_color
        self.current_window_buttons.append(btn_game)

        if parent_window:
            back_btn = tk.Button(
                main_frame,
                text="Back",
                font=('Arial', 12, 'bold'),
                bg="#FFCCCB",
                fg="black",
                relief="raised",
                cursor="hand2",
                command=lambda: [
                    choice_window.destroy(),
                    parent_window.deiconify(),
                    self.restore_previous_buttons(),
                    set_dpad_target(parent_window),
                    check_dpad_file(parent_window),
                    parent_window.focus_force(),     # ✅ grab focus
                    parent_window.grab_set() 
                ]
            )
            back_btn.pack(pady=(20, 0))
            back_btn.default_bg = "#FFCCCB"
            self.current_window_buttons.append(back_btn)

        if self.current_window_buttons:
            self.highlight_button(self.current_index)
        self.enable_dpad_navigation(choice_window)

        # Hook D-pad
        set_dpad_target(choice_window)
        check_dpad_file(choice_window)

        choice_window.focus_force()
        choice_window.grab_set()
        choice_window.wait_window()



    def _restore_tkinter_window(self):
         """Restores the main Tkinter window's visibility and state."""
         print("Attempting to restore Tkinter window...")
         try:
             if self.master and self.master.winfo_exists():
                 self.master.deiconify()
                 self.master.lift()
                 self.master.focus_force()
                 if self.is_tkinter_fullscreen:
                     try:
                         print("Restoring Tkinter to fullscreen...")
                         self.master.attributes('-fullscreen', True)
                         self.master.bind('<Escape>', self.exit_tkinter_fullscreen)
                         print("Tkinter window restored to fullscreen.")
                     except tk.TclError:
                         print("Warning: Failed to restore Tkinter fullscreen.")
                 else:
                     print("Tkinter window restored (windowed).")
             else:
                 print("Tkinter master window no longer exists. Exiting.")
                 sys.exit(0)
         except tk.TclError as e:
             print(f"Error restoring Tkinter window: {e}")
             sys.exit(0)
         except Exception as e:
             print(f"Unexpected error restoring Tkinter: {e}"); traceback.print_exc(); sys.exit(1)

    def start_selected_game(self, period, handout_key):
        """Launches the appropriate Pygame game, hides Tkinter, and restores it after."""
        GameClass = None; game_name = "Unknown Game"
        if period == "Prelim": GameClass = PygameHangman; game_name = "Hangman"
        elif period == "Midterm": GameClass = PygameWordScramble; game_name = "Word Scramble"
        elif period == "Pre-Final": GameClass = PygameFillInBlank; game_name = "Fill-in-the-Blank"
        elif period == "Final": GameClass = PygameOddOneOut; game_name = "Odd One Out"
        else: messagebox.showerror("Internal Error", f"Unknown period '{period}'."); return

        print(f"\n---> Requesting {game_name} for {period}, handout: {handout_key} <---")

        # Pre-launch Data Validation (Simplified Check)
        game_data = load_game_data_by_handout()
        handout_content = game_data.get(handout_key, [])
        if not handout_content:
             messagebox.showwarning("No Game Data", f"No questions found for '{handout_key}'. Cannot start {game_name}.")
             print(f"Error: No game data for {handout_key}.")
             return
       
        # Hide Tkinter Window
        try:
            if self.master and self.master.winfo_exists(): print("Hiding Tkinter window..."); self.master.withdraw()
            else: print("Warning: Tkinter window doesn't exist when hiding.")
        except Exception as e: print(f"Warning: Error hiding Tkinter window: {e}")

        # Launch Pygame Game
        game_instance = None
        game_exit_status = GAME_ERROR # Default if something goes wrong early

        try:
            print(f"Creating {game_name} instance...")
            game_instance = GameClass(handout_key)
            print(f"Running {game_name} instance...")
            game_exit_status = game_instance.run() # Run game loop, get status (QUIT or ERROR)

        except pygame.error as e:
            print(f"!!! PYGAME RUNTIME ERROR in {game_name}: {e} !!!"); traceback.print_exc()
            messagebox.showerror("Pygame Error", f"Pygame error in {game_name}:\n{e}")
            game_exit_status = GAME_ERROR
        except Exception as e:
            print(f"!!! UNEXPECTED GAME ERROR in {game_name}: {e} !!!"); traceback.print_exc()
            messagebox.showerror("Game Error", f"Unexpected error in {game_name}:\n{e}")
            game_exit_status = GAME_ERROR
        finally:
             print(f"---> {game_name} session finished with status: {game_exit_status}. Cleaning up... <---")
             if pygame.get_init(): pygame.quit(); print("pygame.quit() called.")
             else: print("Pygame was not initialized or already quit.")

             # Restore Tkinter (only if game didn't crash catastrophically)
             if game_exit_status in [GAME_QUIT, GAME_ERROR]:
                 self._restore_tkinter_window()
                 # Reset navigation to subject buttons
                 self.current_window_buttons = self.subject_buttons
                 self.current_index = 0
                 self.button_stack = []
                 if self.current_window_buttons:
                     self.highlight_button(0)
             else: # Should not happen with current logic, but handle defensively
                 print(f"Warning: Unexpected game exit status '{game_exit_status}'. Restoring Tkinter.")
                 self._restore_tkinter_window()

# --- Main Execution Block ---
def open_gaming_window():
    print("Starting STIMO Application...")
    root = None
    try:
        print("Initializing Tkinter root...")
        root = tk.Tk()
        root.title("Game Mode")  # ✅ This line makes window restorable/minimizable by title
        print("Creating GameMode...")
        app = GameMode(root)


        print("Starting Tkinter main loop...")
        root.mainloop()
        print("Tkinter main loop finished.")
    except KeyboardInterrupt:
        print("\nApplication interrupted (Ctrl+C).")
    except Exception as e:
        print("\n--- FATAL ERROR in main application ---")
        traceback.print_exc()
        try:
            err_root = tk.Tk()
            err_root.withdraw()
            messagebox.showerror("Fatal Error", f"Critical error:\n{e}\nApp will exit.", parent=err_root)
            err_root.destroy()
        except:
            pass
    finally:
        print("\nCleaning up and returning to launcher...")
        if pygame.get_init():
            pygame.quit()
            print("Final pygame.quit() called.")
        print("Game Mode closed. Returning control to launcher.")


if __name__ == "__main__":
    open_gaming_window()  # Or whatever your function is called