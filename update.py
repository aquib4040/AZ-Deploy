import os
import sys
from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger
from subprocess import run as srun
from shutil import which as shutil_which, rmtree

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)
LOGGER = getLogger("DeployUpdater")

def load_env_file():
    for f in [".env", "config.env"]:
        if os.path.exists(f):
            try:
                from dotenv import load_dotenv
                load_dotenv(f, override=False)
            except ImportError:
                with open(f) as fp:
                    for line in fp:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() not in os.environ:
                                os.environ[k.strip()] = v.strip().strip("'").strip('"')

def fetch_mongo_config(database_url, bot_id):
    try:
        from pymongo import MongoClient
    except ImportError:
        srun("uv pip install --system --break-system-packages pymongo", shell=True)
        from pymongo import MongoClient

    try:
        client = MongoClient(database_url, serverSelectionTimeoutMS=5000)
        db = client.canonleech
        cfg = db["settings.config"].find_one({"_id": bot_id})
        client.close()
        return cfg or {}
    except Exception as e:
        LOGGER.warning(f"Could not load config from MongoDB: {e}")
        return {}

def update_repo(upstream_repo, upstream_branch):
    LOGGER.info(f"Syncing code from {upstream_repo} [{upstream_branch}]...")
    if os.path.exists(".git"):
        srun(["rm", "-rf", ".git"])

    git_cmds = [
        ["git", "init", "-q"],
        ["git", "config", "--global", "user.email", "mdaquibjawed1106@gmail.com"],
        ["git", "config", "--global", "user.name", "aquib4040"],
        ["git", "add", "."],
        ["git", "commit", "-sm", "update", "-q"],
        ["git", "remote", "add", "origin", upstream_repo],
        ["git", "fetch", "origin", "-q"],
        ["git", "reset", "--hard", f"origin/{upstream_branch}", "-q"],
    ]

    for cmd in git_cmds:
        res = srun(cmd)
        if res.returncode != 0:
            LOGGER.error(f"Git command failed: {' '.join(cmd)}")
            return False

    LOGGER.info("Successfully fetched latest repository commits!")
    return True

def install_packages():
    if not os.path.exists("requirements.txt"):
        return
    uv_bin = shutil_which("uv") or "uv"
    LOGGER.info(f"Installing dependencies with {uv_bin}...")
    cmd = f'"{uv_bin}" pip install --system --break-system-packages --no-cache -r requirements.txt'
    res = srun(cmd, shell=True)
    if res.returncode == 0:
        LOGGER.info("Successfully installed requirements!")
    else:
        LOGGER.warning("uv pip install failed, attempting python fallback...")
        srun("python3 -m pip install --break-system-packages --no-cache-dir -r requirements.txt", shell=True)

def cleanup_files():
    for f in ["Dockerfile", "docker-compose.yml", "heroku.yml"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass
    for d in [".github"]:
        if os.path.isdir(d):
            rmtree(d, ignore_errors=True)

def main():
    load_env_file()
    bot_token = os.environ.get("BOT_TOKEN", "").strip()
    bot_id = bot_token.split(":", 1)[0] if bot_token else ""
    database_url = os.environ.get("DATABASE_URL", "").strip()

    upstream_repo = os.environ.get("UPSTREAM_REPO", "").strip()
    upstream_branch = os.environ.get("UPSTREAM_BRANCH", "").strip()

    if database_url and bot_id:
        db_cfg = fetch_mongo_config(database_url, bot_id)
        if not upstream_repo and db_cfg.get("UPSTREAM_REPO"):
            upstream_repo = str(db_cfg["UPSTREAM_REPO"]).strip()
        if not upstream_branch and db_cfg.get("UPSTREAM_BRANCH"):
            upstream_branch = str(db_cfg["UPSTREAM_BRANCH"]).strip()

    upstream_repo = upstream_repo or "https://github.com/aquib4040/AZML"
    upstream_branch = upstream_branch or "test-hk"

    success = update_repo(upstream_repo, upstream_branch)
    if success:
        cleanup_files()
        install_packages()
    else:
        LOGGER.error("Failed to sync upstream repository!")
        sys.exit(1)

if __name__ == "__main__":
    main()
