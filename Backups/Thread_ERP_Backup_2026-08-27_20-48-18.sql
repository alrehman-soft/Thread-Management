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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_dyeing`
--

LOCK TABLES `return_dyeing` WRITE;
/*!40000 ALTER TABLE `return_dyeing` DISABLE KEYS */;
INSERT INTO `return_dyeing` VALUES (6,'2026-08-16',1,'DYE-0001','China','20/2','red',30,30,'do red color on thread','Abid','Ali','2026-08-16 10:04:39','2026-08-16 10:04:39'),(7,'2026-08-23',3,'DYE-0002','Gutermann','30/6','Green',100,100,'Hi','Farhan','Mahir','2026-08-23 07:59:20','2026-08-23 07:59:20'),(8,'2026-08-23',4,'DYE-0003','Tesla','20/2','Blue',100,50,'Any Thing','Ali','Farhan','2026-08-23 08:01:24','2026-08-23 08:01:24'),(9,'2026-08-23',5,'DYE-0004','Western','20/6','Brown',100,40,'Dye Brown Color','Ali','Farhan','2026-08-23 08:01:46','2026-08-23 08:01:46'),(10,'2026-08-23',6,'DYE-0005','Nylon','20/6','Blue',80,80,'For Blue Color','Ali','Farhan','2026-08-23 08:02:01','2026-08-23 08:02:01'),(11,'2026-08-23',7,'DYE-0006','China','20/2','Tan',30,30,'Dye Tan color','Ali','Farhan','2026-08-23 08:02:15','2026-08-23 08:02:15'),(12,'2026-08-23',8,'DYE-0007','Gutermann','30/2','Orange',100,60,'Dye orange color','Ali','Farhan','2026-08-23 08:02:38','2026-08-23 08:02:38'),(13,'2026-08-23',10,'DYE-0009','China','20/3','Gray',50,50,'Dye Gray color','Ali','Farhan','2026-08-23 08:03:50','2026-08-23 08:03:50'),(14,'2026-08-23',11,'DYE-0010','Western','20/6','Red',100,70,'Dye Red color','Ali','Farhan','2026-08-23 08:04:40','2026-08-23 08:04:40'),(15,'2026-08-23',9,'DYE-0008','Nylon','20/6','Green',70,50,'Dye Green color','Ali','Hamza','2026-08-23 08:05:06','2026-08-23 08:05:06');
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
  `status` enum('sent','partial','returned') DEFAULT 'sent',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `expected_return_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stock_in_id` (`stock_in_id`),
  CONSTRAINT `send_dyeing_ibfk_1` FOREIGN KEY (`stock_in_id`) REFERENCES `stock_in` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `send_dyeing`
--

LOCK TABLES `send_dyeing` WRITE;
/*!40000 ALTER TABLE `send_dyeing` DISABLE KEYS */;
INSERT INTO `send_dyeing` VALUES (1,'DYE-0001','2026-04-18',1,'China','20/2',30,'do red color on thread','For customer requirement','Abid','Ali','returned','2026-04-18 15:04:14','2026-08-16 10:04:39','2026-04-22'),(3,'DYE-0002','2026-08-21',9,'Gutermann','30/6',100,'Hi','Dye Green color in Thread','Farhan','Mahir','returned','2026-08-21 14:56:24','2026-08-23 07:59:20','2026-08-27'),(4,'DYE-0003','2026-08-21',8,'Tesla','20/2',100,'Any Thing','Dye blue color in thread','Ali','Farhan','partial','2026-08-21 15:02:03','2026-08-23 08:01:24','2026-08-27'),(5,'DYE-0004','2026-08-22',10,'Western','20/6',100,'Dye Brown Color','For Customer Requirement','Ali','Farhan','partial','2026-08-22 04:57:50','2026-08-23 08:01:46','2026-08-28'),(6,'DYE-0005','2026-08-22',11,'Nylon','20/6',80,'For Blue Color','Thread color change','Ali','Farhan','returned','2026-08-22 05:00:12','2026-08-23 08:02:01','2026-08-28'),(7,'DYE-0006','2026-08-22',1,'China','20/2',30,'Dye Tan color','Change Thread color for customer requirement','Ali','Farhan','returned','2026-08-22 05:16:42','2026-08-23 08:02:15','2026-08-28'),(8,'DYE-0007','2026-08-22',4,'Gutermann','30/2',100,'Dye orange color','For customer Requirement','Ali','Farhan','partial','2026-08-22 05:19:39','2026-08-23 08:02:38','2026-08-28'),(9,'DYE-0008','2026-08-22',11,'Nylon','20/6',70,'Dye Green color','For customer Requirement','Ali','Hamza','partial','2026-08-22 05:53:32','2026-08-23 08:05:53','2026-08-28'),(10,'DYE-0009','2026-08-22',7,'China','20/3',50,'Dye Gray color','For Leather stitching','Ali','Farhan','returned','2026-08-22 06:06:41','2026-08-23 08:03:50','2026-08-28'),(11,'DYE-0010','2026-08-22',10,'Western','20/6',100,'Dye Red color','For highlighter','Ali','Farhan','partial','2026-08-22 06:08:11','2026-08-23 08:04:40','2026-08-28');
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_in`
--

