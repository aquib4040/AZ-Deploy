#!/bin/bash
HEROKU_PORT="${PORT}"

rm -f *.session *.session-journal *.session*

if [ -f .env ]; then
  set -a
  source .env
  set +a
elif [ -n "$BOT_TOKEN" ]; then
  cat <<EOF > .env
BOT_TOKEN=${BOT_TOKEN}
OWNER_ID=${OWNER_ID}
TELEGRAM_API=${TELEGRAM_API}
TELEGRAM_HASH=${TELEGRAM_HASH}
DATABASE_URL=${DATABASE_URL}
EOF
fi

if [ -n "$HEROKU_PORT" ]; then
  export PORT="$HEROKU_PORT"
  export BASE_URL_PORT="$HEROKU_PORT"
else
  export PORT="${PORT:-85}"
  export BASE_URL_PORT="${BASE_URL_PORT:-$PORT}"
fi

python3 update.py
exec python3 -m bot\n