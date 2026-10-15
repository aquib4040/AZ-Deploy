# AZ-Deploy

Remote container deployment wrapper for AZML.

### How to Deploy via GitHub Actions

1. Go to the **Actions** tab of this repository.
2. Select the **Deploy AZML to Heroku** workflow.
3. Click **Run workflow** and provide your credentials:
   - `HEROKU_APP_NAME`
   - `HEROKU_API_KEY`
   - `HEROKU_EMAIL`
   - `BOT_TOKEN`
   - `OWNER_ID`
   - `DATABASE_URL`
   - `TELEGRAM_API`
   - `TELEGRAM_HASH`
   - `UPSTREAM_REPO` (`https://github.com/aquib4040/AZML`)
   - `UPSTREAM_BRANCH` (`test-hk`)
4. Run workflow and monitor logs.\n