Let the agent "see" your page (for debugging layout/modal)

1. Install Playwright (one-time):
   pip install playwright
   playwright install

2. Start the Django server in one terminal:
   python manage.py runserver

3. In another terminal, run:
   python scripts/capture_page.py

4. Screenshots are saved in the project root:
   live_check_main.png   — Records list
   live_check_modal.png — Modal open (Sales)

5. Tell the agent: "Check live_check_main.png and live_check_modal.png"
   (or @-mention those files). The agent can read the images and suggest fixes.
