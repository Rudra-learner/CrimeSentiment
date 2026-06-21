from playwright.sync_api import sync_playwright


def test_sambad():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(
            "https://sambadenglish.com/?s=nayagarh",
            wait_until="networkidle",
            timeout=60000
        )

        print(
            page.title()
        )

        print(
            page.url
        )

        print(
            page.content()[:1000]
        )

        input(
            "\nPress Enter to close..."
        )

        browser.close()


if __name__ == "__main__":

    test_sambad()