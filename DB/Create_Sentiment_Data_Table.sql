DROP TABLE IF EXISTS `sentimentdata`;

CREATE TABLE `sentimentdata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `source` tinytext,
  `date` tinytext,
  `asset` tinytext,
  `score_neg` FLOAT,
  `score_neu` FLOAT,
  `score_pos` FLOAT,
  `score_comp` FLOAT,
  `num_neg` int,
  `num_neu` int,
  `num_pos` int,
  `tot_posts` int
  
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

LOCK TABLES `sentimentdata` WRITE;
