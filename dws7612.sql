-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Erstellungszeit: 12. Feb 2024 um 16:35
-- Server-Version: 10.11.4-MariaDB-1~deb12u1
-- PHP-Version: 8.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `meter`
--
CREATE DATABASE IF NOT EXISTS `meter` DEFAULT CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci;
USE `meter`;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `data`
--

CREATE TABLE IF NOT EXISTS `data` (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) UNSIGNED NOT NULL,
  `time` bigint(20) UNSIGNED NOT NULL,
  `value` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `TIME` (`time`),
  KEY `entity_id` (`entity_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=81906 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


--
-- Tabellenstruktur für Tabelle `entities`
--

CREATE TABLE IF NOT EXISTS `entities` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `description` varchar(128) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

--
-- Daten für Tabelle `entities`
--

INSERT INTO `entities` (`id`, `description`) VALUES
(1, 'gas meter'),
(2, 'electric meter - 1.8.0'),
(3, 'electric meter - 2.8.0');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `properties`
--

CREATE TABLE IF NOT EXISTS `properties` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `entity_id` int(10) UNSIGNED NOT NULL,
  `pkey` varchar(128) NOT NULL,
  `value` tinytext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_id` (`entity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

--
-- Daten für Tabelle `properties`
--

INSERT INTO `properties` (`id`, `entity_id`, `pkey`, `value`) VALUES
(1, 1, 'title', 'Gas'),
(2, 1, 'start', '2810.000'),
(3, 1, 'z', '0.9491'),
(4, 1, 'calorific', '11.563'),
(5, 1, 'rate', '0.1868'),
(6, 1, 'base', '113.05'),
(7, 2, 'title', 'Power (import)'),
(8, 2, 'rate', '30.73'),
(9, 2, 'base', '106.92'),
(10, 3, 'title', 'Power (export)'),
(11, 3, 'rate', '8.11');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
