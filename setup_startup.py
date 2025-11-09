#!/usr/bin/env python3
"""
FileDog Startup Integration Script
Sets up FileDog to start automatically with the system
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_current_dir():
    """Get the current FileDog directory"""
    return Path(__file__).parent.absolute()

def create_windows_startup():
    """Create Windows startup entry"""
    try:
        import winreg
        
        # Get paths
        filedog_dir = get_current_dir()
        python_exe = sys.executable
        filedog_script = filedog_dir / "filedog.py"
        
        # Create the command
        command = f'"{python_exe}" "{filedog_script}" tray'
        
        # Registry key for startup programs
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Open registry key
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "FileDog", 0, winreg.REG_SZ, command)
        
        print("✅ FileDog added to Windows startup")
        print(f"   Command: {command}")
        return True
        
    except ImportError:
        print("❌ winreg module not available")
        return False
    except Exception as e:
        print(f"❌ Error setting up Windows startup: {e}")
        return False

def create_macos_startup():
    """Create macOS startup entry"""
    try:
        # Get paths
        filedog_dir = get_current_dir()
        python_exe = sys.executable
        filedog_script = filedog_dir / "filedog.py"
        
        # Create LaunchAgent directory
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        launch_agents_dir.mkdir(exist_ok=True)
        
        # Create plist content
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.filedog.organizer</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{filedog_script}</string>
        <string>tray</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>{filedog_dir}</string>
</dict>
</plist>"""
        
        # Write plist file
        plist_file = launch_agents_dir / "com.filedog.organizer.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        # Load the launch agent
        subprocess.run(['launchctl', 'load', str(plist_file)], check=True)
        
        print("✅ FileDog added to macOS startup")
        print(f"   LaunchAgent: {plist_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up macOS startup: {e}")
        return False

def create_linux_startup():
    """Create Linux startup entry"""
    try:
        # Get paths
        filedog_dir = get_current_dir()
        python_exe = sys.executable
        filedog_script = filedog_dir / "filedog.py"
        
        # Create autostart directory
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        # Create desktop entry content
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=FileDog
Comment=File Organizer with Background Monitoring
Exec={python_exe} {filedog_script} tray
Icon={filedog_dir}/filedog-icon.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
"""
        
        # Write desktop file
        desktop_file = autostart_dir / "filedog.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make it executable
        os.chmod(desktop_file, 0o755)
        
        print("✅ FileDog added to Linux startup")
        print(f"   Desktop entry: {desktop_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Linux startup: {e}")
        return False

def remove_windows_startup():
    """Remove Windows startup entry"""
    try:
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, "FileDog")
                print("✅ FileDog removed from Windows startup")
                return True
            except FileNotFoundError:
                print("⚠️ FileDog was not in Windows startup")
                return True
                
    except Exception as e:
        print(f"❌ Error removing Windows startup: {e}")
        return False

def remove_macos_startup():
    """Remove macOS startup entry"""
    try:
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_file = launch_agents_dir / "com.filedog.organizer.plist"
        
        if plist_file.exists():
            # Unload the launch agent
            subprocess.run(['launchctl', 'unload', str(plist_file)], check=False)
            # Remove the plist file
            plist_file.unlink()
            print("✅ FileDog removed from macOS startup")
        else:
            print("⚠️ FileDog was not in macOS startup")
        return True
        
    except Exception as e:
        print(f"❌ Error removing macOS startup: {e}")
        return False

def remove_linux_startup():
    """Remove Linux startup entry"""
    try:
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / "filedog.desktop"
        
        if desktop_file.exists():
            desktop_file.unlink()
            print("✅ FileDog removed from Linux startup")
        else:
            print("⚠️ FileDog was not in Linux startup")
        return True
        
    except Exception as e:
        print(f"❌ Error removing Linux startup: {e}")
        return False

def setup_startup():
    """Setup startup for current platform"""
    system = platform.system().lower()
    
    print(f"🖥️ Setting up FileDog startup for {platform.system()}...")
    
    if system == "windows":
        return create_windows_startup()
    elif system == "darwin":  # macOS
        return create_macos_startup()
    elif system == "linux":
        return create_linux_startup()
    else:
        print(f"❌ Unsupported platform: {system}")
        return False

def remove_startup():
    """Remove startup for current platform"""
    system = platform.system().lower()
    
    print(f"🖥️ Removing FileDog startup for {platform.system()}...")
    
    if system == "windows":
        return remove_windows_startup()
    elif system == "darwin":  # macOS
        return remove_macos_startup()
    elif system == "linux":
        return remove_linux_startup()
    else:
        print(f"❌ Unsupported platform: {system}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("""
FileDog Startup Setup

Usage:
    python setup_startup.py [command]

Commands:
    install    Set up FileDog to start automatically with system
    remove     Remove FileDog from system startup
    status     Check if FileDog is set to start automatically

Examples:
    python setup_startup.py install
    python setup_startup.py remove
    python setup_startup.py status
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        if setup_startup():
            print("\n🎉 FileDog will now start automatically with your system!")
            print("   It will run in the background and appear in your system tray.")
        else:
            print("\n❌ Failed to set up startup. You may need to run as administrator.")
    
    elif command == "remove":
        if remove_startup():
            print("\n✅ FileDog removed from startup.")
        else:
            print("\n❌ Failed to remove startup entry.")
    
    elif command == "status":
        system = platform.system().lower()
        if system == "windows":
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "FileDog")
                        print("✅ FileDog is set to start automatically")
                        print(f"   Command: {value}")
                    except FileNotFoundError:
                        print("❌ FileDog is not set to start automatically")
            except Exception as e:
                print(f"❌ Error checking status: {e}")
        else:
            print("Status check not implemented for this platform yet.")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
