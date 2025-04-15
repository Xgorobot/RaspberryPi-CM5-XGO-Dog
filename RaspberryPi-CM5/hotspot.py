from demos.uiutils import fm_logo,re_logo,get_font,Button,splash,display,draw,random
import string
import socket,sys,os,time

sys.path.append("..")
button = Button()
# Font Loading
font1 = get_font(20)

#Color Loading
splash_theme_color = (15, 21, 46)
purple = (24, 47, 223)
draw.rectangle([(0, 0), (320, 240)], fill=splash_theme_color)

'''
    Generate Randomized Wifi Ssid
'''
def generate_wifi_ssid():
    prefix = "xgo-"
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return prefix + suffix

'''
    Generate Randomized Wifi Password
'''
def generate_wifi_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))

'''
    Lcd_Text
'''
def lcd_text(x, y, content):
    draw.text((x, y), content, fill="WHITE", font=font1)

'''
    Get Hotspot IP
'''
def get_ip(ifname):
    import socket, struct, fcntl

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(
        fcntl.ioctl(
            s.fileno(), 0x8915, struct.pack("256s", bytes(ifname[:15], "utf-8"))
        )[20:24]
    )


ssid = generate_wifi_ssid()
password = generate_wifi_password()


hotspot_cmd = "sudo nmcli device wifi hotspot ssid {} password {}".format(
    ssid, password
)

# Activate wlan0
os.system("sudo ifconfig wlan0 up")
time.sleep(2)

# Disconnect the current connection on wlan0
os.system("sudo nmcli device disconnect wlan0")

# Restart NetworkManager 
os.system("sudo systemctl restart NetworkManager")
time.sleep(5)

# Cleaning up possible residual network connections
os.system("sudo nmcli connection delete Hotspot-7")

# Creat Wifi Hotspot
result = os.system(hotspot_cmd)
if result == 0:
    print("Wi-Fi Hotspot Created Successfully")
else:
    print("Wi-Fi Hotspot Created Failed heck The Relevant Settings")

lcd_text(77, 115, "SSID:" + ssid)
lcd_text(77, 150, "PWD:" + password)
splash.paste(re_logo, (115, 15), re_logo)
ip_address = get_ip("wlan0")
lcd_text(102, 185, ip_address)
display.ShowImage(splash)

while True:
    if button.press_a() or button.press_b() or button.press_c() or button.press_d():
        time.sleep(1)
        close_result = os.system("sudo nmcli connection down Hotspot-7")
        if close_result == 0:
            print("stop success")
            time.sleep(1)
            os.system("sudo reboot")
        else:
            print(f"Failed to stop hotspot, error code: {close_result}")
        break
