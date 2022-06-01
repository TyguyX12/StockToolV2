DROP TABLE IF EXISTS `sentimentdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sentimentdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `source` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` datetime NOT NULL DEFAULT CAST(GETDATE() AS Date),
  `asset` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `score_neg` int,
  `score_neu` int,
  `score_pos` int,
  `num_neg` int,
  `num_neu` int,
  `num_pos` int,
  `total_posts` int,
  
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
