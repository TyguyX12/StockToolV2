DROP TABLE IF EXISTS `sentimentdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sentimentdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sentiment_scores` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sentiment_type` varchar(10),
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
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


CREATE TABLE `processedsentimentdata` (
  `asset` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `daily_score` int,
  `weekly_score` int,
  `monthly_score` int,
  PRIMARY KEY (`asset`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `processedsentimentdata`
--

LOCK TABLES `processedsentimentdata` WRITE;
/*!40000 ALTER TABLE `processedsentimentdata` DISABLE KEYS */;
/*!40000 ALTER TABLE `processedsentimentdata` ENABLE KEYS */;
UNLOCK TABLES;
