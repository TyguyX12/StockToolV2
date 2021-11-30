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

DROP TABLE IF EXISTS `redditdata`;

DROP TABLE IF EXISTS `stock_exchanges`;

DROP TABLE IF EXISTS `stocks`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;

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
/*!50003 DROP PROCEDURE IF EXISTS `Create_Historical_Data_Row` */;
/*!50003 DROP PROCEDURE IF EXISTS `Historical_Data_Row` */;
/*!50003 DROP PROCEDURE IF EXISTS `Create_Reddit_Row` */;
/*!50003 DROP PROCEDURE IF EXISTS `Create_Twitter_Row` */;

/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;


DELIMITER ;;
CREATE PROCEDURE Create_Twitter_Row(p_username varchar(255), p_DescriptionOfUser longtext, p_Location mediumtext, p_following longtext, p_followers int, p_totaltweets int, p_RetweetCount int, p_Hashtags longtext, p_TweetText mediumtext, p_Created datetime, p_StockReference int)
BEGIN
INSERT INTO twitterdata
		(username, DescriptionOfUser, Location, Following, followers, TotalTweets, RetweetCount, Hashtags, TweetText, Created, StockReference)
        VALUES
        (p_username, p_DescriptionOfUser, p_Location, p_following, p_followers, p_totaltweets, p_RetweetCount, p_Hashtags, p_TweetText, p_Created, p_StockReference);
END;;
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
