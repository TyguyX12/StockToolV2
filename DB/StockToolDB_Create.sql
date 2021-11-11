-- MySQL dump 10.13  Distrib 8.0.23, for Win64 (x86_64)
--
-- Host: localhost    Database: stocktooldb
-- ------------------------------------------------------
-- Server version	8.0.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `historicaldata`
--

DROP TABLE IF EXISTS `historicaldata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historicaldata` (
  `idHistoricalData` int NOT NULL AUTO_INCREMENT,
  `Open` decimal(10,2) NOT NULL,
  `High` decimal(10,2) NOT NULL,
  `Low` decimal(10,2) NOT NULL,
  `Close` decimal(10,2) NOT NULL,
  `MarketCap` decimal(15,2) NOT NULL,
  `StockReference` int NOT NULL,
  `time_stamp` datetime NOT NULL,
  PRIMARY KEY (`idHistoricalData`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historicaldata`
--

LOCK TABLES `historicaldata` WRITE;
/*!40000 ALTER TABLE `historicaldata` DISABLE KEYS */;
/*!40000 ALTER TABLE `historicaldata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `redditdata`
--

DROP TABLE IF EXISTS `redditdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `redditdata` (
  `idRedditData` int NOT NULL AUTO_INCREMENT,
  `Submission_title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Submission_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Upvote_ratio` float NOT NULL,
  `Upvotes` int NOT NULL,
  `Comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Comment_author` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Flair` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Created` datetime DEFAULT NULL,
  `StockReference` int DEFAULT NULL,
  PRIMARY KEY (`idRedditData`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `redditdata`
--

LOCK TABLES `redditdata` WRITE;
/*!40000 ALTER TABLE `redditdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `redditdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_exchanges`
--

DROP TABLE IF EXISTS `stock_exchanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_exchanges` (
  `idstock_exchanges` int NOT NULL AUTO_INCREMENT,
  `stock_exchanges_name` varchar(255) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`idstock_exchanges`),
  UNIQUE KEY `stock_exchanges_name_UNIQUE` (`stock_exchanges_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_exchanges`
--

LOCK TABLES `stock_exchanges` WRITE;
/*!40000 ALTER TABLE `stock_exchanges` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_exchanges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stocks`
--

DROP TABLE IF EXISTS `stocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stocks` (
  `idStocks` int NOT NULL AUTO_INCREMENT,
  `idStockExchange` int NOT NULL,
  `StockSymbol` varchar(45) COLLATE utf8_bin NOT NULL,
  `StockName` varchar(200) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
  PRIMARY KEY (`idStocks`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stocks`
--

LOCK TABLES `stocks` WRITE;
/*!40000 ALTER TABLE `stocks` DISABLE KEYS */;
/*!40000 ALTER TABLE `stocks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `twitterdata`
--

DROP TABLE IF EXISTS `twitterdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `twitterdata` (
  `idTwitterData` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DescriptionOfUser` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Location` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Following` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `followers` int NOT NULL,
  `TotalTweets` int NOT NULL,
  `RetweetCount` int NOT NULL,
  `Hashtags` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `TweetText` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `StockReference` int NOT NULL,
  `processed` varchar(1) NOT NULL DEFAULT 'N',
  `processed_daily` varchar(1) NOT NULL DEFAULT 'N',
  `processed_weekly` varchar(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`idTwitterData`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `twitterdata`
--

LOCK TABLES `twitterdata` WRITE;
/*!40000 ALTER TABLE `twitterdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `twitterdata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'stocktooldb'
--
/*!50003 DROP PROCEDURE IF EXISTS `Add_Stock` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE PROCEDURE Add_Stock @p_idStockExchange, int @p_StockSymbol varchar(45), @p_StockName varchar(200)
AS
insert into stocks
		(idStockExchange, StockSymbol, StockName)
	values
		(p_idStockExchange, p_StockSymbol, p_StockName);
GO;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Add_stock_exchanges` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;

CREATE PROCEDURE Add_stock_exchanges @p_stock_exchanges_name varchar(255)
AS
insert into stock_exchanges 
		(stock_exchanges_name)
	values
		(p_stock_exchanges_name);
GO;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Create_Historical_Data_Row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;

CREATE PROCEDURE Create_Historical_Data_Row @p_Open decimal(10,2), @p_High decimal(10,2), @p_Low decimal(10,2), @p_Close decimal(10,2), @p_MarketCap decimal(15,2), @p_StockReference int, @p_time_stamp datetime
AS
insert into historicaldata
		(Open, High, Low, Close, MarketCap, StockReference, time_stamp)
	values
		(p_Open, p_High, p_Low, p_Close, p_MarketCap, p_StockReference, p_time_stamp);
GO;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Create_Reddit_Row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;


CREATE PROCEDURE Create_Reddit_Row @p_Submission_title varchar(255), @p_Submission_name varchar(255), @p_Upvote_ratio float, @p_Upvotes int, @p_Comment LONGTEXT, @p_Comment_author LONGTEXT, @p_Flair LONGTEXT, @p_Created DATETIME, @p_StockReference int 

AS
insert into redditdata 
		(Submission_title, Submission_name, Upvote_ratio, Upvotes, Comment, Comment_author, Flair, Created, StockReference)
        values
        (p_Submission_title, p_Submission_name, p_Upvote_ratio, p_Upvotes, p_Comment, p_Comment_author, p_Flair, p_Created, p_StockReference);
GO;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Create_Twitter_Row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;

CREATE PROCEDURE Create_Twitter_Row 

AS
INSERT INTO twitterdata
		(username, DescriptionOfUser, Location, Following, followers, TotalTweets, RetweetCount, Hashtags, TweetText, Created, StockReference)
        VALUES
        (p_username, p_DescriptionOfUser, p_Location, p_following, p_followers, p_totaltweets, p_RetweetCount, p_Hashtags, p_TweetText, p_Created, p_StockReference);
GO;

DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Historical_Data_Row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;

CREATE PROCEDURE Historical_Data_Row @p_Open decimal(10,2), @p_High decimal(10,2), @p_Low decimal(10,2), @p_Close decimal(10,2),  @p_MarketCap decimal(15,2), @p_StockReference int, @p_time_stamp datetime

AS
insert into historicaldata
		(Open, High, Low, Close, MarketCap, StockReference, time_stamp)
	values
		(p_Open, p_High, p_Low, p_Close, p_MarketCap, p_StockReference, p_time_stamp);
GO;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-03-29 16:30:12
