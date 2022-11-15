"""
Get input from user to copy webpage
"""

from playwright.sync_api import Playwright, sync_playwright
from main import run

create_folder = "demo"
# create_folder = input("Give me the folder you wanna create: ")

print("Input can't be empty") if create_folder == "\n" or create_folder == " " \
    else print("Creating folder")

with sync_playwright() as p:
    run(p)
