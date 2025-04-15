from uiutils import (get_font, display_cjk_string, Button, color_white,
                     color_bg, color_purple, lal, draw, splash, display,
                     wifi_logo, arrow_logo_2, la)
import time, os
import subprocess

# Init Key
button = Button()

# Font Loading
font1 = get_font(16)
font2 = get_font(18)

# Wifi Path
wifi1 = "/etc/default/crda"
wifi2 = "/etc/wpa_supplicant/wpa_supplicant.conf"

def safe_write_file(path, content):
    """Securely write to system files with sudo fallback"""
    try:
        subprocess.run(
            f'echo "{content}" | sudo tee {path} >/dev/null',
            shell=True,
            check=True,
            executable='/bin/bash'
        )
        return True
    except subprocess.CalledProcessError:
        try:
            tmp_path = f"/tmp/{os.path.basename(path)}.tmp"
            with open(tmp_path, "w") as f:
                f.write(content)
            subprocess.run(["sudo", "cp", tmp_path, path], check=True)
            os.remove(tmp_path)
            return True
        except Exception:
            return False

def get_current_country():
    """Get current country code from the most authoritative source"""
    try:
        # Try raspi-config first
        result = subprocess.run(["sudo", "raspi-config", "nonint", "get_wifi_country"],
                               capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:2]
        
        # Fall back to wpa_supplicant
        result = subprocess.run(["sudo", "grep", "country=", wifi2],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.split("country=")[1][:2]
        
        # Final fallback to crda
        result = subprocess.run(["sudo", "grep", "REGDOMAIN=", wifi1],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.split("REGDOMAIN=")[1][:2]
    except Exception:
        pass
    
    return "US"  # Default if none found

# Get current country code
ct_code = get_current_country()

# UI initialization
splash.paste(wifi_logo, (133, 25), wifi_logo)
text_width = draw.textlength(lal["WIFISET"]["SET"], font=font2)
title_x = (320 - text_width) / 2

display_cjk_string(
    draw,
    title_x,
    90,
    lal["WIFISET"]["SET"],
    font_size=font2,
    color=color_white,
    background_color=color_bg,
)

country_list = [
    ["United States", "US"],
    ["Britain(UK)", "GB"],
    ["Japan", "JP"],
    ["Koera(South)", "KR"],
    ["China", "CN"],
    ["Australia", "AU"],
    ["Canada", "CA"],
    ["France", "FR"],
    ["Hong Kong", "HK"],
    ["Singapore", "SG"],
]
select = 0

# Display current country code
draw.rectangle([(20, 130), (120, 160)], fill=color_purple)
display_cjk_string(
    draw, 55, 133, ct_code, 
    font_size=font2, 
    color=color_white, 
    background_color=color_purple
)
display.ShowImage(splash)

while True:
    draw.rectangle([(20, 175), (300, 210)], fill=color_white)
    splash.paste(arrow_logo_2, (277, 185), arrow_logo_2)
    display_cjk_string(
        draw,
        30,
        180,
        country_list[select][0],
        font_size=font2,
        color=(0, 0, 0),
        background_color=color_white,
    )
    display.ShowImage(splash)
    
    if button.press_c():  # Previous
        select = len(country_list) - 1 if select == 0 else select - 1
    elif button.press_d():  # Next
        select = 0 if select == len(country_list) - 1 else select + 1
    elif button.press_a():  # Confirm
        break
    elif button.press_b():  # Exit
        os._exit(0)

new_code = country_list[select][1]

# Update all country code locations
success = True

# 1. Update /etc/default/crda
try:
    content = subprocess.getoutput(f"sudo cat {wifi1}")
    if "REGDOMAIN=" in content:
        new_content = content.replace(f"REGDOMAIN={ct_code}", f"REGDOMAIN={new_code}")
    else:
        new_content = f"{content}\nREGDOMAIN={new_code}\n" if content else f"REGDOMAIN={new_code}\n"
    success &= safe_write_file(wifi1, new_content)
except Exception:
    success = False

# 2. Update /etc/wpa_supplicant/wpa_supplicant.conf
try:
    content = subprocess.getoutput(f"sudo cat {wifi2}")
    if "country=" in content:
        new_content = content.replace(f"country={ct_code}", f"country={new_code}")
    else:
        new_content = f"{content}\ncountry={new_code}\n" if content else f"country={new_code}\n"
    success &= safe_write_file(wifi2, new_content)
except Exception:
    success = False

# 3. Update Raspberry Pi configuration
try:
    subprocess.run(["sudo", "raspi-config", "nonint", "do_wifi_country", new_code], 
                  check=True, stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    success = False

# Apply settings immediately
if success:

    subprocess.run(["sudo", "iw", "reg", "set", new_code], 
                  check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"], 
                  check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], 
                  check=True, stderr=subprocess.DEVNULL)
    if la=='cn':
      msg = "设置成功"
    else:
      msg = "Settings Saved!"
    bg_color = color_purple

else:
    if la=='cn':
      msg ="设置失败"
    else:
      msg = "Save Failed"
    bg_color = (255, 0, 0)

text_width = draw.textlength(msg, font=font2)
title_x = (320 - text_width) / 2
display_cjk_string(
    draw,
    title_x,
    210,
    msg,
    font_size=font2,
    color=color_white,
    background_color=bg_color,
)
display.ShowImage(splash)
time.sleep(2)