use StockToolDB;
	
SET GLOBAL event_scheduler = ON;

CREATE EVENT Clear_Social_Media_Data
ON SCHEDULE EVERY 24 HOUR
DO
  DELETE FROM socialmediadata;
