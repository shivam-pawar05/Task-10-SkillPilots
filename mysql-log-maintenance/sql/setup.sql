CREATE DATABASE IF NOT EXISTS maintenance_demo;
USE maintenance_demo;
CREATE TABLE IF NOT EXISTS application_logs (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 level VARCHAR(20) NOT NULL DEFAULT 'INFO',
 message TEXT NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_created_at (created_at)
);
CREATE TABLE IF NOT EXISTS maintenance_runs (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 job_name VARCHAR(100) NOT NULL,
 deleted_rows BIGINT UNSIGNED NOT NULL DEFAULT 0,
 started_at DATETIME NOT NULL,
 completed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
 details VARCHAR(500),
 INDEX idx_job_completed (job_name, completed_at)
);
INSERT INTO application_logs(level,message,created_at) VALUES
('INFO','Recent test log',NOW()),
('WARN','Old test log',NOW()-INTERVAL 45 DAY),
('ERROR','Another old test log',NOW()-INTERVAL 60 DAY);
-- Check with: SHOW VARIABLES LIKE 'event_scheduler';
-- Admin may enable with: SET GLOBAL event_scheduler = ON;
DELIMITER $$
CREATE EVENT IF NOT EXISTS purge_old_application_logs
ON SCHEDULE EVERY 1 DAY
STARTS (CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR)
ON COMPLETION PRESERVE ENABLE
DO
BEGIN
 DECLARE v_started DATETIME DEFAULT NOW();
 DECLARE v_deleted BIGINT DEFAULT 0;
 DELETE FROM application_logs WHERE created_at < NOW() - INTERVAL 30 DAY;
 SET v_deleted = ROW_COUNT();
 INSERT INTO maintenance_runs(job_name,deleted_rows,started_at,completed_at,status,details)
 VALUES('purge_old_application_logs',v_deleted,v_started,NOW(),'SUCCESS',
 'Deleted application log rows older than 30 days');
END$$
DELIMITER ;
-- Verify: SHOW EVENTS FROM maintenance_demo;
