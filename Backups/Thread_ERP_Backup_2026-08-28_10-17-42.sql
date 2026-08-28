-- MySQL dump 10.13  Distrib 8.1.0, for Win64 (x86_64)
--
-- Host: localhost    Database: thread_management_db
-- ------------------------------------------------------
-- Server version	8.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `return_dyeing`
--

DROP TABLE IF EXISTS `return_dyeing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_dyeing` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `send_dyeing_id` int NOT NULL,
  `batch_id` varchar(50) NOT NULL,
  `thread_name` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `issued_quantity` int DEFAULT NULL,
  `return_quantity` int NOT NULL,
  `dyeing_info` text,
  `sender` varchar(100) DEFAULT NULL,
  `receiver` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `send_dyeing_id` (`send_dyeing_id`),
  CONSTRAINT `return_dyeing_ibfk_1` FOREIGN KEY (`send_dyeing_id`) REFERENCES `send_dyeing` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_dyeing`
--

LOCK TABLES `return_dyeing` WRITE;
/*!40000 ALTER TABLE `return_dyeing` DISABLE KEYS */;
/*!40000 ALTER TABLE `return_dyeing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `send_dyeing`
--

DROP TABLE IF EXISTS `send_dyeing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `send_dyeing` (
  `id` int NOT NULL AUTO_INCREMENT,
  `batch_id` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `stock_in_id` int DEFAULT NULL,
  `thread_name` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `issued_quantity` int DEFAULT NULL,
  `dyeing_info` text,
  `reason_for_issue` text,
  `sender` varchar(100) DEFAULT NULL,
  `receiver` varchar(100) DEFAULT NULL,
  `expected_return_date` date DEFAULT NULL,
  `status` enum('sent','partial','returned') DEFAULT 'sent',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `stock_in_id` (`stock_in_id`),
  CONSTRAINT `send_dyeing_ibfk_1` FOREIGN KEY (`stock_in_id`) REFERENCES `stock_in` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `send_dyeing`
--

LOCK TABLES `send_dyeing` WRITE;
/*!40000 ALTER TABLE `send_dyeing` DISABLE KEYS */;
/*!40000 ALTER TABLE `send_dyeing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_in`
--

DROP TABLE IF EXISTS `stock_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_in` (
  `id` int NOT NULL AUTO_INCREMENT,
  `po_number` varchar(50) DEFAULT NULL,
  `date` date NOT NULL,
  `supplier_name` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `supplier_cnic` varchar(20) DEFAULT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `thread_name` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `bundle_quantity` int DEFAULT NULL,
  `bundle_price` decimal(10,2) DEFAULT NULL,
  `total_price` decimal(10,2) GENERATED ALWAYS AS ((`bundle_quantity` * `bundle_price`)) STORED,
  `paid_amount` decimal(10,2) DEFAULT '0.00',
  `balance` decimal(10,2) GENERATED ALWAYS AS (((`bundle_quantity` * `bundle_price`) - `paid_amount`)) STORED,
  `status` enum('pending','partial','completed') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `po_number` (`po_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_in`
--

LOCK TABLES `stock_in` WRITE;
/*!40000 ALTER TABLE `stock_in` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_in` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_out`
--

DROP TABLE IF EXISTS `stock_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_out` (
  `id` int NOT NULL AUTO_INCREMENT,
  `so_number` varchar(50) DEFAULT NULL,
  `date` date NOT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `customer_cnic` varchar(20) DEFAULT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `thread_name` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `bundle_quantity` int DEFAULT NULL,
  `issued_by` varchar(100) DEFAULT NULL,
  `bundle_price` decimal(10,2) DEFAULT NULL,
  `total_bundle_price` decimal(10,2) GENERATED ALWAYS AS ((`bundle_quantity` * `bundle_price`)) STORED,
  `discount` decimal(10,2) DEFAULT '0.00',
  `final_total_price` decimal(10,2) GENERATED ALWAYS AS (((`bundle_quantity` * `bundle_price`) - `discount`)) STORED,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `so_number` (`so_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_out`
--

LOCK TABLES `stock_out` WRITE;
/*!40000 ALTER TABLE `stock_out` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_out` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-28 10:17:42
