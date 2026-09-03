import tkinter as tk
from tkinter import Menu


# Close the main application window and end the Tkinter program.
def click_close():
    win.quit()       # Stop the Tkinter event loop.
    win.destroy()    # Destroy the main window.


# ------------------------------------------------------------
# Main application window
# ------------------------------------------------------------

win = tk.Tk()  # Create the main Tkinter window.
win.attributes('-fullscreen', True)  # Open the window in fullscreen mode.

# Create the menu bar that will appear at the top of the window.
menu_bar = Menu(win)

# Set the initial window size and title.
# Note: the fullscreen setting above takes precedence while fullscreen is active.
win.geometry('500x500')
win.title('Gui')
win.resizable(False, False)  # Prevent the user from resizing the main window.


# ------------------------------------------------------------
# Create menu tabs
# ------------------------------------------------------------

file_tab = Menu(menu_bar)
insert_tab = Menu(menu_bar)
Design_tab = Menu(menu_bar)
view_tab = Menu(menu_bar)
references_tab = Menu(menu_bar)
help_tab = Menu(menu_bar)

# Add the tabs to the main menu bar.
menu_bar.add_cascade(label='File', menu=file_tab)
menu_bar.add_cascade(label='Insert', menu=insert_tab)
menu_bar.add_cascade(label='Design', menu=Design_tab)
menu_bar.add_cascade(label='References', menu=references_tab)
menu_bar.add_cascade(label='View', menu=view_tab)
menu_bar.add_cascade(label='Help', menu=help_tab)

# Attach the menu bar to the main window.
win.config(menu=menu_bar)


# ------------------------------------------------------------
# Simple Calculator window
# ------------------------------------------------------------

def cal():
    # Create a child window that sits on top of the main window.
    calculator = tk.Toplevel(win)
    calculator.title('Simple Calculator')
    calculator.geometry('300x300+100+100')

    # Add a title label to the calculator window.
    label1 = tk.Label(calculator, text='Simple Calculator')
    label1.grid(row=0, column=1, padx=5, pady=5)

    # Create a frame to group the first input area.
    frame1 = tk.Frame(calculator, bg='green')
    frame1.grid(row=1, column=0)

    # Label describing the first input field.
    label2 = tk.Label(frame1, text='Number')
    label2.grid(row=0, column=0, padx=5, pady=5)

    # Entry widget where the user enters an arithmetic expression.
    entry1 = tk.Entry(frame1)
    entry1.grid(row=0, column=1, padx=5, pady=5)

    # Entry widget used to display the calculated result.
    entry2 = tk.Entry(calculator)
    entry2.grid(row=3, column=1, padx=5, pady=5)

    # Calculate the expression entered by the user.
    def estimate():
        a = entry1.get()       # Read the expression from the input box.
        b = eval(a)            # Evaluate the arithmetic expression.
        entry2.delete(0, tk.END)  # Clear any previous result.
        entry2.insert(0, b)       # Display the new result.

    # Button that runs estimate() when clicked.
    button = tk.Button(calculator, text='Calculate', command=estimate)
    button.grid(row=2, column=1, padx=5, pady=5)


# ------------------------------------------------------------
# Casio-style Calculator window
# ------------------------------------------------------------

def calc():
    # Create another child window for the button-based calculator.
    calculator = tk.Toplevel(win)
    calculator.title('Casio Calculator')
    calculator.attributes('-alpha', 0.7)  # Make the calculator slightly transparent.

    # Display box where numbers and operators appear.
    # calculator.geometry('300x300+100+100')  # Optional fixed window position/size.
    display = tk.Entry(calculator)
    display.grid(row=0, column=0, padx=5, pady=5)

    # Insert a number or operator into the display.
    def click(number):
        display.insert(tk.END, number)

    # Create a labelled frame to hold the keypad buttons.
    frame2 = tk.LabelFrame(calculator, text='Keypad')
    frame2.grid(row=1, column=0)

    # Number buttons 1-9.
    button1 = tk.Button(frame2, text='1', width=4, command=lambda: click(1))
    button1.grid(row=1, column=0, padx=5, pady=5)

    button2 = tk.Button(frame2, text='2', width=4, command=lambda: click(2))
    button2.grid(row=1, column=1, padx=5, pady=5)

    button3 = tk.Button(frame2, text='3', width=4, command=lambda: click(3))
    button3.grid(row=1, column=2, padx=5, pady=5)

    button4 = tk.Button(frame2, text='4', width=4, command=lambda: click(4))
    button4.grid(row=1, column=3, padx=5, pady=5)

    button5 = tk.Button(frame2, text='5', width=4, command=lambda: click(5))
    button5.grid(row=2, column=0, padx=5, pady=5)

    button6 = tk.Button(frame2, text='6', width=4, command=lambda: click(6))
    button6.grid(row=2, column=1, padx=5, pady=5)

    button7 = tk.Button(frame2, text='7', width=4, command=lambda: click(7))
    button7.grid(row=2, column=2, padx=5, pady=5)

    button8 = tk.Button(frame2, text='8', width=4, command=lambda: click(8))
    button8.grid(row=2, column=3, padx=5, pady=5)

    button9 = tk.Button(frame2, text='9', width=4, command=lambda: click(9))
    button9.grid(row=3, column=0, padx=5, pady=5)

    button0 = tk.Button(frame2, text='0', width=4, command=lambda: click(0))
    button0.grid(row=3, column=1, padx=5, pady=5)

    # Arithmetic operator buttons.
    buttonplus = tk.Button(frame2, text='+', width=4, command=lambda: click('+'))
    buttonplus.grid(row=3, column=2, padx=5, pady=5)

    buttonminus = tk.Button(frame2, text='-', width=4, command=lambda: click('-'))
    buttonminus.grid(row=3, column=3, padx=5, pady=5)

    buttonslash = tk.Button(frame2, text='/', width=4, command=lambda: click('/'))
    buttonslash.grid(row=4, column=0, padx=5, pady=5)

    buttonstar = tk.Button(frame2, text='*', width=4, command=lambda: click('*'))
    buttonstar.grid(row=4, column=1, padx=5, pady=5)

    # Evaluate the complete expression currently shown in the display.
    def equal():
        a = display.get()           # Read the arithmetic expression.
        b = eval(a)                 # Evaluate the expression.
        display.delete(0, tk.END)   # Clear the display.
        display.insert(0, b)        # Show the calculated result.

    # Equals button.
    buttonequal_to = tk.Button(frame2, text='=', width=4, command=equal)
    buttonequal_to.grid(row=4, column=2, padx=5, pady=5)

    # Clear everything currently shown in the display.
    def clear():
        display.delete(0, tk.END)

    # Clear button.
    buttonclear = tk.Button(frame2, text='C', width=4, command=clear)
    buttonclear.grid(row=4, column=3, padx=5, pady=5)


# ------------------------------------------------------------
# File menu commands
# ------------------------------------------------------------

file_tab.add_command(label='New', command=calc)  # Open the Casio-style calculator.
file_tab.add_command(label='Open')               # Placeholder menu item.
file_tab.add_command(label='Save as')             # Placeholder menu item.
file_tab.add_command(label='Save')                # Placeholder menu item.
file_tab.add_command(label='Close', command=click_close)  # Close the application.

# Help menu items (currently placeholders).
help_tab.add_command(label='Tutorial')
help_tab.add_command(label='About')


# Start Tkinter's event loop so the window remains open and responds to user actions.
win.mainloop()
