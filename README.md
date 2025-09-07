# Wallpaper Slideshow

This project is a wallpaper slideshow application with a GUI controller.

## Dependencies

This project requires the following dependencies:

*   Python 3
*   PySide6

## Installation

1.  **Install Python 3:**
    If you don't have Python 3 installed, you can install it using your distribution's package manager.

2.  **Install PySide6:**
    Use `yay` to install the `pyside6` package from the Arch User Repository (AUR):
    ```bash
    yay -S pyside6
    ```

## Usage

To run the application, execute the `gui.py` script:

```bash
python gui.py
```

The GUI will allow you to control the wallpaper slideshow.

## Hyprland Configuration

To use this application with Hyprland, you need to configure it to autostart the slideshow script and set a keybinding to launch the GUI.

1.  **Autostart the slideshow script:**

    Add the following line to your `hyprland.conf` file, replacing `path/to/your` with the actual path to the `sw.py` script:

    ```
    exec-once = python path/to/your/sw.py
    ```

2.  **Set a keybinding for the GUI:**

    Add the following line to your `hyprland.conf` file, replacing `path/to/your` with the actual path to the `gui.py` script:

    ```
    bind = Super+Shift, W, exec, python path/to/your/gui.py
    ```
