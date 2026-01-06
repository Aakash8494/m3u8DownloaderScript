import os
import subprocess
import argparse
from datetime import datetime


def log(message):
    """
    Simple logger with timestamp
    """
    time = datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] {message}")


def run_all_commands(commands_dir):
    """
    Reads every .txt file from the given folder
    and runs the command inside each file ONE BY ONE.
    """

    # --- Validate folder ---
    if not os.path.isdir(commands_dir):
        log(f"❌ Folder not found: {commands_dir}")
        return

    # --- Collect all .txt files ---
    files = sorted(
        f for f in os.listdir(commands_dir)
        if f.endswith(".txt")
    )

    if not files:
        log("⚠️ No .txt command files found.")
        return

    log(f"📂 Commands folder: {commands_dir}")
    log(f"📝 Total command files: {len(files)}")

    success_count = 0
    fail_count = 0

    # --- Run commands one by one ---
    for index, file in enumerate(files, start=1):
        path = os.path.join(commands_dir, file)

        log("-" * 60)
        log(f"▶️ ({index}/{len(files)}) Running file: {file}")

        # --- Read command from file ---
        with open(path, "r", encoding="utf-8") as f:
            command = f.read().strip()

        if not command:
            log("⚠️ Skipping: file is empty")
            continue

        log("📌 Command:")
        log(command.replace("\n", " "))

        try:
            # IMPORTANT:
            # subprocess.run is BLOCKING
            # → Next command will start only after this finishes
            subprocess.run(command, shell=True, check=True)

            log("✅ Completed successfully")
            success_count += 1

        except subprocess.CalledProcessError as e:
            log("❌ Command failed")
            log(f"Error: {e}")
            fail_count += 1

    # --- Final summary ---
    log("=" * 60)
    log("🎯 All commands processed")
    log(f"✅ Success: {success_count}")
    log(f"❌ Failed : {fail_count}")
    log("=" * 60)


def main():
    """
    Entry point.
    Reads folder path from CLI args.
    """

    parser = argparse.ArgumentParser(
        description="Run all downloader command files sequentially"
    )

    parser.add_argument(
        "--commands-path",
        required=True,
        help="Path to folder containing command .txt files",
    )

    args = parser.parse_args()

    run_all_commands(args.commands_path)


if __name__ == "__main__":
    main()