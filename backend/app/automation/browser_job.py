# backend/app/automation/browser_job.py

from .runner import process_csv_and_submit as _run

def process_csv_and_submit(csv_path: str, proxy: str = "", halt_on_captcha: bool = True,
                           message: str = "", user_profile: dict | None = None):
    return _run(csv_path, proxy, halt_on_captcha, message, user_profile)

if __name__ == "__main__":
    import sys
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else "uploads/websites.csv"
    proxy_arg = sys.argv[2] if len(sys.argv) > 2 else ""
    halt_arg = (sys.argv[3].lower() == "true") if len(sys.argv) > 3 else True
    _run(csv_arg, proxy_arg, halt_arg)
