import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json

# Application Constants
SETTINGS_FILE = "settings.json"
DEFAULT_EMPTY_FILE_NAME = "A_BLKSAVE" # New constant for empty file name fallback

class BLKGeneratorApp:
    """
    Tkinter application for generating BLK files.
    Combines a template with user-provided crosshair code and saves it.
    """
    def __init__(self, master):
        """
        Initializes the BLKGeneratorApp.

        Args:
            master (tk.Tk): The Tkinter root window.
        """
        self.master = master
        master.title("BLK Generator")
        master.geometry("400x550")

        # Load settings upon application startup
        self.settings = self._load_settings()

        # Tkinter variables for checkbox states
        self.include_ranges = tk.BooleanVar(value=True)
        self.vert_var = tk.BooleanVar(value=True)
        self.horz_var = tk.BooleanVar(value=True)

        # Create UI widgets
        self._create_widgets()
        # Update the path label based on loaded settings
        self._update_path_label()

    def _create_widgets(self):
        """
        Creates all UI widgets for the application.
        """
        # Application Title
        tk.Label(self.master, text="BLK Generator", font=("Arial", 24)).pack(pady=10)

        # File Name field
        tk.Label(self.master, text="File name:").pack()
        self.file_name_entry = tk.Entry(self.master, width=40)
        # No default insert, so it starts empty
        self.file_name_entry.pack(pady=5)

        # Frame for save folder selection
        path_frame = tk.Frame(self.master)
        path_frame.pack()
        tk.Button(path_frame, text="Choose save folder", command=self._browse_folder).pack(side=tk.LEFT)
        self.path_label = tk.Label(path_frame, text="", font=("Arial", 12)) # Reduced font size for better readability
        self.path_label.pack(side=tk.LEFT, padx=5)

        # Input/display area for crosshair code
        self.input_text = scrolledtext.ScrolledText(self.master, width=45, height=10, wrap=tk.WORD)
        self.input_text.pack(pady=10)

        # Button to load text from a .txt file
        tk.Button(self.master, text="Load text from .txt", command=self._browse_txt_file).pack(pady=5)

        # "Start" button to generate the BLK file
        tk.Button(self.master, text="Start", bg="black", fg="white", font=("Arial", 15), width=20, command=self._generate_blk).pack(pady=20)

        # Checkboxes for controlling central lines
        tk.Checkbutton(self.master, text="drawCentralLineVert", variable=self.vert_var).pack()
        tk.Checkbutton(self.master, text="drawCentralLineHorz", variable=self.horz_var).pack()

        # Checkbox to include horizontal range lines
        tk.Checkbutton(self.master, text="Include horizontal range lines", variable=self.include_ranges).pack(pady=(5, 0))

    def _load_settings(self):
        """
        Loads application settings from the SETTINGS_FILE.

        Returns:
            dict: A dictionary with loaded settings or an empty dictionary if the file is not found/corrupted.
        """
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Could not read settings from {SETTINGS_FILE}. File might be corrupted.")
                return {}
            except IOError as e:
                messagebox.showerror("Error", f"Error loading settings from {SETTINGS_FILE}: {e}")
                return {}
        return {}

    def _save_settings(self):
        """
        Saves the current application settings to the SETTINGS_FILE.
        """
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4) # Added indentation for JSON readability
        except IOError as e:
            messagebox.showerror("Error", f"Could not save settings to {SETTINGS_FILE}: {e}")

    def _update_path_label(self):
        """
        Updates the path label to display the selected save folder.
        """
        save_path = self.settings.get("save_path")
        if save_path:
            # Display only the folder name for brevity
            self.path_label.config(text=f"Selected: {os.path.basename(save_path)}", fg="green")
        else:
            self.path_label.config(text="No folder selected", fg="red")

    def _browse_folder(self):
        """
        Opens a dialog to choose a save folder.
        Updates settings and the path label.
        """
        folder = filedialog.askdirectory()
        if folder:
            self.settings["save_path"] = folder
            self._save_settings()
            self._update_path_label()

    def _browse_txt_file(self):
        """
        Opens a dialog to choose a .txt file and loads its content
        into the input text area.
        """
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    self.input_text.delete("1.0", tk.END) # Clear current text
                    self.input_text.insert(tk.END, file.read()) # Insert file content
            except IOError as e:
                messagebox.showerror("Error", f"Could not read file {path}: {e}")

    def _load_template(self):
        """
        Generates the main part of the BLK file content based on current settings.

        Returns:
            str: The generated BLK string template.
        """
        # Block of horizontal range lines
        RANGE_BLOCK = """  range:p2=-32, 32
  range:p2=-28, 0
  range:p2=-24, 24
  range:p2=-20, 0
  range:p2=-16, 16
  range:p2=-12, 0
  range:p2=-8, 8
  range:p2=-4, 0
  range:p2=4, 0
  range:p2=8, 8
  range:p2=12, 0
  range:p2=16, 16
  range:p2=20, 0
  range:p2=24, 24
  range:p2=28, 0
  range:p2=32, 32"""

        template_parts = [
            "crosshairHorVertSize:p2=3, 2",
            "rangefinderProgressBarColor1:c=0, 255, 0, 64",
            "rangefinderProgressBarColor2:c=255, 255, 255, 64",
            "rangefinderTextScale:r=0.7",
            "rangefinderUseThousandth:b=no",
            "rangefinderVerticalOffset:r=0.1",
            "rangefinderHorizontalOffset:r=5",
            "detectAllyTextScale:r=0.7",
            "detectAllyOffset:p2=4, 0.05",
            "fontSizeMult:r=1",
            "lineSizeMult:r=1",
            # Using f-strings for conditional inclusion/exclusion of lines
            f"drawCentralLineVert:b={'yes' if self.vert_var.get() else 'no'}",
            f"drawCentralLineHorz:b={'yes' if self.horz_var.get() else 'no'}",
            "drawSightMask:b=yes",
            "useSmoothEdge:b=yes",
            "crosshairColor:c=0, 0, 0, 0",
            "crosshairLightColor:c=0, 0, 0, 0",
            "crosshairDistHorSizeMain:p2=0.03, 0.02",
            "crosshairDistHorSizeAdditional:p2=0.005, 0.003",
            "distanceCorrectionPos:p2=-0.26, -0.05",
            "drawDistanceCorrection:b=yes",
            "", # New line for separation

            "crosshair_distances{",
            "  distance:p3=200, 0, 0",
            "  distance:p3=400, 4, 0",
            "  distance:p3=600, 0, 0",
            "  distance:p3=800, 8, 0",
            "  distance:p3=1000, 0, 0",
            "  distance:p3=1200, 12, 0",
            "  distance:p3=1400, 0, 0",
            "  distance:p3=1600, 16, 0",
            "  distance:p3=1800, 0, 0",
            "  distance:p3=2000, 20, 0",
            "  distance:p3=2200, 0, 0",
            "  distance:p3=2400, 24, 0",
            "  distance:p3=2600, 0, 0",
            "  distance:p3=2800, 28, 0",
            "  distance:p3=3000, 0, 0",
            "  distance:p3=3200, 32, 0",
            "  distance:p3=3400, 0, 0",
            "  distance:p3=3600, 36, 0",
            "  distance:p3=3800, 0, 0",
            "  distance:p3=4000, 40, 0",
            "  distance:p3=4200, 0, 0",
            "  distance:p3=4400, 44, 0",
            "  distance:p3=4600, 0, 0",
            "  distance:p3=4800, 48, 0",
            "  distance:p3=5000, 0, 0",
            "  distance:p3=5200, 52, 0",
            "  distance:p3=5400, 0, 0",
            "  distance:p3=5600, 56, 0",
            "  distance:p3=5800, 0, 0",
            "  distance:p3=6000, 60, 0",
            "}",
            "", # New line for separation

            "crosshair_hor_ranges{"
        ]
        if self.include_ranges.get():
            template_parts.append(RANGE_BLOCK)
        template_parts.append("}")
        template_parts.append("") # New line for separation

        template_parts.append("matchExpClass{")
        template_parts.append("  exp_tank:b = yes")
        template_parts.append("  exp_heavy_tank:b = yes")
        template_parts.append("  exp_tank_destroyer:b = yes")
        template_parts.append("  exp_SPAA:b = yes")
        template_parts.append("}")

        return "\n".join(template_parts)

    def _combine_template_with_crosshair(self, crosshair_code):
        """
        Combines the generated template with the user-provided crosshair code.

        Args:
            crosshair_code (str): The crosshair code entered by the user.

        Returns:
            str: The complete BLK file content.
        """
        crosshair_code = crosshair_code.strip()
        template_content = self._load_template()

        # Check if the crosshair code already contains "drawLines{...}"
        if crosshair_code.startswith("drawLines{") and crosshair_code.endswith("}"):
            return template_content + "\n" + crosshair_code
        else:
            return template_content + "\n\ndrawLines{\n" + crosshair_code + "\n}"

    def _generate_blk(self):
        """
        Generates and saves the BLK file based on user input and settings.
        """
        # If file_name_entry is empty, use DEFAULT_EMPTY_FILE_NAME
        file_name = self.file_name_entry.get().strip() or DEFAULT_EMPTY_FILE_NAME
        save_path = self.settings.get("save_path")

        if not save_path:
            messagebox.showerror("Error", "You did not specify a file path.")
            return

        # Full path to the file
        full_path = os.path.join(save_path, file_name + ".blk")
        sight_code = self.input_text.get("1.0", tk.END) # Get all text from ScrolledText
        final_content = self._combine_template_with_crosshair(sight_code)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                # Ensure there is a single newline at the end of the file
                f.write(final_content.strip() + "\n")
            messagebox.showinfo("Done", f"Saved to:\n{full_path}")
        except IOError as e:
            messagebox.showerror("Error", f"Could not save file to {full_path}: {e}")

# Entry point for the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BLKGeneratorApp(root)
    root.mainloop()
