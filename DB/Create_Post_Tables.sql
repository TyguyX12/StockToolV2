DROP TABLE IF EXISTS `redditposts`;

CREATE TABLE `redditposts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stock` tinytext,
  `TweetText` mediumtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

LOCK TABLES `redditposts` WRITE;


DROP TABLE IF EXISTS `twitterposts`;

CREATE TABLE `twitterposts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stock` tinytext,
  `TweetText` mediumtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

LOCK TABLES `twitterposts` WRITE;
