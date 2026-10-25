import logging, os, smtplib
from pathlib import Path
from email.message import EmailMessage
import pymysql
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
(LOGS := BASE / "logs").mkdir(exist_ok=True)
logging.basicConfig(filename=LOGS/"email_summary.log", level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

def required(k):
    v=os.getenv(k)
    if not v: raise RuntimeError(f"Missing environment setting: {k}")
    return v

def latest_run():
    conn=pymysql.connect(host=os.getenv("DB_HOST","localhost"),
        port=int(os.getenv("DB_PORT","3306")), user=required("DB_USER"),
        password=required("DB_PASSWORD"), database=os.getenv("DB_NAME","maintenance_demo"),
        connect_timeout=10, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT id,job_name,deleted_rows,started_at,completed_at,status,details
                           FROM maintenance_runs WHERE job_name=%s
                           ORDER BY completed_at DESC,id DESC LIMIT 1""",
                        ("purge_old_application_logs",))
            return cur.fetchone()
    finally: conn.close()

def send_summary(run):
    msg=EmailMessage()
    msg["Subject"]=f"MySQL log maintenance summary - {run['status']}"
    msg["From"]=required("SMTP_FROM"); msg["To"]=required("SMTP_TO")
    msg.set_content(
        "MySQL log maintenance summary\n"
        "=============================\n"
        f"Job: {run['job_name']}\nStatus: {run['status']}\n"
        f"Rows deleted: {run['deleted_rows']}\n"
        f"Started: {run['started_at']}\nCompleted: {run['completed_at']}\n"
        f"Details: {run.get('details') or '-'}\n")
    host=required("SMTP_HOST"); port=int(os.getenv("SMTP_PORT","587"))
    user=os.getenv("SMTP_USERNAME",""); password=os.getenv("SMTP_PASSWORD","")
    if os.getenv("SMTP_USE_SSL","false").lower()=="true":
        with smtplib.SMTP_SSL(host,port,timeout=20) as s:
            if user: s.login(user,password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host,port,timeout=20) as s:
            s.ehlo(); s.starttls(); s.ehlo()
            if user: s.login(user,password)
            s.send_message(msg)

def main():
    try:
        run=latest_run()
        if not run: raise RuntimeError("No maintenance run found. Has the MySQL event run?")
        send_summary(run)
        logging.info("Email sent for run %s; deleted_rows=%s",run["id"],run["deleted_rows"])
        print(f"Summary email sent. Latest run deleted {run['deleted_rows']} row(s).")
    except Exception:
        logging.exception("Summary email failed"); raise

if __name__=="__main__": main()
