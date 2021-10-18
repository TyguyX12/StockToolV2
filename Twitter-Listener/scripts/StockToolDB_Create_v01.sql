-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema StockToolDB
-- -----------------------------------------------------
-- This database holds the data for the Stock Tool project for Advance Software ENgineering Spring 2021 section 1

-- -----------------------------------------------------
-- Schema StockToolDB
--
-- This database holds the data for the Stock Tool project for Advance Software ENgineering Spring 2021 section 1
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `StockToolDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;
USE `StockToolDB` ;

-- -----------------------------------------------------
-- Table `StockToolDB`.`TwittwerData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `StockToolDB`.`TwitterData` (
  `idTwittwerData` INT NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(255) NOT NULL,
  `DescriptionOfUser` LONGTEXT NOT NULL,
  `Location` MEDIUMTEXT NOT NULL,
  `Following` LONGTEXT NOT NULL,
  `followers` INT NOT NULL,
  `TotalTweets` INT NOT NULL,
  `RetweetCount` INT NOT NULL,
  `Hashtags` LONGTEXT NOT NULL,
  `TweetText` MEDIUMTEXT NOT NULL,
  PRIMARY KEY (`idTwittwerData`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `StockToolDB`.`RedditData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `StockToolDB`.`RedditData` (
  `idRedditData` INT NOT NULL AUTO_INCREMENT,
  `Submission_title` VARCHAR(255) NOT NULL,
  `Submission_name` VARCHAR(255) NOT NULL,
  `Upvote_ratio` FLOAT NOT NULL,
  `Upvotes` INT NOT NULL,
  `Comment` LONGTEXT NOT NULL,
  `Comment_author` LONGTEXT NOT NULL,
  `Flair` LONGTEXT NOT NULL,
  PRIMARY KEY (`idRedditData`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `StockToolDB`.`HistoricalData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `StockToolDB`.`HistoricalData` (
  `idHistoricalData` INT NOT NULL AUTO_INCREMENT,
  `Open` DECIMAL(10,2) NOT NULL,
  `High` DECIMAL(10,2) NOT NULL,
  `Low` DECIMAL(10,2) NOT NULL,
  `Close` DECIMAL(10,2) NOT NULL,
  `MarketCap` DECIMAL(15,2) NOT NULL,
  PRIMARY KEY (`idHistoricalData`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `StockToolDB`.`Stocks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `StockToolDB`.`Stocks` (
  `idStocks` INT NOT NULL AUTO_INCREMENT,
  `StockExchange` VARCHAR(45) NOT NULL,
  `StockSymbol` VARCHAR(45) NOT NULL,
  `StockName` VARCHAR(200) CHARACTER SET 'ascii' NOT NULL,
  PRIMARY KEY (`idStocks`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
