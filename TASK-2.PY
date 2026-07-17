#!/usr/bin/env python3
"""
Calculator Application (GUI)
============================

A modern, desktop calculator built with Python's Tkinter library,
following Object-Oriented Programming principles.

Author : Senior Python Engineer
Project: CodSoft Python Internship - Task (Calculator Application)

Features:
    - Basic arithmetic operations: addition, subtraction,
      multiplication, division, and modulus.
    - Decimal number support.
    - Full mouse (button) and keyboard input support.
    - Clear (C) and Delete (⌫) functionality.
    - Graceful error handling (e.g., division by zero, invalid
      expressions) without crashing the application.
    - Modern, responsive, non-resizable UI centered on screen.

This module is intentionally kept in a single file for simplicity of
submission, but functionality is cleanly separated into classes:
    - CalculatorEngine: Handles expression validation and evaluation.
    - CalculatorApp: Handles the Tkinter GUI, layout, and event
      bindings.
"""

import re
import tkinter as tk
from tkinter import font as tkfont


# --------------------------------------------------------------------------- #
#  CALCULATION ENGINE
# --------------------------------------------------------------------------- #
class CalculatorEngine:
    """
    Handles the core arithmetic logic of the calculator.

    This class is responsible for validating user-entered expressions
    and safely evaluating them, without relying on unrestricted use of
    Python's built-in `eval`.
    """

    # Only digits, whitespace, decimal points, parentheses, and the
    # four basic arithmetic operators (+, -, *, /) and modulus (%)
    # are permitted in a validated expression.
    _ALLOWED_EXPRESSION_PATTERN = re.compile(r"^[0-9+\-*/%.() ]+$")

    @staticmethod
    def sanitize_display_symbols(expression: str) -> str:
        """
        Convert calculator display symbols (×, ÷) into Python-evaluable
        operators (*, /).

        Args:
            expression (str): The raw expression shown on the display.

        Returns:
            str: A Python-compatible arithmetic expression.
        """
        return expression.replace("×", "*").replace("÷", "/")

    def evaluate(self, expression: str) -> str:
        """
        Safely evaluate an arithmetic expression and return the result
        as a string.

        Args:
            expression (str): The expression to evaluate (may contain
                display symbols such as × and ÷).

        Returns:
            str: The computed result, formatted as a string.

        Raises:
            ValueError: If the expression is empty, contains invalid
                characters, or is otherwise malformed.
            ZeroDivisionError: If the expression attempts to divide or
                take a modulus by zero.
        """
        if not expression:
            raise ValueError("Nothing to calculate.")

        clean_expression = self.sanitize_display_symbols(expression)

        if not self._ALLOWED_EXPRESSION_PATTERN.match(clean_expression):
            raise ValueError("Expression contains invalid characters.")

        try:
            # A restricted namespace (no builtins) is used to prevent
            # execution of arbitrary code through eval().
            result = eval(clean_expression, {"__builtins__": {}}, {})
        except ZeroDivisionError:
            raise ZeroDivisionError("Cannot divide by zero.")
        except (SyntaxError, TypeError, NameError):
            raise ValueError("Invalid expression.")

        return self._format_result(result)

    @staticmethod
    def _format_result(result) -> str:
        """
        Format a numeric result for display, trimming unnecessary
        trailing zeros from floating-point numbers.

        Args:
            result: The numeric result of an evaluated expression.

        Returns:
            str: A clean, display-friendly string representation.
        """
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            # Limit to 10 decimal places to avoid floating-point noise.
            return f"{result:.10f}".rstrip("0").rstrip(".")
        return str(result)


