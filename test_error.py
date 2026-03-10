from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        errors = []
        page.on("pageerror", lambda err: errors.append(err))

        page.goto("file:///app/public/index.html")

        # Click the locate button
        page.locator("#locate-btn").click()
        time.sleep(1)

        if len(errors) > 0:
            print("ERRORS FOUND:")
            for e in errors:
                print(e)
        else:
            print("NO ERRORS FOUND")

        # Check text in a11y announcer
        print("Announcer text:", page.locator("#a11y-announcer").text_content())

        browser.close()

if __name__ == "__main__":
    run()
