from playwright.sync_api import Playwright, expect
from decouple import config
import re


def cp_run(playwright: Playwright, dest_folder, source_folder, is_video):
    # Runs playwright and logins to whm panel
    browser = playwright.chromium.launch(channel="chrome", headless=False)
    # Choose video directory if user wants video
    context = browser.new_context(no_viewport=True, record_video_dir="videos/" if is_video else None)

    page = context.new_page()

    print("Logging into cPanel")
    page.goto(config('GOLINK'))
    expect(page).to_have_title("cPanel Login")
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
    page.wait_for_timeout(500)
    page1.get_by_role("link", name=re.compile("Klasör")).click()
    page1.locator("input#new-folder-name").fill(f"{dest_folder}")
    page1.get_by_role("button", name="Create New Folder").click()

    # Create zip from source folder
    page1.locator("input#location").fill(f"public_html/demo/{source_folder}")
    page1.locator("button#btnGo").click()
    page.wait_for_timeout(500)
    page1.get_by_role("link", name=re.compile("Tümünü Seç")).click()
    page1.get_by_role("link", name=re.compile("Sıkıştır")).click()
    page1.get_by_role("radio", name=re.compile("Zip Arşivi")).click()
    page1.locator("input[name='compressfilepath']").fill(f"/public_html/demo/{source_folder}/transfer.zip")
    page1.get_by_role("button", name="Compress Files").click()
    page.wait_for_timeout(5000)
    page1.locator("button:has-text(\"Close\"").click()
    page1.get_by_role("link", name=re.compile("Yeniden Yükle")).click()
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click(button="right")
    page1.get_by_role("link", name=re.compile("Taşı")).click()
    page1.get_by_label("Geçerli Yol:").fill(f"/public_html/demo/{dest_folder}")
    page1.get_by_role("button", name="Move Files").click()

    # Go to the destination folder to extract the zip
    page1.locator("input#location").fill(f"public_html/demo/{dest_folder}")
    page1.locator("button#btnGo").click()
    page.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click(button="right")
    page1.get_by_role("link", name=re.compile("Çıkar")).click()
    page1.get_by_role("button", name="Extract Files").click()
    page1.get_by_role("button", name="Close").click()
    page1.get_by_role("link", name=re.compile("Yeniden Yükle")).click()

    # Delete the zip file
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click()
    page1.wait_for_timeout(500)
    page1.locator(".yui-dt-rec:has-text(\"transfer.zip\")").click(button="right")
    page1.get_by_role("link", name=re.compile("Sil")).click()
    page1.get_by_label("Dosyaları çöp kutusuna atmadan kalıcı olarak silin").check()
    page1.get_by_role("button", name="Confirm").click()
    page.pause()