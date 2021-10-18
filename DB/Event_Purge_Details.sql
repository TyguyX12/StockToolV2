use StockToolDB;
	
SET GLOBAL event_scheduler = ON;

CREATE EVENT Eve_Detail_Table_Purge
ON SCHEDULE EVERY 24 HOUR
DO
  DELETE FROM twitterdata 
	WHERE processed = 'Y' and processed_daily = 'Y' and processed_weekly = 'Y';
