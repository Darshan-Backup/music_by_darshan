-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 31, 2025 at 08:02 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `newlogin`
--

-- --------------------------------------------------------

--
-- Table structure for table `passwords_backup`
--

DROP TABLE IF EXISTS `passwords_backup`;
CREATE TABLE IF NOT EXISTS `passwords_backup` (
  `pwd_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `org_pwd` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `hash_pwd` varchar(255) NOT NULL,
  PRIMARY KEY (`pwd_id`),
  KEY `user_id_fk` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `passwords_backup`
--

INSERT INTO `passwords_backup` (`pwd_id`, `user_id`, `org_pwd`, `hash_pwd`) VALUES
(1, 33, 'Darshan@2004', 'gAAAAABn6j5oXIYpetzTQOrIGYB7wMn-ejhb49PkOXsGVeLlkZ3QDw9o6FBSE-ubDiECFPKs7lxWu1g9E9h53y2ZA2AmL3LXRw==');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `dob` date NOT NULL,
  `gender` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `dob`, `gender`) VALUES
(33, 'Darshan', 'darshanhulamani77@gmail.com', 'gAAAAABn6j5oXIYpetzTQOrIGYB7wMn-ejhb49PkOXsGVeLlkZ3QDw9o6FBSE-ubDiECFPKs7lxWu1g9E9h53y2ZA2AmL3LXRw==', '2004-05-14', 'Male');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `passwords_backup`
--
ALTER TABLE `passwords_backup`
  ADD CONSTRAINT `user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
