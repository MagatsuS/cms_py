#!/usr/bin/env python3
"""
Modern GUI for CMS_PY Digital Signage Player
"""
import os
import sys
import platform
import subprocess
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
import customtkinter as ctk

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SetupDialog(ctk.CTkToplevel):
    """Modern setup dialog for first-time configuration"""

    def __init__(self, parent):
        super().__init__(parent)

        self.player_url = None
        self.save_config = False

        # Configure window
        self.title("CMS_PY - First Time Setup")
        self.geometry("600x400")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f'600x400+{x}+{y}')

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header = ctk.CTkLabel(
            container,
            text="🖥️  FIRST TIME SETUP",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            container,
            text="CMS_PY Digital Signage Player",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))

        # Info frame
        info_frame = ctk.CTkFrame(container, fg_color=("gray85", "gray20"))
        info_frame.pack(fill="x", pady=(0, 20))

        info_text = ctk.CTkLabel(
            info_frame,
            text="Player URL not configured in .env file.\nPlease enter your player URL from cms_dupe:",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_text.pack(padx=15, pady=15)

        # URL Input
        url_label = ctk.CTkLabel(
            container,
            text="Player URL:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        url_label.pack(fill="x", pady=(0, 5))

        self.url_entry = ctk.CTkEntry(
            container,
            placeholder_text="http://127.0.0.1:8000/player/PLAYER-ABC123",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", pady=(0, 10))
        self.url_entry.focus()

        # Example text
        example = ctk.CTkLabel(
            container,
            text="Example: http://127.0.0.1:8000/player/PLAYER-ABC123",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        example.pack(anchor="w", pady=(0, 20))

        # Save checkbox
        self.save_var = ctk.BooleanVar(value=True)
        save_checkbox = ctk.CTkCheckBox(
            container,
            text="Save URL to .env file",
            variable=self.save_var,
            font=ctk.CTkFont(size=12)
        )
        save_checkbox.pack(anchor="w", pady=(0, 30))

        # Buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x")

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=120,
            height=35,
            fg_color="gray40",
            hover_color="gray30"
        )
        cancel_btn.pack(side="left")

        submit_btn = ctk.CTkButton(
            button_frame,
            text="Continue",
            command=self.submit,
            width=120,
            height=35
        )
        submit_btn.pack(side="right")

        # Bind Enter key
        self.url_entry.bind("<Return>", lambda e: self.submit())

    def submit(self):
        """Handle submit button"""
        url = self.url_entry.get().strip()

        if not url:
            self.show_error("Please enter a player URL")
            return

        if not url.startswith('http'):
            self.show_error("Invalid URL format.\nMust start with http:// or https://")
            return

        self.player_url = url
        self.save_config = self.save_var.get()
        self.destroy()

    def cancel(self):
        """Handle cancel button"""
        self.player_url = None
        self.destroy()

    def show_error(self, message):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("350x150")
        error_dialog.resizable(False, False)

        # Center on parent
        error_dialog.transient(self)
        error_dialog.grab_set()

        x = self.winfo_x() + (self.winfo_width() // 2) - 175
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        error_dialog.geometry(f'350x150+{x}+{y}')

        container = ctk.CTkFrame(error_dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(
            container,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=300
        )
        label.pack(expand=True)

        btn = ctk.CTkButton(
            container,
            text="OK",
            command=error_dialog.destroy,
            width=100
        )
        btn.pack()


class PlayerLauncher(ctk.CTk):
    """Main player launcher window"""

    def __init__(self):
        super().__init__()

        self.player_url = None

        # Configure window
        self.title("CMS_PY Digital Signage Player")
        self.geometry("700x500")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f'700x500+{x}+{y}')

        self.create_widgets()
        self.check_configuration()

    def create_widgets(self):
        """Create main window widgets"""

        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)

        # Header
        header = ctk.CTkLabel(
            container,
            text="🖥️  CMS_PY",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        header.pack(pady=(0, 5))

        subtitle = ctk.CTkLabel(
            container,
            text="Browser-Based Digital Signage Player",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 40))

        # Info frame
        self.info_frame = ctk.CTkFrame(container, fg_color=("gray85", "gray20"))
        self.info_frame.pack(fill="both", expand=True, pady=(0, 30))

        info_container = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        info_container.pack(fill="both", expand=True, padx=30, pady=30)

        self.url_label = ctk.CTkLabel(
            info_container,
            text="Player URL:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.url_label.pack(fill="x", pady=(0, 10))

        self.url_display = ctk.CTkTextbox(
            info_container,
            height=60,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.url_display.pack(fill="x", pady=(0, 20))
        self.url_display.configure(state="disabled")

        info_text = ctk.CTkLabel(
            info_container,
            text="This will open the player in fullscreen kiosk mode.\nPress F11 or Alt+F4 to exit fullscreen.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info_text.pack(fill="x")

        # Buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x")

        self.config_btn = ctk.CTkButton(
            button_frame,
            text="⚙️  Configure",
            command=self.show_setup,
            width=140,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        self.config_btn.pack(side="left")

        self.launch_btn = ctk.CTkButton(
            button_frame,
            text="🚀  Launch Player",
            command=self.launch_player,
            width=140,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.launch_btn.pack(side="right")

    def check_configuration(self):
        """Check if player URL is configured"""
        self.player_url = os.getenv('PLAYER_URL', '')

        if not self.player_url or self.player_url == 'http://127.0.0.1:8000/player/PLAYER-XXXXXXXX':
            # Show setup dialog
            self.after(100, self.show_setup)
        else:
            self.update_url_display()

    def update_url_display(self):
        """Update URL display"""
        self.url_display.configure(state="normal")
        self.url_display.delete("1.0", "end")
        self.url_display.insert("1.0", self.player_url if self.player_url else "Not configured")
        self.url_display.configure(state="disabled")

        # Enable/disable launch button
        self.launch_btn.configure(state="normal" if self.player_url else "disabled")

    def show_setup(self):
        """Show setup dialog"""
        dialog = SetupDialog(self)
        self.wait_window(dialog)

        if dialog.player_url:
            self.player_url = dialog.player_url

            # Save to .env if requested
            if dialog.save_config:
                self.save_to_env(self.player_url)

            self.update_url_display()

    def save_to_env(self, url):
        """Save player URL to .env file"""
        try:
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace PLAYER_URL line
                if 'PLAYER_URL=' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('PLAYER_URL='):
                            lines[i] = f'PLAYER_URL={url}'
                            break
                    content = '\n'.join(lines)
                else:
                    content += f'\nPLAYER_URL={url}\n'

                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info("Player URL saved to .env file")
            else:
                logger.warning(".env file not found")
        except Exception as e:
            logger.error(f"Failed to save player URL: {str(e)}")

    def launch_player(self):
        """Launch the player in browser"""
        if not self.player_url:
            return

        logger.info(f"Launching player: {self.player_url}")

        # Import the browser opening function from original file
        from player_browser import open_browser_kiosk

        success = open_browser_kiosk(self.player_url)

        if success:
            logger.info("Player started successfully!")

            # Schedule F11 press after delay (non-blocking)
            if HAS_PYAUTOGUI:
                def press_f11():
                    logger.info("Pressing F11 to enter fullscreen...")
                    try:
                        pyautogui.press('f11')
                        logger.info("Fullscreen activated!")
                    except Exception as e:
                        logger.error(f"Failed to press F11: {e}")

                logger.info("Will press F11 in 3 seconds...")
                self.after(3000, press_f11)

            # Minimize this window after delay
            self.after(3500, self.iconify)
        else:
            logger.error("Failed to start player")


def main():
    """Main entry point"""
    # Check if already configured
    player_url = os.getenv('PLAYER_URL', '')

    if player_url and player_url != 'http://127.0.0.1:8000/player/PLAYER-XXXXXXXX':
        # Already configured - launch directly
        logger.info(f"Player URL configured: {player_url}")
        logger.info("Launching player in fullscreen...")

        from player_browser import open_browser_kiosk
        success = open_browser_kiosk(player_url)

        if success:
            logger.info("Player started successfully!")

            # Auto-press F11 to ensure fullscreen
            if HAS_PYAUTOGUI:
                logger.info("Waiting 3 seconds for browser to load...")
                time.sleep(3)
                logger.info("Pressing F11 to enter fullscreen...")
                try:
                    pyautogui.press('f11')
                    logger.info("Fullscreen activated!")
                except Exception as e:
                    logger.error(f"Failed to press F11: {e}")
        else:
            logger.error("Failed to start player")
    else:
        # Not configured - show GUI
        app = PlayerLauncher()
        app.mainloop()


if __name__ == '__main__':
    main()
