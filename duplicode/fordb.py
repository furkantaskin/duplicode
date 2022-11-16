from playwright.sync_api import Playwright, sync_playwright
from decouple import config
import re
import time


def pma_run(playwright: Playwright, dest_folder, source_folder, is_video, use_id):
    browser = playwright.chromium.launch(channel="chrome", headless=False)

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
    page.get_by_role("link", name="MySQL® Veritabanları MySQL® Veritabanları").click()
    page.wait_for_load_state('networkidle')
    # TODO Fix empty list error
    db_options = page.locator("select#checkdb option")
    page.pause()
    print(db_options.inner_text(), db_options.count(), sep="\n")
    db_list = [db_options.nth(i).get_attribute("value") for i in range(db_options.count())]
    print(db_list)


with sync_playwright() as p:
    pma_run(p, None, None, False, 1)