LOCK TABLES `stock_in` WRITE;
/*!40000 ALTER TABLE `stock_in` DISABLE KEYS */;
INSERT INTO `stock_in` (`id`, `po_number`, `date`, `supplier_name`, `phone`, `email`, `supplier_cnic`, `company_name`, `thread_name`, `size`, `bundle_quantity`, `bundle_price`, `paid_amount`, `status`, `created_at`, `updated_at`) VALUES (1,'PO-0001','2026-04-08','Azam','3112345678','azam@gmail.com','4220173729199','Hamza Leather','China','20/2',60,300.00,18000.00,'pending','2026-04-08 05:51:00','2026-08-21 14:29:25'),(3,'PO-0002','2026-08-17','Adil','03224344567','adil@gmail.com','4220177665543','Adil & Co','Tesla','20/6',50,300.00,15000.00,'pending','2026-08-17 09:36:21','2026-08-17 09:36:21'),(4,'PO-0003','2026-08-21','Daniyal','03421122334','dani@gmail.com','4220166655544','Daniyal & Co','Gutermann','30/2',100,400.00,40000.00,'pending','2026-08-21 12:04:51','2026-08-21 12:04:51'),(5,'PO-0004','2026-08-21','Shehryar','03123344888','shery@gmail.com','4220188822233','Shery & Co.','Gutermann','30/3',50,300.00,15000.00,'pending','2026-08-21 12:06:54','2026-08-21 12:06:54'),(6,'PO-0005','2026-08-21','Aqib','03125566778','aqib@gmail.com','4220145667898','Aqib & Co.','Western','30/6',80,350.00,28000.00,'pending','2026-08-21 14:05:15','2026-08-21 14:34:16'),(7,'PO-0006','2026-08-21','Kamran','03203988798','kami@gmail.com','4220104563346','Kamran & Co.','China','20/3',100,250.00,20000.00,'pending','2026-08-21 14:07:15','2026-08-21 14:07:15'),(8,'PO-0007','2026-08-21','Moosa','03112983939','moosa@gmail.com','4220123998786','Moosa & Co.','Tesla','20/2',100,300.00,20000.00,'pending','2026-08-21 14:13:16','2026-08-21 14:13:16'),(9,'PO-0008','2026-08-21','Fayaz','03113899788','fayaz@gmail.com','4220155768899','Fayaz & Co.','Gutermann','30/6',150,250.00,37500.00,'pending','2026-08-21 14:21:46','2026-08-21 14:21:46'),(10,'PO-0009','2026-08-21','Imran','03001122333','Imran@gmail.com','4220122233344','Imran & Co.','Western','20/6',200,250.00,30000.00,'pending','2026-08-21 14:33:26','2026-08-21 14:33:26'),(11,'PO-0010','2026-08-21','Umair','03112223334','umair@gmail.com','4220155566677','Umair & Co.','Nylon','20/6',150,300.00,45000.00,'pending','2026-08-21 14:38:14','2026-08-21 14:38:14');
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_out`
--

LOCK TABLES `stock_out` WRITE;
/*!40000 ALTER TABLE `stock_out` DISABLE KEYS */;
INSERT INTO `stock_out` (`id`, `so_number`, `date`, `customer_name`, `phone`, `email`, `customer_cnic`, `company_name`, `thread_name`, `size`, `color`, `bundle_quantity`, `issued_by`, `bundle_price`, `discount`, `created_at`, `updated_at`) VALUES (1,'SO-0001','2026-08-17','Ali','03865577884','ali@gmail.com','4220198778884','Ali Leather','China','20/2','red',30,'Farhan',1200.00,5000.00,'2026-08-17 05:25:42','2026-08-23 08:50:36'),(2,'SO-0002','2026-08-23','Imran','03001112233','imran@gmail.com','4220122233344','Imran Leather','Nylon','20/6','Blue',80,'Asim',600.00,5000.00,'2026-08-23 08:28:06','2026-08-23 08:28:06'),(3,'SO-0003','2026-08-23','Uzair','03221889944','uzair@gmail.com','4220193837465','uzair & Co.','Gutermann','30/6','Green',60,'Asim',550.00,4000.00,'2026-08-23 08:30:59','2026-08-23 08:30:59'),(4,'SO-0004','2026-08-23','Saad','033247575844','saad@gmail.com','4220188877744','saad & Co.','Tesla','20/2','Blue',50,'Asim',600.00,5000.00,'2026-08-23 08:33:17','2026-08-23 08:33:17'),(5,'SO-0005','2026-08-23','Rehman Ali','03708999666','rehman@gmail.com','4220102334455','Rehman & CO.','Western','20/6','Red',40,'Asim',700.00,4000.00,'2026-08-23 08:43:03','2026-08-23 08:43:03'),(6,'SO-0006','2026-08-23','Kashan','03221119998','kashi@gmail.com','4220166655444','Kashan Merchandizer','China','20/2','Tan',30,'Abdul Raheem',500.00,2000.00,'2026-08-23 08:50:05','2026-08-23 08:50:05'),(7,'SO-0007','2026-08-23','Raza','032218138429','raza@gmail.com','4220172387389','Raza & Co.','China','20/3','Gray',50,'Abdul Rehman',1000.00,6000.00,'2026-08-23 08:51:52','2026-08-23 08:51:52'),(8,'SO-0008','2026-08-23','Bilal','03232238387','bilal@gmail.com','4220165757655','Bilal & Co.','Gutermann','30/2','Orange',60,'Asim',900.00,0.00,'2026-08-23 08:54:04','2026-08-23 09:21:35'),(9,'SO-0009','2026-08-23','Ashraf','03219831291','ashraf@gmail.com','4220192938393','Ashraf & Co.','Nylon','20/6','Green',50,'Asim',700.00,3000.00,'2026-08-23 09:25:54','2026-08-23 09:26:10'),(10,'SO-0010','2026-08-23','M. Waqas','03223848738','waqas@giam.com','4220183483476','Waqar & Sons','Gutermann','30/6','Green',40,'Asim',900.00,0.00,'2026-08-23 09:34:05','2026-08-23 09:34:05');
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

-- Dump completed on 2026-08-27 20:48:19