# --------------------------------------------------------------------------- #
#  GUI APPLICATION
# --------------------------------------------------------------------------- #
class CalculatorApp:
    """
    Builds and manages the Tkinter-based graphical user interface for
    the calculator, including layout, styling, button/keyboard
    bindings, and interaction with the CalculatorEngine.
    """

    # ---------------------------- Color Palette ---------------------------- #
    COLOR_BACKGROUND = "#1e1e2f"
    COLOR_DISPLAY_BG = "#252537"
    COLOR_DISPLAY_TEXT = "#ffffff"
    COLOR_DIGIT_BTN = "#33334d"
    COLOR_DIGIT_BTN_HOVER = "#44445f"
    COLOR_OPERATOR_BTN = "#ff9f43"
    COLOR_OPERATOR_BTN_HOVER = "#ffb976"
    COLOR_FUNCTION_BTN = "#5f5f7a"
    COLOR_FUNCTION_BTN_HOVER = "#75758f"
    COLOR_EQUALS_BTN = "#00b894"
    COLOR_EQUALS_BTN_HOVER = "#04d6a8"
    COLOR_BTN_TEXT = "#ffffff"

    WINDOW_WIDTH = 360
    WINDOW_HEIGHT = 520

    def __init__(self):
        self.engine = CalculatorEngine()
        self.expression = ""
        self.error_state = False

        self.root = tk.Tk()
        self._configure_window()

        self.display_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        self.button_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")

        self.display_var = tk.StringVar(value="0")

        self._build_display()
        self._build_button_grid()
        self._bind_keyboard_events()

    # ---------------------------- Window Setup ---------------------------- #
    def _configure_window(self) -> None:
        """Configure the main application window: size, title, and position."""
        self.root.title("Calculator")
        self.root.configure(bg=self.COLOR_BACKGROUND)
        self.root.resizable(False, False)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = (screen_width // 2) - (self.WINDOW_WIDTH // 2)
        pos_y = (screen_height // 2) - (self.WINDOW_HEIGHT // 2)

        self.root.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{pos_x}+{pos_y}"
        )

    # ---------------------------- Display Area ---------------------------- #
    def _build_display(self) -> None:
        """Create the responsive display area showing the current expression/result."""
        display_frame = tk.Frame(self.root, bg=self.COLOR_DISPLAY_BG, height=140)
        display_frame.pack(fill="both", padx=15, pady=(20, 10))
        display_frame.pack_propagate(False)

        display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            anchor="e",
            bg=self.COLOR_DISPLAY_BG,
            fg=self.COLOR_DISPLAY_TEXT,
            font=self.display_font,
            padx=15,
        )
        display_label.pack(fill="both", expand=True)

    # ---------------------------- Button Grid ---------------------------- #
    def _build_button_grid(self) -> None:
        """Create and lay out all calculator buttons in a responsive grid."""
        button_frame = tk.Frame(self.root, bg=self.COLOR_BACKGROUND)
        button_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))

        for col in range(4):
            button_frame.columnconfigure(col, weight=1, uniform="col")
        for row in range(5):
            button_frame.rowconfigure(row, weight=1, uniform="row")

        # Layout: (label, row, col, colspan, button_type)
        # button_type -> "digit", "operator", "function", "equals"
        button_layout = [
            ("C", 0, 0, 1, "function"),
            ("⌫", 0, 1, 1, "function"),
            ("%", 0, 2, 1, "operator"),
            ("÷", 0, 3, 1, "operator"),
            ("7", 1, 0, 1, "digit"),
            ("8", 1, 1, 1, "digit"),
            ("9", 1, 2, 1, "digit"),
            ("×", 1, 3, 1, "operator"),
            ("4", 2, 0, 1, "digit"),
            ("5", 2, 1, 1, "digit"),
            ("6", 2, 2, 1, "digit"),
            ("-", 2, 3, 1, "operator"),
            ("1", 3, 0, 1, "digit"),
            ("2", 3, 1, 1, "digit"),
            ("3", 3, 2, 1, "digit"),
            ("+", 3, 3, 1, "operator"),
            ("0", 4, 0, 2, "digit"),
            (".", 4, 2, 1, "digit"),
            ("=", 4, 3, 1, "equals"),
        ]

        for label, row, col, colspan, button_type in button_layout:
            self._create_button(button_frame, label, row, col, colspan, button_type)

    def _create_button(
        self,
        parent: tk.Frame,
        label: str,
        row: int,
        col: int,
        colspan: int,
        button_type: str,
    ) -> None:
        """
        Create a single calculator button with the appropriate style
        and click handler, then place it in the grid.

        Args:
            parent (tk.Frame): The parent frame to attach the button to.
            label (str): The text displayed on the button.
            row (int): Grid row position.
            col (int): Grid column position.
            colspan (int): Number of columns the button should span.
            button_type (str): One of "digit", "operator", "function",
                or "equals" — determines the button's color scheme.
        """
        colors = {
            "digit": (self.COLOR_DIGIT_BTN, self.COLOR_DIGIT_BTN_HOVER),
            "operator": (self.COLOR_OPERATOR_BTN, self.COLOR_OPERATOR_BTN_HOVER),
            "function": (self.COLOR_FUNCTION_BTN, self.COLOR_FUNCTION_BTN_HOVER),
            "equals": (self.COLOR_EQUALS_BTN, self.COLOR_EQUALS_BTN_HOVER),
        }
        bg_color, hover_color = colors[button_type]

        button = tk.Button(
            parent,
            text=label,
            font=self.button_font,
            fg=self.COLOR_BTN_TEXT,
            bg=bg_color,
            activebackground=hover_color,
            activeforeground=self.COLOR_BTN_TEXT,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda: self._on_button_click(label, button_type),
        )
        button.grid(
            row=row, column=col, columnspan=colspan,
            sticky="nsew", padx=6, pady=6, ipady=8,
        )

        # Simple hover effect for a more modern, interactive feel.
        button.bind("<Enter>", lambda _event: button.config(bg=hover_color))
        button.bind("<Leave>", lambda _event: button.config(bg=bg_color))

    # ---------------------------- Event Handling ---------------------------- #
    def _on_button_click(self, label: str, button_type: str) -> None:
        """Dispatch a button click to the appropriate handler based on its type."""
        if button_type == "function" and label == "C":
            self.clear_display()
        elif button_type == "function" and label == "⌫":
            self.delete_last_character()
        elif button_type == "equals":
            self.calculate_result()
        else:
            self.append_to_expression(label)

    def _bind_keyboard_events(self) -> None:
        """Bind keyboard keys to their corresponding calculator actions."""
        digit_and_operator_keys = "0123456789+-*/%.()"
        for key in digit_and_operator_keys:
            self.root.bind(key, self._handle_key_press)

        self.root.bind("<Return>", lambda _event: self.calculate_result())
        self.root.bind("<KP_Enter>", lambda _event: self.calculate_result())
        self.root.bind("<BackSpace>", lambda _event: self.delete_last_character())
        self.root.bind("<Escape>", lambda _event: self.clear_display())

    def _handle_key_press(self, event: tk.Event) -> None:
        """
        Handle a raw keyboard key press by converting it to the
        appropriate display symbol and appending it to the expression.
        """
        key_to_symbol = {"*": "×", "/": "÷"}
        symbol = key_to_symbol.get(event.char, event.char)
        self.append_to_expression(symbol)

    # ---------------------------- Core Actions ---------------------------- #
    def append_to_expression(self, value: str) -> None:
        """
        Append a digit, decimal point, or operator to the current
        expression and refresh the display.

        Args:
            value (str): The character/symbol to append.
        """
        # If the previous calculation resulted in an error, start fresh
        # once the user begins typing a new expression.
        if self.error_state:
            self.expression = ""
            self.error_state = False

        self.expression += value
        self._update_display(self.expression)

    def clear_display(self) -> None:
        """Reset the display and internal expression (Clear/C button)."""
        self.expression = ""
        self.error_state = False
        self._update_display("0")

    def delete_last_character(self) -> None:
        """Remove the last character from the current expression (⌫ button)."""
        if self.error_state:
            # Treat delete the same as clear if currently showing an error.
            self.clear_display()
            return

        self.expression = self.expression[:-1]
        self._update_display(self.expression if self.expression else "0")

    def calculate_result(self) -> None:
        """
        Evaluate the current expression using the CalculatorEngine and
        display the result, or a friendly error message on failure.
        """
        try:
            result = self.engine.evaluate(self.expression)
            self._update_display(result)
            self.expression = result  # Allow chained calculations.
            self.error_state = False
        except ZeroDivisionError:
            self._show_error("Cannot divide by zero")
        except ValueError:
            self._show_error("Invalid expression")
        except Exception:  # Fallback safeguard for unexpected issues.
            self._show_error("Something went wrong")

    # ---------------------------- Display Helpers ---------------------------- #
    def _update_display(self, text: str) -> None:
        """Update the display label with the given text."""
        self.display_var.set(text if text else "0")

    def _show_error(self, message: str) -> None:
        """Display an error message on screen and reset internal state."""
        self.display_var.set(message)
        self.expression = ""
        self.error_state = True

    # ---------------------------- Runner ---------------------------- #
    def run(self) -> None:
        """Start the Tkinter main event loop."""
        self.root.mainloop()


# --------------------------------------------------------------------------- #
#  ENTRY POINT
# --------------------------------------------------------------------------- #
def main() -> None:
    """Application entry point."""
    app = CalculatorApp()
    app.run()


if __name__ == "__main__":
    main()