MySQL Log Maintenance and Email Summary
A demo MySQL Event deletes application log rows older than 30 days, stores the deleted-row count in an audit table, and a Python script emails the latest summary via SMTP.

Setup
Install Python 3.10+ and MySQL.
Run sql/setup.sql in MySQL Workbench.
Check SHOW VARIABLES LIKE 'event_scheduler';. If OFF, a MySQL admin can enable it with SET GLOBAL event_scheduler = ON; configure it persistently in server settings if appropriate.
Create a virtual environment and install dependencies:
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
Copy .env.example to .env; set database credentials and SMTP settings. Never commit .env.
Run python main.py to email the latest maintenance run.
Workflow
MySQL Event runs daily at about 02:00 server time.
It deletes rows older than 30 days and immediately captures ROW_COUNT().
The count is stored in maintenance_runs.
Python reads the latest audit record and sends a summary email.
Email logs are written to logs/email_summary.log.
Schedule Python after the event
Use Windows Task Scheduler to run about 10 minutes after the event (for example 02:10):

Program: full path to .venv\\Scripts\\python.exe
Arguments: main.py
Start in: full project folder path
Make sure the machine and database are available at the scheduled time. MySQL event time uses the database server's time zone.

Verify
SELECT * FROM maintenance_runs ORDER BY completed_at DESC LIMIT 5;
SELECT COUNT(*) FROM application_logs WHERE created_at < NOW() - INTERVAL 30 DAY;
Safety and production notes
This SQL uses a demo application_logs table; adapt only after backup and testing.
ROW_COUNT() must immediately follow the DELETE to capture its affected-row count.
The event logs successful runs, including zero deletions; add a MySQL error handler and monitoring for production.
Large deletes may lock rows and increase replication load; consider batched deletion for large tables.
Use a least-privilege database account and SMTP credentials/app password supported by your provider.
If logs are stored in files rather than a MySQL table, this event-based design does not apply directly.
