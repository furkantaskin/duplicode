"""
Aim of this part is to copy source template and generate new project through cPanel file manager.

- Log in to the cPanel
- Go to the file manager
- Create zip from template (it can vary per project)
- Create destination folder or new project in file manager
- Move the zip file and extract it
- Delete the zip file after extraction

==== WARNING ====
It is currently using cPanel for my personal purposes. It may vary from team to team or company to company.
Check selectors with text arguments. Because cPanel is using mixed language in their file manager, creating JSON for
selector texts will be a difficult challenge.

Author: Furkan Taşkın (muffinisamuffin)
"""
from playwright.sync_api import Playwright
from decouple import config
import re


def cp_run(playwright: Playwright, dest_folder, source_folder, is_video, use_id):

    # Runs playwright and logins to whm panel
    browser = playwright.chromium.launch(channel="chrome", slow_mo=1000, headless=True)

    # Choose video directory if user wants video
    context = browser.new_context(no_viewport=True,
                                  viewport={"width": 1800, "height": 900},
                                  record_video_size={"width": 1800, "height": 900},
                                  record_video_dir=f"videos/{int(use_id)}" if is_video else None)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()

    print("Logging into cPanel")
    page.goto(config('GOLINK'))
    page.locator("input#user").fill(config('USERNAME'))
    page.locator("input#pass").fill(config('USERPASS'))
    page.locator("button[name='login']").click()
    page.wait_for_load_state('networkidle')
    with page.expect_popup() as popup_info:
        page.get_by_role("link", name="Dosya Yöneticisi Dosya Yöneticisi").click()
    page1 = popup_info.value

    # Create destination folder
    print("Creating destination folder")
    page1.locator("input#location").fill(f"public_html/demo")
    page1.locator("button#btnGo").click()
    page1.wait_for_timeout(500)
    page1.get_by_role("link", name=re.compile("Klasör")).click()
    page1.locator("input#new-folder-name").fill(f"{dest_folder}")
    page1.get_by_role("button", name="Create New Folder").click()
    page1.wait_for_timeout(600)

    # Create zip from source folder
    print("Compressing source file")
    page1.locator("input#location").fill(f"public_html/demo/{source_folder}")
    page1.locator("button#btnGo").click()
    page.wait_for_timeout(500)
    page1.get_by_role("link", name=re.compile("Tümünü Seç")).click()
    page1.get_by_role("link", name=re.compile("Sıkıştır")).click()
    page1.get_by_role("radio", name=re.compile("Zip Arşivi")).click()
    page1.locator("input[name='compressfilepath']").fill(f"/public_html/demo/{source_folder}/transfer.zip")
    page1.get_by_role("button", name="Compress Files").click()
    page.wait_for_timeout(30000)
    page1.get_by_role("button", name="Close").click()
    page1.get_by_role("link", name=" Yeniden yükle").click()
    page1.get_by_role("cell", name="transfer.zip").locator("div:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    print("Moving files")
    page1.get_by_role("link", name=re.compile("Taşı")).click()
    page1.get_by_label("Geçerli Yol:").fill(f"/public_html/demo/{dest_folder}/")
    page1.keyboard.press("Enter")

    # Go to the destination folder to extract the zip
    page1.locator("input#location").fill(f"public_html/demo/{dest_folder}/")
    page1.locator("button#btnGo").click()
    page.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click(button="right")
    print("Extracting zip file")
    page1.get_by_role("link", name=re.compile("Çıkar")).click()
    page1.get_by_role("button", name="Extract Files").click()
    page1.get_by_role("button", name="Close").click()
    page1.get_by_role("link", name=" Yeniden yükle").click()

    # Delete the zip file
    print("Removing unused files")
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click(button="right")
    page1.get_by_role("link", name=re.compile("Sil")).click()
    page1.get_by_label("Dosyaları çöp kutusuna atmadan kalıcı olarak silin").check()
    page1.get_by_role("button", name="Confirm").click()
    context.tracing.stop(path=f"../traces/trace_{int(use_id)}.zip")
    print("Shutting Down")
    context.close()
    browser.close()
