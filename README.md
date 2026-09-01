# Schedule page monitor → phone notification

Checks the schedule page hourly and sends a push notification to your phone
via [ntfy.sh](https://ntfy.sh) when the content changes. Runs for free on
GitHub Actions — nothing needs to stay on at your end.

## Setup (~10 minutes)

### 1. Install ntfy on your phone
- iOS: [App Store link](https://apps.apple.com/us/app/ntfy/id1625396347)
- Android: [Play Store link](https://play.google.com/store/apps/details?id=io.heckel.ntfy)

Open the app, tap "+", and subscribe to a **topic name you make up** —
something unique and hard to guess, e.g. `amaterasu-sched-x7k2p9`.
(Anyone who knows your topic name can see/send to it, so don't use something
guessable like `my-schedule`.)

### 2. Create a GitHub repo
- Go to github.com, create a new **private** repository (e.g. `schedule-watch`).
- Upload these two files to it:
  - `check_schedule.py`
  - `state.json` — create an empty one containing just `{}`
- Create a folder `.github/workflows/` and upload `check-schedule.yml` into it.

### 3. Add your ntfy topic as a secret
- In the repo: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `NTFY_TOPIC`
- Value: the topic name you picked in step 1 (e.g. `amaterasu-sched-x7k2p9`)

### 4. Enable Actions and test it
- Go to the **Actions** tab in your repo, enable workflows if prompted.
- Click into "Check schedule page" → **Run workflow** to trigger it manually
  once. This first run just saves a baseline (no notification, that's normal).
- Run it manually a second time — you should see "No change." in the log.

From here it runs automatically every hour. When the page's schedule content
changes, you'll get a push notification on your phone.

## Notes
- The script hashes the visible text content of the page's main section, so
  it ignores insignificant changes to header/footer chrome, ads, etc.
- If you ever want to check a different URL, edit `MONITOR_URL` in the
  workflow file or the script directly.
- GitHub's free tier includes plenty of Actions minutes for a once-an-hour
  check like this.
