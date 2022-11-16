"""
Get input from user to copy webpage
"""

from playwright.sync_api import Playwright, sync_playwright
from duplicode import main
import time

create_folder = input("Give me the folder you wanna create: ")
res_folder = input("Choose folder to copy: ")
video_option = input("Do you want video record (y/n): ").lower()

check_video = True if video_option == "y" else False

print("Input can't be empty") if create_folder in ["\n", " "] else print("Starting Process for cPanel")
get_id = int(time.time())
print("Current process id is", get_id)
options = ["cPanel", "CWP", "Plesk"]

with sync_playwright() as p:
    main.cp_run(p, create_folder, res_folder, check_video, get_id)
