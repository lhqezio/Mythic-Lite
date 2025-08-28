"""
Cross-platform input handling for Mythic-Lite.
Provides Windows-safe input handling with fallbacks for other platforms.
"""

import sys
import os
from typing import Optional

# Conditionally import Windows-specific modules
try:
    if os.name == 'nt':  # Windows
        import msvcrt
        WINDOWS_AVAILABLE = True
    else:
        WINDOWS_AVAILABLE = False
except ImportError:
    WINDOWS_AVAILABLE = False


class WindowsInputHandler:
    """Cross-platform input handler with Windows optimizations."""
    
    def __init__(self):
        self.is_windows = os.name == 'nt' and WINDOWS_AVAILABLE
        self.use_fallback = False
    
    def get_input(self, prompt: str = "") -> str:
        """Get user input safely."""
        if self.is_windows and not self.use_fallback:
            try:
                return self._windows_input(prompt)
            except Exception as e:
                print(f"⚠️  Windows input failed, falling back to standard input: {e}")
                self.use_fallback = True
                return input(prompt)
        else:
            return input(prompt)
    
    def _windows_input(self, prompt: str = "") -> str:
        """Windows-specific input handling using msvcrt."""
        if not WINDOWS_AVAILABLE:
            return input(prompt)
            
        if prompt:
            sys.stdout.write(prompt)
            sys.stdout.flush()
        
        chars = []
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Handle Enter key
                if char == b'\r':
                    print()  # New line
                    break
                
                # Handle Backspace
                elif char == b'\x08':
                    if chars:
                        chars.pop()
                        # Clear last character from console
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                
                # Handle Ctrl+C
                elif char == b'\x03':
                    raise KeyboardInterrupt
                
                # Handle printable characters
                elif char >= b' ' and char <= b'~':
                    chars.append(char.decode('utf-8'))
                    sys.stdout.write(char.decode('utf-8'))
                    sys.stdout.flush()
                
                # Handle special keys (ignore)
                elif char.startswith(b'\xe0'):
                    msvcrt.getch()  # Skip the second byte of special keys
        
        return ''.join(chars)
    
    def get_choice(self, prompt: str = "", valid_choices: Optional[list] = None) -> str:
        """Get a single character choice safely."""
        if self.is_windows and not self.use_fallback:
            try:
                return self._windows_choice(prompt, valid_choices)
            except Exception as e:
                print(f"⚠️  Windows choice input failed, falling back to standard input: {e}")
                self.use_fallback = True
                return self._standard_choice(prompt, valid_choices)
        else:
            return self._standard_choice(prompt, valid_choices)
    
    def _standard_choice(self, prompt: str = "", valid_choices: Optional[list] = None) -> str:
        """Standard choice input with validation."""
        while True:
            choice = input(prompt).strip().lower()
            if valid_choices and choice not in valid_choices:
                print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")
                continue
            return choice
    
    def _windows_choice(self, prompt: str = "", valid_choices: Optional[list] = None) -> str:
        """Windows-specific single character input."""
        if not WINDOWS_AVAILABLE:
            return self._standard_choice(prompt, valid_choices)
            
        if prompt:
            print(prompt, end='', flush=True)
        
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Handle Enter key
                if char == b'\r':
                    print()
                    break
                
                # Handle Ctrl+C
                elif char == b'\x03':
                    raise KeyboardInterrupt
                
                # Handle printable characters
                elif char >= b' ' and char <= b'~':
                    choice = char.decode('utf-8').lower()
                    if valid_choices and choice not in valid_choices:
                        print(f"\nInvalid choice '{choice}'. Please enter one of: {', '.join(valid_choices)}")
                        return self._standard_choice(prompt, valid_choices)
                    print(choice)
                    return choice
                
                # Handle special keys (ignore)
                elif char.startswith(b'\xe0'):
                    msvcrt.getch()  # Skip the second byte of special keys


# Convenience functions
def safe_input(prompt: str = "") -> str:
    """Get user input safely across platforms."""
    handler = WindowsInputHandler()
    return handler.get_input(prompt)


def safe_choice(prompt: str = "", valid_choices: Optional[list] = None) -> str:
    """Get a single character choice safely across platforms."""
    handler = WindowsInputHandler()
    return handler.get_choice(prompt, valid_choices)


# Backward compatibility
WindowsInput = WindowsInputHandler
