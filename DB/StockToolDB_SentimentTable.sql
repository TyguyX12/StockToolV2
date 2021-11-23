DROP TABLE IF EXISTS `sentimentdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sentimentdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `asset` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `daily_twitter_score` int,
  `daily_reddit_score` int,
  `daily_cumulative_score` int,
  `date` datetime NOT NULL DEFAULT CAST(GETDATE() AS Date),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sentimentdata`
--

LOCK TABLES `sentimentdata` WRITE;
/*!40000 ALTER TABLE `sentimentdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `sentimentdata` ENABLE KEYS */;
UNLOCK TABLES;
