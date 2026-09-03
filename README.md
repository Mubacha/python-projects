# Python Projects — Simple Tkinter Calculator

## Overview

This repository contains a beginner Python GUI project built with **Tkinter**. The project creates a main application window with a menu bar and includes a simple calculator and a Casio-style button-based calculator.

## Project

### Simple Calculator GUI

The program demonstrates how to:

- Create a desktop GUI with Tkinter
- Create and configure the main application window
- Build menu bars and menu items
- Open child windows with `Toplevel`
- Use `Label`, `Entry`, `Button`, `Frame`, and `LabelFrame` widgets
- Arrange widgets using the `grid()` geometry manager
- Connect buttons to Python functions using `command`
- Use `lambda` to pass values to callback functions
- Read from and write to `Entry` widgets
- Clear and update calculator displays
- Run a Tkinter application with `mainloop()`

## Files

- `simple_calculator.py` — commented source code for the Tkinter calculator application.

## Running the project

Make sure Python is installed. Tkinter is included with most standard Python installations.

Run:

```bash
python simple_calculator.py
```

## Notes

The calculator code uses Python's `eval()` function to evaluate arithmetic expressions entered by the user. This is convenient for a beginner project, but `eval()` should **not** be used with untrusted input in production applications because it can execute arbitrary Python code.

The main window is configured for fullscreen mode, while a `geometry()` setting is also present as part of the original project structure. The child calculator windows provide the practical calculator interfaces.

## Learning goal

This project is intended as a practical exercise in Python GUI programming, with emphasis on understanding how Tkinter widgets, functions, callbacks, and layout management work together.
