-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: bugs
-- ------------------------------------------------------
-- Server version	11.1.2-MariaDB-1:11.1.2+maria~ubu2204

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attach_data`
--

DROP TABLE IF EXISTS `attach_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attach_data` (
  `id` mediumint(9) NOT NULL,
  `thedata` longblob NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_attach_data_id_attachments_attach_id` FOREIGN KEY (`id`) REFERENCES `attachments` (`attach_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=100000 AVG_ROW_LENGTH=1000000;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attach_data`
--

LOCK TABLES `attach_data` WRITE;
/*!40000 ALTER TABLE `attach_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `attach_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attachments`
--

DROP TABLE IF EXISTS `attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attachments` (
  `attach_id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `bug_id` mediumint(9) NOT NULL,
  `creation_ts` datetime NOT NULL,
  `modification_time` datetime NOT NULL,
  `description` tinytext NOT NULL,
  `mimetype` tinytext NOT NULL,
  `ispatch` tinyint(4) NOT NULL DEFAULT 0,
  `filename` varchar(255) NOT NULL,
  `submitter_id` mediumint(9) NOT NULL,
  `isobsolete` tinyint(4) NOT NULL DEFAULT 0,
  `isprivate` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`attach_id`),
  KEY `attachments_bug_id_idx` (`bug_id`),
  KEY `attachments_creation_ts_idx` (`creation_ts`),
  KEY `attachments_modification_time_idx` (`modification_time`),
  KEY `attachments_submitter_id_idx` (`submitter_id`,`bug_id`),
  CONSTRAINT `fk_attachments_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attachments_submitter_id_profiles_userid` FOREIGN KEY (`submitter_id`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachments`
--

LOCK TABLES `attachments` WRITE;
/*!40000 ALTER TABLE `attachments` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audit_log` (
  `user_id` mediumint(9) DEFAULT NULL,
  `class` varchar(255) NOT NULL,
  `object_id` int(11) NOT NULL,
  `field` varchar(64) NOT NULL,
  `removed` mediumtext DEFAULT NULL,
  `added` mediumtext DEFAULT NULL,
  `at_time` datetime NOT NULL,
  KEY `audit_log_class_idx` (`class`,`at_time`),
  KEY `fk_audit_log_user_id_profiles_userid` (`user_id`),
  CONSTRAINT `fk_audit_log_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

LOCK TABLES `audit_log` WRITE;
/*!40000 ALTER TABLE `audit_log` DISABLE KEYS */;
INSERT INTO `audit_log` VALUES (NULL,'Bugzilla::Field',1,'__create__',NULL,'bug_id','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',2,'__create__',NULL,'short_desc','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',3,'__create__',NULL,'classification','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',4,'__create__',NULL,'product','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',5,'__create__',NULL,'version','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',6,'__create__',NULL,'rep_platform','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',7,'__create__',NULL,'bug_file_loc','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',8,'__create__',NULL,'op_sys','2023-09-20 13:12:34'),(NULL,'Bugzilla::Field',9,'__create__',NULL,'bug_status','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',10,'__create__',NULL,'status_whiteboard','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',11,'__create__',NULL,'keywords','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',12,'__create__',NULL,'resolution','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',13,'__create__',NULL,'bug_severity','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',14,'__create__',NULL,'priority','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',15,'__create__',NULL,'component','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',16,'__create__',NULL,'assigned_to','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',17,'__create__',NULL,'reporter','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',18,'__create__',NULL,'qa_contact','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',19,'__create__',NULL,'assigned_to_realname','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',20,'__create__',NULL,'reporter_realname','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',21,'__create__',NULL,'qa_contact_realname','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',22,'__create__',NULL,'cc','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',23,'__create__',NULL,'dependson','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',24,'__create__',NULL,'blocked','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',25,'__create__',NULL,'attachments.description','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',26,'__create__',NULL,'attachments.filename','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',27,'__create__',NULL,'attachments.mimetype','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',28,'__create__',NULL,'attachments.ispatch','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',29,'__create__',NULL,'attachments.isobsolete','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',30,'__create__',NULL,'attachments.isprivate','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',31,'__create__',NULL,'attachments.submitter','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',32,'__create__',NULL,'target_milestone','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',33,'__create__',NULL,'creation_ts','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',34,'__create__',NULL,'delta_ts','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',35,'__create__',NULL,'longdesc','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',36,'__create__',NULL,'longdescs.isprivate','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',37,'__create__',NULL,'longdescs.count','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',38,'__create__',NULL,'alias','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',39,'__create__',NULL,'everconfirmed','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',40,'__create__',NULL,'reporter_accessible','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',41,'__create__',NULL,'cclist_accessible','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',42,'__create__',NULL,'bug_group','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',43,'__create__',NULL,'estimated_time','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',44,'__create__',NULL,'remaining_time','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',45,'__create__',NULL,'deadline','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',46,'__create__',NULL,'commenter','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',47,'__create__',NULL,'flagtypes.name','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',48,'__create__',NULL,'requestees.login_name','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',49,'__create__',NULL,'setters.login_name','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',50,'__create__',NULL,'work_time','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',51,'__create__',NULL,'percentage_complete','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',52,'__create__',NULL,'content','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',53,'__create__',NULL,'attach_data.thedata','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',54,'__create__',NULL,'owner_idle_time','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',55,'__create__',NULL,'see_also','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',56,'__create__',NULL,'tag','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',57,'__create__',NULL,'last_visit_ts','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',58,'__create__',NULL,'comment_tag','2023-09-20 13:12:35'),(NULL,'Bugzilla::Field',59,'__create__',NULL,'days_elapsed','2023-09-20 13:12:35'),(NULL,'Bugzilla::Classification',1,'__create__',NULL,'Unclassified','2023-09-20 13:12:35'),(NULL,'Bugzilla::Group',1,'__create__',NULL,'admin','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',2,'__create__',NULL,'tweakparams','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',3,'__create__',NULL,'editusers','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',4,'__create__',NULL,'creategroups','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',5,'__create__',NULL,'editclassifications','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',6,'__create__',NULL,'editcomponents','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',7,'__create__',NULL,'editkeywords','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',8,'__create__',NULL,'editbugs','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',9,'__create__',NULL,'canconfirm','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',10,'__create__',NULL,'bz_canusewhineatothers','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',11,'__create__',NULL,'bz_canusewhines','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',12,'__create__',NULL,'bz_sudoers','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',13,'__create__',NULL,'bz_sudo_protect','2023-09-20 13:12:40'),(NULL,'Bugzilla::Group',14,'__create__',NULL,'bz_quip_moderators','2023-09-20 13:12:40'),(NULL,'Bugzilla::User',1,'__create__',NULL,'andreas@hasenkopf.xyz','2023-09-20 13:12:55'),(NULL,'Bugzilla::Product',1,'__create__',NULL,'TestProduct','2023-09-20 13:12:55'),(NULL,'Bugzilla::Version',1,'__create__',NULL,'unspecified','2023-09-20 13:12:55'),(NULL,'Bugzilla::Milestone',1,'__create__',NULL,'---','2023-09-20 13:12:55'),(NULL,'Bugzilla::Component',1,'__create__',NULL,'TestComponent','2023-09-20 13:12:55'),(1,'Bugzilla::Product',2,'__create__',NULL,'Red Hat Enterprise Linux 9','2023-11-27 12:25:54'),(1,'Bugzilla::Version',2,'__create__',NULL,'unspecified','2023-11-27 12:25:54'),(1,'Bugzilla::Milestone',2,'__create__',NULL,'---','2023-11-27 12:25:54'),(1,'Bugzilla::Component',2,'__create__',NULL,'python-bugzilla','2023-11-27 12:25:54'),(1,'Bugzilla::Version',3,'__create__',NULL,'9.0','2023-11-27 12:26:06'),(1,'Bugzilla::Version',4,'__create__',NULL,'9.1','2023-11-27 12:26:14'),(1,'Bugzilla::Product',3,'__create__',NULL,'SUSE Linux Enterprise Server 15 SP6','2023-11-27 12:29:18'),(1,'Bugzilla::Version',5,'__create__',NULL,'unspecified','2023-11-27 12:29:18'),(1,'Bugzilla::Milestone',3,'__create__',NULL,'---','2023-11-27 12:29:18'),(1,'Bugzilla::Component',3,'__create__',NULL,'Kernel','2023-11-27 12:29:18'),(1,'Bugzilla::Component',4,'__create__',NULL,'Containers','2023-11-27 12:29:46');
/*!40000 ALTER TABLE `audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_group_map`
--

DROP TABLE IF EXISTS `bug_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_group_map` (
  `bug_id` mediumint(9) NOT NULL,
  `group_id` mediumint(9) NOT NULL,
  UNIQUE KEY `bug_group_map_bug_id_idx` (`bug_id`,`group_id`),
  KEY `bug_group_map_group_id_idx` (`group_id`),
  CONSTRAINT `fk_bug_group_map_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bug_group_map_group_id_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_group_map`
--

LOCK TABLES `bug_group_map` WRITE;
/*!40000 ALTER TABLE `bug_group_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `bug_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_see_also`
--

DROP TABLE IF EXISTS `bug_see_also`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_see_also` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `bug_id` mediumint(9) NOT NULL,
  `value` varchar(255) NOT NULL,
  `class` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `bug_see_also_bug_id_idx` (`bug_id`,`value`),
  CONSTRAINT `fk_bug_see_also_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_see_also`
--

LOCK TABLES `bug_see_also` WRITE;
/*!40000 ALTER TABLE `bug_see_also` DISABLE KEYS */;
/*!40000 ALTER TABLE `bug_see_also` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_severity`
--

DROP TABLE IF EXISTS `bug_severity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_severity` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bug_severity_value_idx` (`value`),
  KEY `bug_severity_sortkey_idx` (`sortkey`,`value`),
  KEY `bug_severity_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_severity`
--

LOCK TABLES `bug_severity` WRITE;
/*!40000 ALTER TABLE `bug_severity` DISABLE KEYS */;
INSERT INTO `bug_severity` VALUES (1,'blocker',100,1,NULL),(2,'critical',200,1,NULL),(3,'major',300,1,NULL),(4,'normal',400,1,NULL),(5,'minor',500,1,NULL),(6,'trivial',600,1,NULL),(7,'enhancement',700,1,NULL);
/*!40000 ALTER TABLE `bug_severity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_status`
--

DROP TABLE IF EXISTS `bug_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_status` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  `is_open` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bug_status_value_idx` (`value`),
  KEY `bug_status_sortkey_idx` (`sortkey`,`value`),
  KEY `bug_status_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_status`
--

LOCK TABLES `bug_status` WRITE;
/*!40000 ALTER TABLE `bug_status` DISABLE KEYS */;
INSERT INTO `bug_status` VALUES (1,'UNCONFIRMED',100,1,NULL,1),(2,'CONFIRMED',200,1,NULL,1),(3,'IN_PROGRESS',300,1,NULL,1),(4,'RESOLVED',400,1,NULL,0),(5,'VERIFIED',500,1,NULL,0);
/*!40000 ALTER TABLE `bug_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_tag`
--

DROP TABLE IF EXISTS `bug_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_tag` (
  `bug_id` mediumint(9) NOT NULL,
  `tag_id` mediumint(9) NOT NULL,
  UNIQUE KEY `bug_tag_bug_id_idx` (`bug_id`,`tag_id`),
  KEY `fk_bug_tag_tag_id_tag_id` (`tag_id`),
  CONSTRAINT `fk_bug_tag_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bug_tag_tag_id_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_tag`
--

LOCK TABLES `bug_tag` WRITE;
/*!40000 ALTER TABLE `bug_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `bug_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_user_last_visit`
--

DROP TABLE IF EXISTS `bug_user_last_visit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_user_last_visit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` mediumint(9) NOT NULL,
  `bug_id` mediumint(9) NOT NULL,
  `last_visit_ts` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bug_user_last_visit_idx` (`user_id`,`bug_id`),
  KEY `bug_user_last_visit_last_visit_ts_idx` (`last_visit_ts`),
  KEY `fk_bug_user_last_visit_bug_id_bugs_bug_id` (`bug_id`),
  CONSTRAINT `fk_bug_user_last_visit_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bug_user_last_visit_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_user_last_visit`
--

LOCK TABLES `bug_user_last_visit` WRITE;
/*!40000 ALTER TABLE `bug_user_last_visit` DISABLE KEYS */;
INSERT INTO `bug_user_last_visit` VALUES (1,1,1,'2023-11-27 15:53:08'),(2,1,2,'2023-11-27 15:38:47');
/*!40000 ALTER TABLE `bug_user_last_visit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bugs`
--

DROP TABLE IF EXISTS `bugs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs` (
  `bug_id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `assigned_to` mediumint(9) NOT NULL,
  `bug_file_loc` mediumtext NOT NULL DEFAULT '',
  `bug_severity` varchar(64) NOT NULL,
  `bug_status` varchar(64) NOT NULL,
  `creation_ts` datetime DEFAULT NULL,
  `delta_ts` datetime NOT NULL,
  `short_desc` varchar(255) NOT NULL,
  `op_sys` varchar(64) NOT NULL,
  `priority` varchar(64) NOT NULL,
  `product_id` smallint(6) NOT NULL,
  `rep_platform` varchar(64) NOT NULL,
  `reporter` mediumint(9) NOT NULL,
  `version` varchar(64) NOT NULL,
  `component_id` mediumint(9) NOT NULL,
  `resolution` varchar(64) NOT NULL DEFAULT '',
  `target_milestone` varchar(64) NOT NULL DEFAULT '---',
  `qa_contact` mediumint(9) DEFAULT NULL,
  `status_whiteboard` mediumtext NOT NULL DEFAULT '',
  `lastdiffed` datetime DEFAULT NULL,
  `everconfirmed` tinyint(4) NOT NULL,
  `reporter_accessible` tinyint(4) NOT NULL DEFAULT 1,
  `cclist_accessible` tinyint(4) NOT NULL DEFAULT 1,
  `estimated_time` decimal(7,2) NOT NULL DEFAULT 0.00,
  `remaining_time` decimal(7,2) NOT NULL DEFAULT 0.00,
  `deadline` datetime DEFAULT NULL,
  PRIMARY KEY (`bug_id`),
  KEY `bugs_assigned_to_idx` (`assigned_to`),
  KEY `bugs_creation_ts_idx` (`creation_ts`),
  KEY `bugs_delta_ts_idx` (`delta_ts`),
  KEY `bugs_bug_severity_idx` (`bug_severity`),
  KEY `bugs_bug_status_idx` (`bug_status`),
  KEY `bugs_op_sys_idx` (`op_sys`),
  KEY `bugs_priority_idx` (`priority`),
  KEY `bugs_product_id_idx` (`product_id`),
  KEY `bugs_reporter_idx` (`reporter`),
  KEY `bugs_version_idx` (`version`),
  KEY `bugs_component_id_idx` (`component_id`),
  KEY `bugs_resolution_idx` (`resolution`),
  KEY `bugs_target_milestone_idx` (`target_milestone`),
  KEY `bugs_qa_contact_idx` (`qa_contact`),
  CONSTRAINT `fk_bugs_assigned_to_profiles_userid` FOREIGN KEY (`assigned_to`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_component_id_components_id` FOREIGN KEY (`component_id`) REFERENCES `components` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_qa_contact_profiles_userid` FOREIGN KEY (`qa_contact`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_reporter_profiles_userid` FOREIGN KEY (`reporter`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs`
--

LOCK TABLES `bugs` WRITE;
/*!40000 ALTER TABLE `bugs` DISABLE KEYS */;
INSERT INTO `bugs` VALUES (1,1,'','major','IN_PROGRESS','2023-11-27 15:35:33','2023-11-27 15:53:04','ZeroDivisionError in function foo_bar()','Linux','---',3,'PC',1,'unspecified',4,'','---',NULL,'AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L','2023-11-27 15:53:04',1,1,1,0.00,0.00,NULL),(2,1,'','enhancement','CONFIRMED','2023-11-27 15:38:45','2023-11-27 15:38:45','Expect the Spanish inquisition','Linux','---',2,'PC',1,'9.1',2,'','---',NULL,'','2023-11-27 15:38:45',1,1,1,0.00,0.00,NULL);
/*!40000 ALTER TABLE `bugs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bugs_activity`
--

DROP TABLE IF EXISTS `bugs_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs_activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bug_id` mediumint(9) NOT NULL,
  `attach_id` mediumint(9) DEFAULT NULL,
  `who` mediumint(9) NOT NULL,
  `bug_when` datetime NOT NULL,
  `fieldid` mediumint(9) NOT NULL,
  `added` varchar(255) DEFAULT NULL,
  `removed` varchar(255) DEFAULT NULL,
  `comment_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bugs_activity_bug_id_idx` (`bug_id`),
  KEY `bugs_activity_who_idx` (`who`),
  KEY `bugs_activity_bug_when_idx` (`bug_when`),
  KEY `bugs_activity_fieldid_idx` (`fieldid`),
  KEY `bugs_activity_added_idx` (`added`),
  KEY `bugs_activity_removed_idx` (`removed`),
  KEY `fk_bugs_activity_attach_id_attachments_attach_id` (`attach_id`),
  KEY `fk_bugs_activity_comment_id_longdescs_comment_id` (`comment_id`),
  CONSTRAINT `fk_bugs_activity_attach_id_attachments_attach_id` FOREIGN KEY (`attach_id`) REFERENCES `attachments` (`attach_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_activity_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_activity_comment_id_longdescs_comment_id` FOREIGN KEY (`comment_id`) REFERENCES `longdescs` (`comment_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_activity_fieldid_fielddefs_id` FOREIGN KEY (`fieldid`) REFERENCES `fielddefs` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_bugs_activity_who_profiles_userid` FOREIGN KEY (`who`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs_activity`
--

LOCK TABLES `bugs_activity` WRITE;
/*!40000 ALTER TABLE `bugs_activity` DISABLE KEYS */;
INSERT INTO `bugs_activity` VALUES (1,1,NULL,1,'2023-11-27 15:45:09',9,'IN_PROGRESS','CONFIRMED',NULL),(2,1,NULL,1,'2023-11-27 15:47:58',10,'AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L','',NULL),(3,1,NULL,1,'2023-11-27 15:53:04',38,'FOO-1','',NULL);
/*!40000 ALTER TABLE `bugs_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bugs_aliases`
--

DROP TABLE IF EXISTS `bugs_aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs_aliases` (
  `alias` varchar(40) NOT NULL,
  `bug_id` mediumint(9) DEFAULT NULL,
  UNIQUE KEY `bugs_aliases_alias_idx` (`alias`),
  KEY `bugs_aliases_bug_id_idx` (`bug_id`),
  CONSTRAINT `fk_bugs_aliases_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs_aliases`
--

LOCK TABLES `bugs_aliases` WRITE;
/*!40000 ALTER TABLE `bugs_aliases` DISABLE KEYS */;
INSERT INTO `bugs_aliases` VALUES ('FOO-1',1);
/*!40000 ALTER TABLE `bugs_aliases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bugs_fulltext`
--

DROP TABLE IF EXISTS `bugs_fulltext`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs_fulltext` (
  `bug_id` mediumint(9) NOT NULL,
  `short_desc` varchar(255) NOT NULL,
  `comments` mediumtext DEFAULT NULL,
  `comments_noprivate` mediumtext DEFAULT NULL,
  PRIMARY KEY (`bug_id`),
  FULLTEXT KEY `bugs_fulltext_short_desc_idx` (`short_desc`),
  FULLTEXT KEY `bugs_fulltext_comments_idx` (`comments`),
  FULLTEXT KEY `bugs_fulltext_comments_noprivate_idx` (`comments_noprivate`),
  CONSTRAINT `fk_bugs_fulltext_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs_fulltext`
--

LOCK TABLES `bugs_fulltext` WRITE;
/*!40000 ALTER TABLE `bugs_fulltext` DISABLE KEYS */;
INSERT INTO `bugs_fulltext` VALUES (1,'ZeroDivisionError in function foo_bar()','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nAt vero eos et accusam et justo duo dolores et ea rebum.\nStet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.','Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nAt vero eos et accusam et justo duo dolores et ea rebum.\nStet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.'),(2,'Expect the Spanish inquisition','Nobody expects the Spanish Inquisition! \n\nOur chief weapon is surprise, surprise and fear, fear and surprise. \n\nOur two weapons are fear and surprise, and ruthless efficiency. \n\nOur three weapons are fear and surprise and ruthless efficiency and an almost fanatical dedication to the pope.','Nobody expects the Spanish Inquisition! \n\nOur chief weapon is surprise, surprise and fear, fear and surprise. \n\nOur two weapons are fear and surprise, and ruthless efficiency. \n\nOur three weapons are fear and surprise and ruthless efficiency and an almost fanatical dedication to the pope.');
/*!40000 ALTER TABLE `bugs_fulltext` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bz_schema`
--

DROP TABLE IF EXISTS `bz_schema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bz_schema` (
  `schema_data` longblob NOT NULL,
  `version` decimal(3,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bz_schema`
--

LOCK TABLES `bz_schema` WRITE;
/*!40000 ALTER TABLE `bz_schema` DISABLE KEYS */;
INSERT INTO `bz_schema` VALUES ('$VAR1 = {\n          \'attach_data\' => {\n                             \'FIELDS\' => [\n                                           \'id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'PRIMARYKEY\' => 1,\n                                             \'REFERENCES\' => {\n                                                               \'COLUMN\' => \'attach_id\',\n                                                               \'DELETE\' => \'CASCADE\',\n                                                               \'TABLE\' => \'attachments\',\n                                                               \'created\' => 1\n                                                             },\n                                             \'TYPE\' => \'INT3\'\n                                           },\n                                           \'thedata\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'LONGBLOB\'\n                                           }\n                                         ]\n                           },\n          \'attachments\' => {\n                             \'FIELDS\' => [\n                                           \'attach_id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'PRIMARYKEY\' => 1,\n                                             \'TYPE\' => \'MEDIUMSERIAL\'\n                                           },\n                                           \'bug_id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'REFERENCES\' => {\n                                                               \'COLUMN\' => \'bug_id\',\n                                                               \'DELETE\' => \'CASCADE\',\n                                                               \'TABLE\' => \'bugs\',\n                                                               \'created\' => 1\n                                                             },\n                                             \'TYPE\' => \'INT3\'\n                                           },\n                                           \'creation_ts\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'DATETIME\'\n                                           },\n                                           \'modification_time\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'DATETIME\'\n                                           },\n                                           \'description\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'TINYTEXT\'\n                                           },\n                                           \'mimetype\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'TINYTEXT\'\n                                           },\n                                           \'ispatch\',\n                                           {\n                                             \'DEFAULT\' => \'FALSE\',\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'BOOLEAN\'\n                                           },\n                                           \'filename\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'varchar(255)\'\n                                           },\n                                           \'submitter_id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'REFERENCES\' => {\n                                                               \'COLUMN\' => \'userid\',\n                                                               \'TABLE\' => \'profiles\',\n                                                               \'created\' => 1\n                                                             },\n                                             \'TYPE\' => \'INT3\'\n                                           },\n                                           \'isobsolete\',\n                                           {\n                                             \'DEFAULT\' => \'FALSE\',\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'BOOLEAN\'\n                                           },\n                                           \'isprivate\',\n                                           {\n                                             \'DEFAULT\' => \'FALSE\',\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'BOOLEAN\'\n                                           }\n                                         ],\n                             \'INDEXES\' => [\n                                            \'attachments_bug_id_idx\',\n                                            [\n                                              \'bug_id\'\n                                            ],\n                                            \'attachments_creation_ts_idx\',\n                                            [\n                                              \'creation_ts\'\n                                            ],\n                                            \'attachments_modification_time_idx\',\n                                            [\n                                              \'modification_time\'\n                                            ],\n                                            \'attachments_submitter_id_idx\',\n                                            [\n                                              \'submitter_id\',\n                                              \'bug_id\'\n                                            ]\n                                          ]\n                           },\n          \'audit_log\' => {\n                           \'FIELDS\' => [\n                                         \'user_id\',\n                                         {\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'userid\',\n                                                             \'DELETE\' => \'SET NULL\',\n                                                             \'TABLE\' => \'profiles\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'class\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'varchar(255)\'\n                                         },\n                                         \'object_id\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'INT4\'\n                                         },\n                                         \'field\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'varchar(64)\'\n                                         },\n                                         \'removed\',\n                                         {\n                                           \'TYPE\' => \'MEDIUMTEXT\'\n                                         },\n                                         \'added\',\n                                         {\n                                           \'TYPE\' => \'MEDIUMTEXT\'\n                                         },\n                                         \'at_time\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'DATETIME\'\n                                         }\n                                       ],\n                           \'INDEXES\' => [\n                                          \'audit_log_class_idx\',\n                                          [\n                                            \'class\',\n                                            \'at_time\'\n                                          ]\n                                        ]\n                         },\n          \'bug_group_map\' => {\n                               \'FIELDS\' => [\n                                             \'bug_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'bug_id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'bugs\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'group_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'groups\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'bug_group_map_bug_id_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'bug_id\',\n                                                              \'group_id\'\n                                                            ],\n                                                \'TYPE\' => \'UNIQUE\'\n                                              },\n                                              \'bug_group_map_group_id_idx\',\n                                              [\n                                                \'group_id\'\n                                              ]\n                                            ]\n                             },\n          \'bug_see_also\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'MEDIUMSERIAL\'\n                                            },\n                                            \'bug_id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'bug_id\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'bugs\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'value\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(255)\'\n                                            },\n                                            \'class\',\n                                            {\n                                              \'DEFAULT\' => \'\\\'\\\'\',\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(255)\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'bug_see_also_bug_id_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'bug_id\',\n                                                             \'value\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             }\n                                           ]\n                            },\n          \'bug_severity\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'SMALLSERIAL\'\n                                            },\n                                            \'value\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(64)\'\n                                            },\n                                            \'sortkey\',\n                                            {\n                                              \'DEFAULT\' => 0,\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'INT2\'\n                                            },\n                                            \'isactive\',\n                                            {\n                                              \'DEFAULT\' => \'TRUE\',\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'BOOLEAN\'\n                                            },\n                                            \'visibility_value_id\',\n                                            {\n                                              \'TYPE\' => \'INT2\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'bug_severity_value_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'value\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             },\n                                             \'bug_severity_sortkey_idx\',\n                                             [\n                                               \'sortkey\',\n                                               \'value\'\n                                             ],\n                                             \'bug_severity_visibility_value_id_idx\',\n                                             [\n                                               \'visibility_value_id\'\n                                             ]\n                                           ]\n                            },\n          \'bug_status\' => {\n                            \'FIELDS\' => [\n                                          \'id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'TYPE\' => \'SMALLSERIAL\'\n                                          },\n                                          \'value\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'varchar(64)\'\n                                          },\n                                          \'sortkey\',\n                                          {\n                                            \'DEFAULT\' => 0,\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'isactive\',\n                                          {\n                                            \'DEFAULT\' => \'TRUE\',\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'BOOLEAN\'\n                                          },\n                                          \'visibility_value_id\',\n                                          {\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'is_open\',\n                                          {\n                                            \'DEFAULT\' => \'TRUE\',\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'BOOLEAN\'\n                                          }\n                                        ],\n                            \'INDEXES\' => [\n                                           \'bug_status_value_idx\',\n                                           {\n                                             \'FIELDS\' => [\n                                                           \'value\'\n                                                         ],\n                                             \'TYPE\' => \'UNIQUE\'\n                                           },\n                                           \'bug_status_sortkey_idx\',\n                                           [\n                                             \'sortkey\',\n                                             \'value\'\n                                           ],\n                                           \'bug_status_visibility_value_id_idx\',\n                                           [\n                                             \'visibility_value_id\'\n                                           ]\n                                         ]\n                          },\n          \'bug_tag\' => {\n                         \'FIELDS\' => [\n                                       \'bug_id\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'REFERENCES\' => {\n                                                           \'COLUMN\' => \'bug_id\',\n                                                           \'DELETE\' => \'CASCADE\',\n                                                           \'TABLE\' => \'bugs\',\n                                                           \'created\' => 1\n                                                         },\n                                         \'TYPE\' => \'INT3\'\n                                       },\n                                       \'tag_id\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'REFERENCES\' => {\n                                                           \'COLUMN\' => \'id\',\n                                                           \'DELETE\' => \'CASCADE\',\n                                                           \'TABLE\' => \'tag\',\n                                                           \'created\' => 1\n                                                         },\n                                         \'TYPE\' => \'INT3\'\n                                       }\n                                     ],\n                         \'INDEXES\' => [\n                                        \'bug_tag_bug_id_idx\',\n                                        {\n                                          \'FIELDS\' => [\n                                                        \'bug_id\',\n                                                        \'tag_id\'\n                                                      ],\n                                          \'TYPE\' => \'UNIQUE\'\n                                        }\n                                      ]\n                       },\n          \'bug_user_last_visit\' => {\n                                     \'FIELDS\' => [\n                                                   \'id\',\n                                                   {\n                                                     \'NOTNULL\' => 1,\n                                                     \'PRIMARYKEY\' => 1,\n                                                     \'TYPE\' => \'INTSERIAL\'\n                                                   },\n                                                   \'user_id\',\n                                                   {\n                                                     \'NOTNULL\' => 1,\n                                                     \'REFERENCES\' => {\n                                                                       \'COLUMN\' => \'userid\',\n                                                                       \'DELETE\' => \'CASCADE\',\n                                                                       \'TABLE\' => \'profiles\',\n                                                                       \'created\' => 1\n                                                                     },\n                                                     \'TYPE\' => \'INT3\'\n                                                   },\n                                                   \'bug_id\',\n                                                   {\n                                                     \'NOTNULL\' => 1,\n                                                     \'REFERENCES\' => {\n                                                                       \'COLUMN\' => \'bug_id\',\n                                                                       \'DELETE\' => \'CASCADE\',\n                                                                       \'TABLE\' => \'bugs\',\n                                                                       \'created\' => 1\n                                                                     },\n                                                     \'TYPE\' => \'INT3\'\n                                                   },\n                                                   \'last_visit_ts\',\n                                                   {\n                                                     \'NOTNULL\' => 1,\n                                                     \'TYPE\' => \'DATETIME\'\n                                                   }\n                                                 ],\n                                     \'INDEXES\' => [\n                                                    \'bug_user_last_visit_idx\',\n                                                    {\n                                                      \'FIELDS\' => [\n                                                                    \'user_id\',\n                                                                    \'bug_id\'\n                                                                  ],\n                                                      \'TYPE\' => \'UNIQUE\'\n                                                    },\n                                                    \'bug_user_last_visit_last_visit_ts_idx\',\n                                                    [\n                                                      \'last_visit_ts\'\n                                                    ]\n                                                  ]\n                                   },\n          \'bugs\' => {\n                      \'FIELDS\' => [\n                                    \'bug_id\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'PRIMARYKEY\' => 1,\n                                      \'TYPE\' => \'MEDIUMSERIAL\'\n                                    },\n                                    \'assigned_to\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'REFERENCES\' => {\n                                                        \'COLUMN\' => \'userid\',\n                                                        \'TABLE\' => \'profiles\',\n                                                        \'created\' => 1\n                                                      },\n                                      \'TYPE\' => \'INT3\'\n                                    },\n                                    \'bug_file_loc\',\n                                    {\n                                      \'DEFAULT\' => \'\\\'\\\'\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'MEDIUMTEXT\'\n                                    },\n                                    \'bug_severity\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'bug_status\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'creation_ts\',\n                                    {\n                                      \'TYPE\' => \'DATETIME\'\n                                    },\n                                    \'delta_ts\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'DATETIME\'\n                                    },\n                                    \'short_desc\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(255)\'\n                                    },\n                                    \'op_sys\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'priority\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'product_id\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'REFERENCES\' => {\n                                                        \'COLUMN\' => \'id\',\n                                                        \'TABLE\' => \'products\',\n                                                        \'created\' => 1\n                                                      },\n                                      \'TYPE\' => \'INT2\'\n                                    },\n                                    \'rep_platform\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'reporter\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'REFERENCES\' => {\n                                                        \'COLUMN\' => \'userid\',\n                                                        \'TABLE\' => \'profiles\',\n                                                        \'created\' => 1\n                                                      },\n                                      \'TYPE\' => \'INT3\'\n                                    },\n                                    \'version\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'component_id\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'REFERENCES\' => {\n                                                        \'COLUMN\' => \'id\',\n                                                        \'TABLE\' => \'components\',\n                                                        \'created\' => 1\n                                                      },\n                                      \'TYPE\' => \'INT3\'\n                                    },\n                                    \'resolution\',\n                                    {\n                                      \'DEFAULT\' => \'\\\'\\\'\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'target_milestone\',\n                                    {\n                                      \'DEFAULT\' => \'\\\'---\\\'\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'varchar(64)\'\n                                    },\n                                    \'qa_contact\',\n                                    {\n                                      \'REFERENCES\' => {\n                                                        \'COLUMN\' => \'userid\',\n                                                        \'TABLE\' => \'profiles\',\n                                                        \'created\' => 1\n                                                      },\n                                      \'TYPE\' => \'INT3\'\n                                    },\n                                    \'status_whiteboard\',\n                                    {\n                                      \'DEFAULT\' => \'\\\'\\\'\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'MEDIUMTEXT\'\n                                    },\n                                    \'lastdiffed\',\n                                    {\n                                      \'TYPE\' => \'DATETIME\'\n                                    },\n                                    \'everconfirmed\',\n                                    {\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'BOOLEAN\'\n                                    },\n                                    \'reporter_accessible\',\n                                    {\n                                      \'DEFAULT\' => \'TRUE\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'BOOLEAN\'\n                                    },\n                                    \'cclist_accessible\',\n                                    {\n                                      \'DEFAULT\' => \'TRUE\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'BOOLEAN\'\n                                    },\n                                    \'estimated_time\',\n                                    {\n                                      \'DEFAULT\' => \'0\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'decimal(7,2)\'\n                                    },\n                                    \'remaining_time\',\n                                    {\n                                      \'DEFAULT\' => \'0\',\n                                      \'NOTNULL\' => 1,\n                                      \'TYPE\' => \'decimal(7,2)\'\n                                    },\n                                    \'deadline\',\n                                    {\n                                      \'TYPE\' => \'DATETIME\'\n                                    }\n                                  ],\n                      \'INDEXES\' => [\n                                     \'bugs_assigned_to_idx\',\n                                     [\n                                       \'assigned_to\'\n                                     ],\n                                     \'bugs_creation_ts_idx\',\n                                     [\n                                       \'creation_ts\'\n                                     ],\n                                     \'bugs_delta_ts_idx\',\n                                     [\n                                       \'delta_ts\'\n                                     ],\n                                     \'bugs_bug_severity_idx\',\n                                     [\n                                       \'bug_severity\'\n                                     ],\n                                     \'bugs_bug_status_idx\',\n                                     [\n                                       \'bug_status\'\n                                     ],\n                                     \'bugs_op_sys_idx\',\n                                     [\n                                       \'op_sys\'\n                                     ],\n                                     \'bugs_priority_idx\',\n                                     [\n                                       \'priority\'\n                                     ],\n                                     \'bugs_product_id_idx\',\n                                     [\n                                       \'product_id\'\n                                     ],\n                                     \'bugs_reporter_idx\',\n                                     [\n                                       \'reporter\'\n                                     ],\n                                     \'bugs_version_idx\',\n                                     [\n                                       \'version\'\n                                     ],\n                                     \'bugs_component_id_idx\',\n                                     [\n                                       \'component_id\'\n                                     ],\n                                     \'bugs_resolution_idx\',\n                                     [\n                                       \'resolution\'\n                                     ],\n                                     \'bugs_target_milestone_idx\',\n                                     [\n                                       \'target_milestone\'\n                                     ],\n                                     \'bugs_qa_contact_idx\',\n                                     [\n                                       \'qa_contact\'\n                                     ]\n                                   ]\n                    },\n          \'bugs_activity\' => {\n                               \'FIELDS\' => [\n                                             \'id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'PRIMARYKEY\' => 1,\n                                               \'TYPE\' => \'INTSERIAL\'\n                                             },\n                                             \'bug_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'bug_id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'bugs\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'attach_id\',\n                                             {\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'attach_id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'attachments\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'who\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'userid\',\n                                                                 \'TABLE\' => \'profiles\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'bug_when\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'DATETIME\'\n                                             },\n                                             \'fieldid\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'id\',\n                                                                 \'TABLE\' => \'fielddefs\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'added\',\n                                             {\n                                               \'TYPE\' => \'varchar(255)\'\n                                             },\n                                             \'removed\',\n                                             {\n                                               \'TYPE\' => \'varchar(255)\'\n                                             },\n                                             \'comment_id\',\n                                             {\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'comment_id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'longdescs\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT4\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'bugs_activity_bug_id_idx\',\n                                              [\n                                                \'bug_id\'\n                                              ],\n                                              \'bugs_activity_who_idx\',\n                                              [\n                                                \'who\'\n                                              ],\n                                              \'bugs_activity_bug_when_idx\',\n                                              [\n                                                \'bug_when\'\n                                              ],\n                                              \'bugs_activity_fieldid_idx\',\n                                              [\n                                                \'fieldid\'\n                                              ],\n                                              \'bugs_activity_added_idx\',\n                                              [\n                                                \'added\'\n                                              ],\n                                              \'bugs_activity_removed_idx\',\n                                              [\n                                                \'removed\'\n                                              ]\n                                            ]\n                             },\n          \'bugs_aliases\' => {\n                              \'FIELDS\' => [\n                                            \'alias\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(40)\'\n                                            },\n                                            \'bug_id\',\n                                            {\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'bug_id\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'bugs\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'bugs_aliases_bug_id_idx\',\n                                             [\n                                               \'bug_id\'\n                                             ],\n                                             \'bugs_aliases_alias_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'alias\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             }\n                                           ]\n                            },\n          \'bugs_fulltext\' => {\n                               \'FIELDS\' => [\n                                             \'bug_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'PRIMARYKEY\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'bug_id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'bugs\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'short_desc\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'varchar(255)\'\n                                             },\n                                             \'comments\',\n                                             {\n                                               \'TYPE\' => \'LONGTEXT\'\n                                             },\n                                             \'comments_noprivate\',\n                                             {\n                                               \'TYPE\' => \'LONGTEXT\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'bugs_fulltext_short_desc_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'short_desc\'\n                                                            ],\n                                                \'TYPE\' => \'FULLTEXT\'\n                                              },\n                                              \'bugs_fulltext_comments_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'comments\'\n                                                            ],\n                                                \'TYPE\' => \'FULLTEXT\'\n                                              },\n                                              \'bugs_fulltext_comments_noprivate_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'comments_noprivate\'\n                                                            ],\n                                                \'TYPE\' => \'FULLTEXT\'\n                                              }\n                                            ]\n                             },\n          \'bz_schema\' => {\n                           \'FIELDS\' => [\n                                         \'schema_data\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'LONGBLOB\'\n                                         },\n                                         \'version\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'decimal(3,2)\'\n                                         }\n                                       ]\n                         },\n          \'category_group_map\' => {\n                                    \'FIELDS\' => [\n                                                  \'category_id\',\n                                                  {\n                                                    \'NOTNULL\' => 1,\n                                                    \'REFERENCES\' => {\n                                                                      \'COLUMN\' => \'id\',\n                                                                      \'DELETE\' => \'CASCADE\',\n                                                                      \'TABLE\' => \'series_categories\',\n                                                                      \'created\' => 1\n                                                                    },\n                                                    \'TYPE\' => \'INT2\'\n                                                  },\n                                                  \'group_id\',\n                                                  {\n                                                    \'NOTNULL\' => 1,\n                                                    \'REFERENCES\' => {\n                                                                      \'COLUMN\' => \'id\',\n                                                                      \'DELETE\' => \'CASCADE\',\n                                                                      \'TABLE\' => \'groups\',\n                                                                      \'created\' => 1\n                                                                    },\n                                                    \'TYPE\' => \'INT3\'\n                                                  }\n                                                ],\n                                    \'INDEXES\' => [\n                                                   \'category_group_map_category_id_idx\',\n                                                   {\n                                                     \'FIELDS\' => [\n                                                                   \'category_id\',\n                                                                   \'group_id\'\n                                                                 ],\n                                                     \'TYPE\' => \'UNIQUE\'\n                                                   }\n                                                 ]\n                                  },\n          \'cc\' => {\n                    \'FIELDS\' => [\n                                  \'bug_id\',\n                                  {\n                                    \'NOTNULL\' => 1,\n                                    \'REFERENCES\' => {\n                                                      \'COLUMN\' => \'bug_id\',\n                                                      \'DELETE\' => \'CASCADE\',\n                                                      \'TABLE\' => \'bugs\',\n                                                      \'created\' => 1\n                                                    },\n                                    \'TYPE\' => \'INT3\'\n                                  },\n                                  \'who\',\n                                  {\n                                    \'NOTNULL\' => 1,\n                                    \'REFERENCES\' => {\n                                                      \'COLUMN\' => \'userid\',\n                                                      \'DELETE\' => \'CASCADE\',\n                                                      \'TABLE\' => \'profiles\',\n                                                      \'created\' => 1\n                                                    },\n                                    \'TYPE\' => \'INT3\'\n                                  }\n                                ],\n                    \'INDEXES\' => [\n                                   \'cc_bug_id_idx\',\n                                   {\n                                     \'FIELDS\' => [\n                                                   \'bug_id\',\n                                                   \'who\'\n                                                 ],\n                                     \'TYPE\' => \'UNIQUE\'\n                                   },\n                                   \'cc_who_idx\',\n                                   [\n                                     \'who\'\n                                   ]\n                                 ]\n                  },\n          \'classifications\' => {\n                                 \'FIELDS\' => [\n                                               \'id\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'PRIMARYKEY\' => 1,\n                                                 \'TYPE\' => \'SMALLSERIAL\'\n                                               },\n                                               \'name\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'varchar(64)\'\n                                               },\n                                               \'description\',\n                                               {\n                                                 \'TYPE\' => \'MEDIUMTEXT\'\n                                               },\n                                               \'sortkey\',\n                                               {\n                                                 \'DEFAULT\' => \'0\',\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'INT2\'\n                                               }\n                                             ],\n                                 \'INDEXES\' => [\n                                                \'classifications_name_idx\',\n                                                {\n                                                  \'FIELDS\' => [\n                                                                \'name\'\n                                                              ],\n                                                  \'TYPE\' => \'UNIQUE\'\n                                                }\n                                              ]\n                               },\n          \'component_cc\' => {\n                              \'FIELDS\' => [\n                                            \'user_id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'userid\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'profiles\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'component_id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'id\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'components\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'component_cc_user_id_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'component_id\',\n                                                             \'user_id\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             }\n                                           ]\n                            },\n          \'components\' => {\n                            \'FIELDS\' => [\n                                          \'id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'TYPE\' => \'MEDIUMSERIAL\'\n                                          },\n                                          \'name\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'varchar(64)\'\n                                          },\n                                          \'product_id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'id\',\n                                                              \'DELETE\' => \'CASCADE\',\n                                                              \'TABLE\' => \'products\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'initialowner\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'userid\',\n                                                              \'TABLE\' => \'profiles\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT3\'\n                                          },\n                                          \'initialqacontact\',\n                                          {\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'userid\',\n                                                              \'DELETE\' => \'SET NULL\',\n                                                              \'TABLE\' => \'profiles\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT3\'\n                                          },\n                                          \'description\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'MEDIUMTEXT\'\n                                          },\n                                          \'isactive\',\n                                          {\n                                            \'DEFAULT\' => \'TRUE\',\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'BOOLEAN\'\n                                          }\n                                        ],\n                            \'INDEXES\' => [\n                                           \'components_product_id_idx\',\n                                           {\n                                             \'FIELDS\' => [\n                                                           \'product_id\',\n                                                           \'name\'\n                                                         ],\n                                             \'TYPE\' => \'UNIQUE\'\n                                           },\n                                           \'components_name_idx\',\n                                           [\n                                             \'name\'\n                                           ]\n                                         ]\n                          },\n          \'dependencies\' => {\n                              \'FIELDS\' => [\n                                            \'blocked\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'bug_id\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'bugs\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'dependson\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'bug_id\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'bugs\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'dependencies_blocked_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'blocked\',\n                                                             \'dependson\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             },\n                                             \'dependencies_dependson_idx\',\n                                             [\n                                               \'dependson\'\n                                             ]\n                                           ]\n                            },\n          \'duplicates\' => {\n                            \'FIELDS\' => [\n                                          \'dupe_of\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'bug_id\',\n                                                              \'DELETE\' => \'CASCADE\',\n                                                              \'TABLE\' => \'bugs\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT3\'\n                                          },\n                                          \'dupe\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'bug_id\',\n                                                              \'DELETE\' => \'CASCADE\',\n                                                              \'TABLE\' => \'bugs\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT3\'\n                                          }\n                                        ]\n                          },\n          \'email_bug_ignore\' => {\n                                  \'FIELDS\' => [\n                                                \'user_id\',\n                                                {\n                                                  \'NOTNULL\' => 1,\n                                                  \'REFERENCES\' => {\n                                                                    \'COLUMN\' => \'userid\',\n                                                                    \'DELETE\' => \'CASCADE\',\n                                                                    \'TABLE\' => \'profiles\',\n                                                                    \'created\' => 1\n                                                                  },\n                                                  \'TYPE\' => \'INT3\'\n                                                },\n                                                \'bug_id\',\n                                                {\n                                                  \'NOTNULL\' => 1,\n                                                  \'REFERENCES\' => {\n                                                                    \'COLUMN\' => \'bug_id\',\n                                                                    \'DELETE\' => \'CASCADE\',\n                                                                    \'TABLE\' => \'bugs\',\n                                                                    \'created\' => 1\n                                                                  },\n                                                  \'TYPE\' => \'INT3\'\n                                                }\n                                              ],\n                                  \'INDEXES\' => [\n                                                 \'email_bug_ignore_user_id_idx\',\n                                                 {\n                                                   \'FIELDS\' => [\n                                                                 \'user_id\',\n                                                                 \'bug_id\'\n                                                               ],\n                                                   \'TYPE\' => \'UNIQUE\'\n                                                 }\n                                               ]\n                                },\n          \'email_setting\' => {\n                               \'FIELDS\' => [\n                                             \'user_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'userid\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'profiles\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'relationship\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'INT1\'\n                                             },\n                                             \'event\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'INT1\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'email_setting_user_id_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'user_id\',\n                                                              \'relationship\',\n                                                              \'event\'\n                                                            ],\n                                                \'TYPE\' => \'UNIQUE\'\n                                              }\n                                            ]\n                             },\n          \'field_visibility\' => {\n                                  \'FIELDS\' => [\n                                                \'field_id\',\n                                                {\n                                                  \'REFERENCES\' => {\n                                                                    \'COLUMN\' => \'id\',\n                                                                    \'DELETE\' => \'CASCADE\',\n                                                                    \'TABLE\' => \'fielddefs\',\n                                                                    \'created\' => 1\n                                                                  },\n                                                  \'TYPE\' => \'INT3\'\n                                                },\n                                                \'value_id\',\n                                                {\n                                                  \'NOTNULL\' => 1,\n                                                  \'TYPE\' => \'INT2\'\n                                                }\n                                              ],\n                                  \'INDEXES\' => [\n                                                 \'field_visibility_field_id_idx\',\n                                                 {\n                                                   \'FIELDS\' => [\n                                                                 \'field_id\',\n                                                                 \'value_id\'\n                                                               ],\n                                                   \'TYPE\' => \'UNIQUE\'\n                                                 }\n                                               ]\n                                },\n          \'fielddefs\' => {\n                           \'FIELDS\' => [\n                                         \'id\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'PRIMARYKEY\' => 1,\n                                           \'TYPE\' => \'MEDIUMSERIAL\'\n                                         },\n                                         \'name\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'varchar(64)\'\n                                         },\n                                         \'type\',\n                                         {\n                                           \'DEFAULT\' => 0,\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'INT2\'\n                                         },\n                                         \'custom\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'description\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'TINYTEXT\'\n                                         },\n                                         \'long_desc\',\n                                         {\n                                           \'DEFAULT\' => \'\\\'\\\'\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'varchar(255)\'\n                                         },\n                                         \'mailhead\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'sortkey\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'INT2\'\n                                         },\n                                         \'obsolete\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'enter_bug\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'buglist\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'visibility_field_id\',\n                                         {\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'id\',\n                                                             \'TABLE\' => \'fielddefs\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'value_field_id\',\n                                         {\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'id\',\n                                                             \'TABLE\' => \'fielddefs\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'reverse_desc\',\n                                         {\n                                           \'TYPE\' => \'TINYTEXT\'\n                                         },\n                                         \'is_mandatory\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'is_numeric\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         }\n                                       ],\n                           \'INDEXES\' => [\n                                          \'fielddefs_name_idx\',\n                                          {\n                                            \'FIELDS\' => [\n                                                          \'name\'\n                                                        ],\n                                            \'TYPE\' => \'UNIQUE\'\n                                          },\n                                          \'fielddefs_sortkey_idx\',\n                                          [\n                                            \'sortkey\'\n                                          ],\n                                          \'fielddefs_value_field_id_idx\',\n                                          [\n                                            \'value_field_id\'\n                                          ],\n                                          \'fielddefs_is_mandatory_idx\',\n                                          [\n                                            \'is_mandatory\'\n                                          ]\n                                        ]\n                         },\n          \'flagexclusions\' => {\n                                \'FIELDS\' => [\n                                              \'type_id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'flagtypes\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              },\n                                              \'product_id\',\n                                              {\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'products\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT2\'\n                                              },\n                                              \'component_id\',\n                                              {\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'components\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              }\n                                            ],\n                                \'INDEXES\' => [\n                                               \'flagexclusions_type_id_idx\',\n                                               {\n                                                 \'FIELDS\' => [\n                                                               \'type_id\',\n                                                               \'product_id\',\n                                                               \'component_id\'\n                                                             ],\n                                                 \'TYPE\' => \'UNIQUE\'\n                                               }\n                                             ]\n                              },\n          \'flaginclusions\' => {\n                                \'FIELDS\' => [\n                                              \'type_id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'flagtypes\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              },\n                                              \'product_id\',\n                                              {\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'products\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT2\'\n                                              },\n                                              \'component_id\',\n                                              {\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'components\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              }\n                                            ],\n                                \'INDEXES\' => [\n                                               \'flaginclusions_type_id_idx\',\n                                               {\n                                                 \'FIELDS\' => [\n                                                               \'type_id\',\n                                                               \'product_id\',\n                                                               \'component_id\'\n                                                             ],\n                                                 \'TYPE\' => \'UNIQUE\'\n                                               }\n                                             ]\n                              },\n          \'flags\' => {\n                       \'FIELDS\' => [\n                                     \'id\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'PRIMARYKEY\' => 1,\n                                       \'TYPE\' => \'MEDIUMSERIAL\'\n                                     },\n                                     \'type_id\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'id\',\n                                                         \'DELETE\' => \'CASCADE\',\n                                                         \'TABLE\' => \'flagtypes\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'status\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'TYPE\' => \'char(1)\'\n                                     },\n                                     \'bug_id\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'bug_id\',\n                                                         \'DELETE\' => \'CASCADE\',\n                                                         \'TABLE\' => \'bugs\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'attach_id\',\n                                     {\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'attach_id\',\n                                                         \'DELETE\' => \'CASCADE\',\n                                                         \'TABLE\' => \'attachments\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'creation_date\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'TYPE\' => \'DATETIME\'\n                                     },\n                                     \'modification_date\',\n                                     {\n                                       \'TYPE\' => \'DATETIME\'\n                                     },\n                                     \'setter_id\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'userid\',\n                                                         \'TABLE\' => \'profiles\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'requestee_id\',\n                                     {\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'userid\',\n                                                         \'TABLE\' => \'profiles\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     }\n                                   ],\n                       \'INDEXES\' => [\n                                      \'flags_bug_id_idx\',\n                                      [\n                                        \'bug_id\',\n                                        \'attach_id\'\n                                      ],\n                                      \'flags_setter_id_idx\',\n                                      [\n                                        \'setter_id\'\n                                      ],\n                                      \'flags_requestee_id_idx\',\n                                      [\n                                        \'requestee_id\'\n                                      ],\n                                      \'flags_type_id_idx\',\n                                      [\n                                        \'type_id\'\n                                      ]\n                                    ]\n                     },\n          \'flagtypes\' => {\n                           \'FIELDS\' => [\n                                         \'id\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'PRIMARYKEY\' => 1,\n                                           \'TYPE\' => \'MEDIUMSERIAL\'\n                                         },\n                                         \'name\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'varchar(50)\'\n                                         },\n                                         \'description\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'MEDIUMTEXT\'\n                                         },\n                                         \'cc_list\',\n                                         {\n                                           \'TYPE\' => \'varchar(200)\'\n                                         },\n                                         \'target_type\',\n                                         {\n                                           \'DEFAULT\' => \'\\\'b\\\'\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'char(1)\'\n                                         },\n                                         \'is_active\',\n                                         {\n                                           \'DEFAULT\' => \'TRUE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'is_requestable\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'is_requesteeble\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'is_multiplicable\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'sortkey\',\n                                         {\n                                           \'DEFAULT\' => \'0\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'INT2\'\n                                         },\n                                         \'grant_group_id\',\n                                         {\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'id\',\n                                                             \'DELETE\' => \'SET NULL\',\n                                                             \'TABLE\' => \'groups\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'request_group_id\',\n                                         {\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'id\',\n                                                             \'DELETE\' => \'SET NULL\',\n                                                             \'TABLE\' => \'groups\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         }\n                                       ]\n                         },\n          \'group_control_map\' => {\n                                   \'FIELDS\' => [\n                                                 \'group_id\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'REFERENCES\' => {\n                                                                     \'COLUMN\' => \'id\',\n                                                                     \'DELETE\' => \'CASCADE\',\n                                                                     \'TABLE\' => \'groups\',\n                                                                     \'created\' => 1\n                                                                   },\n                                                   \'TYPE\' => \'INT3\'\n                                                 },\n                                                 \'product_id\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'REFERENCES\' => {\n                                                                     \'COLUMN\' => \'id\',\n                                                                     \'DELETE\' => \'CASCADE\',\n                                                                     \'TABLE\' => \'products\',\n                                                                     \'created\' => 1\n                                                                   },\n                                                   \'TYPE\' => \'INT2\'\n                                                 },\n                                                 \'entry\',\n                                                 {\n                                                   \'DEFAULT\' => \'FALSE\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'BOOLEAN\'\n                                                 },\n                                                 \'membercontrol\',\n                                                 {\n                                                   \'DEFAULT\' => \'0\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'INT1\'\n                                                 },\n                                                 \'othercontrol\',\n                                                 {\n                                                   \'DEFAULT\' => \'0\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'INT1\'\n                                                 },\n                                                 \'canedit\',\n                                                 {\n                                                   \'DEFAULT\' => \'FALSE\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'BOOLEAN\'\n                                                 },\n                                                 \'editcomponents\',\n                                                 {\n                                                   \'DEFAULT\' => \'FALSE\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'BOOLEAN\'\n                                                 },\n                                                 \'editbugs\',\n                                                 {\n                                                   \'DEFAULT\' => \'FALSE\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'BOOLEAN\'\n                                                 },\n                                                 \'canconfirm\',\n                                                 {\n                                                   \'DEFAULT\' => \'FALSE\',\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'BOOLEAN\'\n                                                 }\n                                               ],\n                                   \'INDEXES\' => [\n                                                  \'group_control_map_product_id_idx\',\n                                                  {\n                                                    \'FIELDS\' => [\n                                                                  \'product_id\',\n                                                                  \'group_id\'\n                                                                ],\n                                                    \'TYPE\' => \'UNIQUE\'\n                                                  },\n                                                  \'group_control_map_group_id_idx\',\n                                                  [\n                                                    \'group_id\'\n                                                  ]\n                                                ]\n                                 },\n          \'group_group_map\' => {\n                                 \'FIELDS\' => [\n                                               \'member_id\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'id\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'groups\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT3\'\n                                               },\n                                               \'grantor_id\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'id\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'groups\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT3\'\n                                               },\n                                               \'grant_type\',\n                                               {\n                                                 \'DEFAULT\' => \'0\',\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'INT1\'\n                                               }\n                                             ],\n                                 \'INDEXES\' => [\n                                                \'group_group_map_member_id_idx\',\n                                                {\n                                                  \'FIELDS\' => [\n                                                                \'member_id\',\n                                                                \'grantor_id\',\n                                                                \'grant_type\'\n                                                              ],\n                                                  \'TYPE\' => \'UNIQUE\'\n                                                }\n                                              ]\n                               },\n          \'groups\' => {\n                        \'FIELDS\' => [\n                                      \'id\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'PRIMARYKEY\' => 1,\n                                        \'TYPE\' => \'MEDIUMSERIAL\'\n                                      },\n                                      \'name\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'varchar(255)\'\n                                      },\n                                      \'description\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'MEDIUMTEXT\'\n                                      },\n                                      \'isbuggroup\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'BOOLEAN\'\n                                      },\n                                      \'userregexp\',\n                                      {\n                                        \'DEFAULT\' => \'\\\'\\\'\',\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'TINYTEXT\'\n                                      },\n                                      \'isactive\',\n                                      {\n                                        \'DEFAULT\' => \'TRUE\',\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'BOOLEAN\'\n                                      },\n                                      \'icon_url\',\n                                      {\n                                        \'TYPE\' => \'TINYTEXT\'\n                                      }\n                                    ],\n                        \'INDEXES\' => [\n                                       \'groups_name_idx\',\n                                       {\n                                         \'FIELDS\' => [\n                                                       \'name\'\n                                                     ],\n                                         \'TYPE\' => \'UNIQUE\'\n                                       }\n                                     ]\n                      },\n          \'keyworddefs\' => {\n                             \'FIELDS\' => [\n                                           \'id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'PRIMARYKEY\' => 1,\n                                             \'TYPE\' => \'SMALLSERIAL\'\n                                           },\n                                           \'name\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'varchar(64)\'\n                                           },\n                                           \'description\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'MEDIUMTEXT\'\n                                           }\n                                         ],\n                             \'INDEXES\' => [\n                                            \'keyworddefs_name_idx\',\n                                            {\n                                              \'FIELDS\' => [\n                                                            \'name\'\n                                                          ],\n                                              \'TYPE\' => \'UNIQUE\'\n                                            }\n                                          ]\n                           },\n          \'keywords\' => {\n                          \'FIELDS\' => [\n                                        \'bug_id\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'REFERENCES\' => {\n                                                            \'COLUMN\' => \'bug_id\',\n                                                            \'DELETE\' => \'CASCADE\',\n                                                            \'TABLE\' => \'bugs\',\n                                                            \'created\' => 1\n                                                          },\n                                          \'TYPE\' => \'INT3\'\n                                        },\n                                        \'keywordid\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'REFERENCES\' => {\n                                                            \'COLUMN\' => \'id\',\n                                                            \'DELETE\' => \'CASCADE\',\n                                                            \'TABLE\' => \'keyworddefs\',\n                                                            \'created\' => 1\n                                                          },\n                                          \'TYPE\' => \'INT2\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'keywords_bug_id_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'bug_id\',\n                                                         \'keywordid\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         },\n                                         \'keywords_keywordid_idx\',\n                                         [\n                                           \'keywordid\'\n                                         ]\n                                       ]\n                        },\n          \'login_failure\' => {\n                               \'FIELDS\' => [\n                                             \'user_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'userid\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'profiles\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'login_time\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'DATETIME\'\n                                             },\n                                             \'ip_addr\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'varchar(40)\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'login_failure_user_id_idx\',\n                                              [\n                                                \'user_id\'\n                                              ]\n                                            ]\n                             },\n          \'logincookies\' => {\n                              \'FIELDS\' => [\n                                            \'cookie\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'varchar(16)\'\n                                            },\n                                            \'userid\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'userid\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'profiles\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'ipaddr\',\n                                            {\n                                              \'TYPE\' => \'varchar(40)\'\n                                            },\n                                            \'lastused\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'DATETIME\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'logincookies_lastused_idx\',\n                                             [\n                                               \'lastused\'\n                                             ]\n                                           ]\n                            },\n          \'longdescs\' => {\n                           \'FIELDS\' => [\n                                         \'comment_id\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'PRIMARYKEY\' => 1,\n                                           \'TYPE\' => \'INTSERIAL\'\n                                         },\n                                         \'bug_id\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'bug_id\',\n                                                             \'DELETE\' => \'CASCADE\',\n                                                             \'TABLE\' => \'bugs\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'who\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'REFERENCES\' => {\n                                                             \'COLUMN\' => \'userid\',\n                                                             \'TABLE\' => \'profiles\',\n                                                             \'created\' => 1\n                                                           },\n                                           \'TYPE\' => \'INT3\'\n                                         },\n                                         \'bug_when\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'DATETIME\'\n                                         },\n                                         \'work_time\',\n                                         {\n                                           \'DEFAULT\' => \'0\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'decimal(7,2)\'\n                                         },\n                                         \'thetext\',\n                                         {\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'LONGTEXT\'\n                                         },\n                                         \'isprivate\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'already_wrapped\',\n                                         {\n                                           \'DEFAULT\' => \'FALSE\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'BOOLEAN\'\n                                         },\n                                         \'type\',\n                                         {\n                                           \'DEFAULT\' => \'0\',\n                                           \'NOTNULL\' => 1,\n                                           \'TYPE\' => \'INT2\'\n                                         },\n                                         \'extra_data\',\n                                         {\n                                           \'TYPE\' => \'varchar(255)\'\n                                         }\n                                       ],\n                           \'INDEXES\' => [\n                                          \'longdescs_bug_id_idx\',\n                                          [\n                                            \'bug_id\',\n                                            \'work_time\'\n                                          ],\n                                          \'longdescs_who_idx\',\n                                          [\n                                            \'who\',\n                                            \'bug_id\'\n                                          ],\n                                          \'longdescs_bug_when_idx\',\n                                          [\n                                            \'bug_when\'\n                                          ]\n                                        ]\n                         },\n          \'longdescs_tags\' => {\n                                \'FIELDS\' => [\n                                              \'id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'PRIMARYKEY\' => 1,\n                                                \'TYPE\' => \'MEDIUMSERIAL\'\n                                              },\n                                              \'comment_id\',\n                                              {\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'comment_id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'longdescs\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT4\'\n                                              },\n                                              \'tag\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'TYPE\' => \'varchar(24)\'\n                                              }\n                                            ],\n                                \'INDEXES\' => [\n                                               \'longdescs_tags_idx\',\n                                               {\n                                                 \'FIELDS\' => [\n                                                               \'comment_id\',\n                                                               \'tag\'\n                                                             ],\n                                                 \'TYPE\' => \'UNIQUE\'\n                                               }\n                                             ]\n                              },\n          \'longdescs_tags_activity\' => {\n                                         \'FIELDS\' => [\n                                                       \'id\',\n                                                       {\n                                                         \'NOTNULL\' => 1,\n                                                         \'PRIMARYKEY\' => 1,\n                                                         \'TYPE\' => \'MEDIUMSERIAL\'\n                                                       },\n                                                       \'bug_id\',\n                                                       {\n                                                         \'NOTNULL\' => 1,\n                                                         \'REFERENCES\' => {\n                                                                           \'COLUMN\' => \'bug_id\',\n                                                                           \'DELETE\' => \'CASCADE\',\n                                                                           \'TABLE\' => \'bugs\',\n                                                                           \'created\' => 1\n                                                                         },\n                                                         \'TYPE\' => \'INT3\'\n                                                       },\n                                                       \'comment_id\',\n                                                       {\n                                                         \'REFERENCES\' => {\n                                                                           \'COLUMN\' => \'comment_id\',\n                                                                           \'DELETE\' => \'CASCADE\',\n                                                                           \'TABLE\' => \'longdescs\',\n                                                                           \'created\' => 1\n                                                                         },\n                                                         \'TYPE\' => \'INT4\'\n                                                       },\n                                                       \'who\',\n                                                       {\n                                                         \'NOTNULL\' => 1,\n                                                         \'REFERENCES\' => {\n                                                                           \'COLUMN\' => \'userid\',\n                                                                           \'TABLE\' => \'profiles\',\n                                                                           \'created\' => 1\n                                                                         },\n                                                         \'TYPE\' => \'INT3\'\n                                                       },\n                                                       \'bug_when\',\n                                                       {\n                                                         \'NOTNULL\' => 1,\n                                                         \'TYPE\' => \'DATETIME\'\n                                                       },\n                                                       \'added\',\n                                                       {\n                                                         \'TYPE\' => \'varchar(24)\'\n                                                       },\n                                                       \'removed\',\n                                                       {\n                                                         \'TYPE\' => \'varchar(24)\'\n                                                       }\n                                                     ],\n                                         \'INDEXES\' => [\n                                                        \'longdescs_tags_activity_bug_id_idx\',\n                                                        [\n                                                          \'bug_id\'\n                                                        ]\n                                                      ]\n                                       },\n          \'longdescs_tags_weights\' => {\n                                        \'FIELDS\' => [\n                                                      \'id\',\n                                                      {\n                                                        \'NOTNULL\' => 1,\n                                                        \'PRIMARYKEY\' => 1,\n                                                        \'TYPE\' => \'MEDIUMSERIAL\'\n                                                      },\n                                                      \'tag\',\n                                                      {\n                                                        \'NOTNULL\' => 1,\n                                                        \'TYPE\' => \'varchar(24)\'\n                                                      },\n                                                      \'weight\',\n                                                      {\n                                                        \'NOTNULL\' => 1,\n                                                        \'TYPE\' => \'INT3\'\n                                                      }\n                                                    ],\n                                        \'INDEXES\' => [\n                                                       \'longdescs_tags_weights_tag_idx\',\n                                                       {\n                                                         \'FIELDS\' => [\n                                                                       \'tag\'\n                                                                     ],\n                                                         \'TYPE\' => \'UNIQUE\'\n                                                       }\n                                                     ]\n                                      },\n          \'mail_staging\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'INTSERIAL\'\n                                            },\n                                            \'message\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'LONGBLOB\'\n                                            }\n                                          ]\n                            },\n          \'milestones\' => {\n                            \'FIELDS\' => [\n                                          \'id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'TYPE\' => \'MEDIUMSERIAL\'\n                                          },\n                                          \'product_id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'REFERENCES\' => {\n                                                              \'COLUMN\' => \'id\',\n                                                              \'DELETE\' => \'CASCADE\',\n                                                              \'TABLE\' => \'products\',\n                                                              \'created\' => 1\n                                                            },\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'value\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'varchar(64)\'\n                                          },\n                                          \'sortkey\',\n                                          {\n                                            \'DEFAULT\' => 0,\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'isactive\',\n                                          {\n                                            \'DEFAULT\' => \'TRUE\',\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'BOOLEAN\'\n                                          }\n                                        ],\n                            \'INDEXES\' => [\n                                           \'milestones_product_id_idx\',\n                                           {\n                                             \'FIELDS\' => [\n                                                           \'product_id\',\n                                                           \'value\'\n                                                         ],\n                                             \'TYPE\' => \'UNIQUE\'\n                                           }\n                                         ]\n                          },\n          \'namedqueries\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'MEDIUMSERIAL\'\n                                            },\n                                            \'userid\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'userid\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'profiles\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'name\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(64)\'\n                                            },\n                                            \'query\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'LONGTEXT\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'namedqueries_userid_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'userid\',\n                                                             \'name\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             }\n                                           ]\n                            },\n          \'namedqueries_link_in_footer\' => {\n                                             \'FIELDS\' => [\n                                                           \'namedquery_id\',\n                                                           {\n                                                             \'NOTNULL\' => 1,\n                                                             \'REFERENCES\' => {\n                                                                               \'COLUMN\' => \'id\',\n                                                                               \'DELETE\' => \'CASCADE\',\n                                                                               \'TABLE\' => \'namedqueries\',\n                                                                               \'created\' => 1\n                                                                             },\n                                                             \'TYPE\' => \'INT3\'\n                                                           },\n                                                           \'user_id\',\n                                                           {\n                                                             \'NOTNULL\' => 1,\n                                                             \'REFERENCES\' => {\n                                                                               \'COLUMN\' => \'userid\',\n                                                                               \'DELETE\' => \'CASCADE\',\n                                                                               \'TABLE\' => \'profiles\',\n                                                                               \'created\' => 1\n                                                                             },\n                                                             \'TYPE\' => \'INT3\'\n                                                           }\n                                                         ],\n                                             \'INDEXES\' => [\n                                                            \'namedqueries_link_in_footer_id_idx\',\n                                                            {\n                                                              \'FIELDS\' => [\n                                                                            \'namedquery_id\',\n                                                                            \'user_id\'\n                                                                          ],\n                                                              \'TYPE\' => \'UNIQUE\'\n                                                            },\n                                                            \'namedqueries_link_in_footer_userid_idx\',\n                                                            [\n                                                              \'user_id\'\n                                                            ]\n                                                          ]\n                                           },\n          \'namedquery_group_map\' => {\n                                      \'FIELDS\' => [\n                                                    \'namedquery_id\',\n                                                    {\n                                                      \'NOTNULL\' => 1,\n                                                      \'REFERENCES\' => {\n                                                                        \'COLUMN\' => \'id\',\n                                                                        \'DELETE\' => \'CASCADE\',\n                                                                        \'TABLE\' => \'namedqueries\',\n                                                                        \'created\' => 1\n                                                                      },\n                                                      \'TYPE\' => \'INT3\'\n                                                    },\n                                                    \'group_id\',\n                                                    {\n                                                      \'NOTNULL\' => 1,\n                                                      \'REFERENCES\' => {\n                                                                        \'COLUMN\' => \'id\',\n                                                                        \'DELETE\' => \'CASCADE\',\n                                                                        \'TABLE\' => \'groups\',\n                                                                        \'created\' => 1\n                                                                      },\n                                                      \'TYPE\' => \'INT3\'\n                                                    }\n                                                  ],\n                                      \'INDEXES\' => [\n                                                     \'namedquery_group_map_namedquery_id_idx\',\n                                                     {\n                                                       \'FIELDS\' => [\n                                                                     \'namedquery_id\'\n                                                                   ],\n                                                       \'TYPE\' => \'UNIQUE\'\n                                                     },\n                                                     \'namedquery_group_map_group_id_idx\',\n                                                     [\n                                                       \'group_id\'\n                                                     ]\n                                                   ]\n                                    },\n          \'op_sys\' => {\n                        \'FIELDS\' => [\n                                      \'id\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'PRIMARYKEY\' => 1,\n                                        \'TYPE\' => \'SMALLSERIAL\'\n                                      },\n                                      \'value\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'varchar(64)\'\n                                      },\n                                      \'sortkey\',\n                                      {\n                                        \'DEFAULT\' => 0,\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'INT2\'\n                                      },\n                                      \'isactive\',\n                                      {\n                                        \'DEFAULT\' => \'TRUE\',\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'BOOLEAN\'\n                                      },\n                                      \'visibility_value_id\',\n                                      {\n                                        \'TYPE\' => \'INT2\'\n                                      }\n                                    ],\n                        \'INDEXES\' => [\n                                       \'op_sys_value_idx\',\n                                       {\n                                         \'FIELDS\' => [\n                                                       \'value\'\n                                                     ],\n                                         \'TYPE\' => \'UNIQUE\'\n                                       },\n                                       \'op_sys_sortkey_idx\',\n                                       [\n                                         \'sortkey\',\n                                         \'value\'\n                                       ],\n                                       \'op_sys_visibility_value_id_idx\',\n                                       [\n                                         \'visibility_value_id\'\n                                       ]\n                                     ]\n                      },\n          \'priority\' => {\n                          \'FIELDS\' => [\n                                        \'id\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'PRIMARYKEY\' => 1,\n                                          \'TYPE\' => \'SMALLSERIAL\'\n                                        },\n                                        \'value\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(64)\'\n                                        },\n                                        \'sortkey\',\n                                        {\n                                          \'DEFAULT\' => 0,\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'INT2\'\n                                        },\n                                        \'isactive\',\n                                        {\n                                          \'DEFAULT\' => \'TRUE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        },\n                                        \'visibility_value_id\',\n                                        {\n                                          \'TYPE\' => \'INT2\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'priority_value_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'value\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         },\n                                         \'priority_sortkey_idx\',\n                                         [\n                                           \'sortkey\',\n                                           \'value\'\n                                         ],\n                                         \'priority_visibility_value_id_idx\',\n                                         [\n                                           \'visibility_value_id\'\n                                         ]\n                                       ]\n                        },\n          \'products\' => {\n                          \'FIELDS\' => [\n                                        \'id\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'PRIMARYKEY\' => 1,\n                                          \'TYPE\' => \'SMALLSERIAL\'\n                                        },\n                                        \'name\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(64)\'\n                                        },\n                                        \'classification_id\',\n                                        {\n                                          \'DEFAULT\' => \'1\',\n                                          \'NOTNULL\' => 1,\n                                          \'REFERENCES\' => {\n                                                            \'COLUMN\' => \'id\',\n                                                            \'DELETE\' => \'CASCADE\',\n                                                            \'TABLE\' => \'classifications\',\n                                                            \'created\' => 1\n                                                          },\n                                          \'TYPE\' => \'INT2\'\n                                        },\n                                        \'description\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'MEDIUMTEXT\'\n                                        },\n                                        \'isactive\',\n                                        {\n                                          \'DEFAULT\' => 1,\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        },\n                                        \'defaultmilestone\',\n                                        {\n                                          \'DEFAULT\' => \'\\\'---\\\'\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(64)\'\n                                        },\n                                        \'allows_unconfirmed\',\n                                        {\n                                          \'DEFAULT\' => \'TRUE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'products_name_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'name\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         }\n                                       ]\n                        },\n          \'profile_search\' => {\n                                \'FIELDS\' => [\n                                              \'id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'PRIMARYKEY\' => 1,\n                                                \'TYPE\' => \'INTSERIAL\'\n                                              },\n                                              \'user_id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'userid\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'profiles\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              },\n                                              \'bug_list\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'TYPE\' => \'MEDIUMTEXT\'\n                                              },\n                                              \'list_order\',\n                                              {\n                                                \'TYPE\' => \'MEDIUMTEXT\'\n                                              }\n                                            ],\n                                \'INDEXES\' => [\n                                               \'profile_search_user_id_idx\',\n                                               [\n                                                 \'user_id\'\n                                               ]\n                                             ]\n                              },\n          \'profile_setting\' => {\n                                 \'FIELDS\' => [\n                                               \'user_id\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'userid\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'profiles\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT3\'\n                                               },\n                                               \'setting_name\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'name\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'setting\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'varchar(32)\'\n                                               },\n                                               \'setting_value\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'varchar(32)\'\n                                               }\n                                             ],\n                                 \'INDEXES\' => [\n                                                \'profile_setting_value_unique_idx\',\n                                                {\n                                                  \'FIELDS\' => [\n                                                                \'user_id\',\n                                                                \'setting_name\'\n                                                              ],\n                                                  \'TYPE\' => \'UNIQUE\'\n                                                }\n                                              ]\n                               },\n          \'profiles\' => {\n                          \'FIELDS\' => [\n                                        \'userid\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'PRIMARYKEY\' => 1,\n                                          \'TYPE\' => \'MEDIUMSERIAL\'\n                                        },\n                                        \'login_name\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(255)\'\n                                        },\n                                        \'cryptpassword\',\n                                        {\n                                          \'TYPE\' => \'varchar(128)\'\n                                        },\n                                        \'realname\',\n                                        {\n                                          \'DEFAULT\' => \'\\\'\\\'\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(255)\'\n                                        },\n                                        \'disabledtext\',\n                                        {\n                                          \'DEFAULT\' => \'\\\'\\\'\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'MEDIUMTEXT\'\n                                        },\n                                        \'disable_mail\',\n                                        {\n                                          \'DEFAULT\' => \'FALSE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        },\n                                        \'mybugslink\',\n                                        {\n                                          \'DEFAULT\' => \'TRUE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        },\n                                        \'extern_id\',\n                                        {\n                                          \'TYPE\' => \'varchar(64)\'\n                                        },\n                                        \'is_enabled\',\n                                        {\n                                          \'DEFAULT\' => \'TRUE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        },\n                                        \'last_seen_date\',\n                                        {\n                                          \'TYPE\' => \'DATETIME\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'profiles_login_name_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'login_name\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         },\n                                         \'profiles_extern_id_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'extern_id\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         }\n                                       ]\n                        },\n          \'profiles_activity\' => {\n                                   \'FIELDS\' => [\n                                                 \'id\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'PRIMARYKEY\' => 1,\n                                                   \'TYPE\' => \'MEDIUMSERIAL\'\n                                                 },\n                                                 \'userid\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'REFERENCES\' => {\n                                                                     \'COLUMN\' => \'userid\',\n                                                                     \'DELETE\' => \'CASCADE\',\n                                                                     \'TABLE\' => \'profiles\',\n                                                                     \'created\' => 1\n                                                                   },\n                                                   \'TYPE\' => \'INT3\'\n                                                 },\n                                                 \'who\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'REFERENCES\' => {\n                                                                     \'COLUMN\' => \'userid\',\n                                                                     \'TABLE\' => \'profiles\',\n                                                                     \'created\' => 1\n                                                                   },\n                                                   \'TYPE\' => \'INT3\'\n                                                 },\n                                                 \'profiles_when\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'DATETIME\'\n                                                 },\n                                                 \'fieldid\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'REFERENCES\' => {\n                                                                     \'COLUMN\' => \'id\',\n                                                                     \'TABLE\' => \'fielddefs\',\n                                                                     \'created\' => 1\n                                                                   },\n                                                   \'TYPE\' => \'INT3\'\n                                                 },\n                                                 \'oldvalue\',\n                                                 {\n                                                   \'TYPE\' => \'TINYTEXT\'\n                                                 },\n                                                 \'newvalue\',\n                                                 {\n                                                   \'TYPE\' => \'TINYTEXT\'\n                                                 }\n                                               ],\n                                   \'INDEXES\' => [\n                                                  \'profiles_activity_userid_idx\',\n                                                  [\n                                                    \'userid\'\n                                                  ],\n                                                  \'profiles_activity_profiles_when_idx\',\n                                                  [\n                                                    \'profiles_when\'\n                                                  ],\n                                                  \'profiles_activity_fieldid_idx\',\n                                                  [\n                                                    \'fieldid\'\n                                                  ]\n                                                ]\n                                 },\n          \'quips\' => {\n                       \'FIELDS\' => [\n                                     \'quipid\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'PRIMARYKEY\' => 1,\n                                       \'TYPE\' => \'MEDIUMSERIAL\'\n                                     },\n                                     \'userid\',\n                                     {\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'userid\',\n                                                         \'DELETE\' => \'SET NULL\',\n                                                         \'TABLE\' => \'profiles\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'quip\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'TYPE\' => \'varchar(512)\'\n                                     },\n                                     \'approved\',\n                                     {\n                                       \'DEFAULT\' => \'TRUE\',\n                                       \'NOTNULL\' => 1,\n                                       \'TYPE\' => \'BOOLEAN\'\n                                     }\n                                   ]\n                     },\n          \'rep_platform\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'SMALLSERIAL\'\n                                            },\n                                            \'value\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'varchar(64)\'\n                                            },\n                                            \'sortkey\',\n                                            {\n                                              \'DEFAULT\' => 0,\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'INT2\'\n                                            },\n                                            \'isactive\',\n                                            {\n                                              \'DEFAULT\' => \'TRUE\',\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'BOOLEAN\'\n                                            },\n                                            \'visibility_value_id\',\n                                            {\n                                              \'TYPE\' => \'INT2\'\n                                            }\n                                          ],\n                              \'INDEXES\' => [\n                                             \'rep_platform_value_idx\',\n                                             {\n                                               \'FIELDS\' => [\n                                                             \'value\'\n                                                           ],\n                                               \'TYPE\' => \'UNIQUE\'\n                                             },\n                                             \'rep_platform_sortkey_idx\',\n                                             [\n                                               \'sortkey\',\n                                               \'value\'\n                                             ],\n                                             \'rep_platform_visibility_value_id_idx\',\n                                             [\n                                               \'visibility_value_id\'\n                                             ]\n                                           ]\n                            },\n          \'reports\' => {\n                         \'FIELDS\' => [\n                                       \'id\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'PRIMARYKEY\' => 1,\n                                         \'TYPE\' => \'MEDIUMSERIAL\'\n                                       },\n                                       \'user_id\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'REFERENCES\' => {\n                                                           \'COLUMN\' => \'userid\',\n                                                           \'DELETE\' => \'CASCADE\',\n                                                           \'TABLE\' => \'profiles\',\n                                                           \'created\' => 1\n                                                         },\n                                         \'TYPE\' => \'INT3\'\n                                       },\n                                       \'name\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'TYPE\' => \'varchar(64)\'\n                                       },\n                                       \'query\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'TYPE\' => \'LONGTEXT\'\n                                       }\n                                     ],\n                         \'INDEXES\' => [\n                                        \'reports_user_id_idx\',\n                                        {\n                                          \'FIELDS\' => [\n                                                        \'user_id\',\n                                                        \'name\'\n                                                      ],\n                                          \'TYPE\' => \'UNIQUE\'\n                                        }\n                                      ]\n                       },\n          \'resolution\' => {\n                            \'FIELDS\' => [\n                                          \'id\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'TYPE\' => \'SMALLSERIAL\'\n                                          },\n                                          \'value\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'varchar(64)\'\n                                          },\n                                          \'sortkey\',\n                                          {\n                                            \'DEFAULT\' => 0,\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'INT2\'\n                                          },\n                                          \'isactive\',\n                                          {\n                                            \'DEFAULT\' => \'TRUE\',\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'BOOLEAN\'\n                                          },\n                                          \'visibility_value_id\',\n                                          {\n                                            \'TYPE\' => \'INT2\'\n                                          }\n                                        ],\n                            \'INDEXES\' => [\n                                           \'resolution_value_idx\',\n                                           {\n                                             \'FIELDS\' => [\n                                                           \'value\'\n                                                         ],\n                                             \'TYPE\' => \'UNIQUE\'\n                                           },\n                                           \'resolution_sortkey_idx\',\n                                           [\n                                             \'sortkey\',\n                                             \'value\'\n                                           ],\n                                           \'resolution_visibility_value_id_idx\',\n                                           [\n                                             \'visibility_value_id\'\n                                           ]\n                                         ]\n                          },\n          \'series\' => {\n                        \'FIELDS\' => [\n                                      \'series_id\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'PRIMARYKEY\' => 1,\n                                        \'TYPE\' => \'MEDIUMSERIAL\'\n                                      },\n                                      \'creator\',\n                                      {\n                                        \'REFERENCES\' => {\n                                                          \'COLUMN\' => \'userid\',\n                                                          \'DELETE\' => \'CASCADE\',\n                                                          \'TABLE\' => \'profiles\',\n                                                          \'created\' => 1\n                                                        },\n                                        \'TYPE\' => \'INT3\'\n                                      },\n                                      \'category\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'REFERENCES\' => {\n                                                          \'COLUMN\' => \'id\',\n                                                          \'DELETE\' => \'CASCADE\',\n                                                          \'TABLE\' => \'series_categories\',\n                                                          \'created\' => 1\n                                                        },\n                                        \'TYPE\' => \'INT2\'\n                                      },\n                                      \'subcategory\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'REFERENCES\' => {\n                                                          \'COLUMN\' => \'id\',\n                                                          \'DELETE\' => \'CASCADE\',\n                                                          \'TABLE\' => \'series_categories\',\n                                                          \'created\' => 1\n                                                        },\n                                        \'TYPE\' => \'INT2\'\n                                      },\n                                      \'name\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'varchar(64)\'\n                                      },\n                                      \'frequency\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'INT2\'\n                                      },\n                                      \'query\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'MEDIUMTEXT\'\n                                      },\n                                      \'is_public\',\n                                      {\n                                        \'DEFAULT\' => \'FALSE\',\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'BOOLEAN\'\n                                      }\n                                    ],\n                        \'INDEXES\' => [\n                                       \'series_creator_idx\',\n                                       [\n                                         \'creator\'\n                                       ],\n                                       \'series_category_idx\',\n                                       {\n                                         \'FIELDS\' => [\n                                                       \'category\',\n                                                       \'subcategory\',\n                                                       \'name\'\n                                                     ],\n                                         \'TYPE\' => \'UNIQUE\'\n                                       }\n                                     ]\n                      },\n          \'series_categories\' => {\n                                   \'FIELDS\' => [\n                                                 \'id\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'PRIMARYKEY\' => 1,\n                                                   \'TYPE\' => \'SMALLSERIAL\'\n                                                 },\n                                                 \'name\',\n                                                 {\n                                                   \'NOTNULL\' => 1,\n                                                   \'TYPE\' => \'varchar(64)\'\n                                                 }\n                                               ],\n                                   \'INDEXES\' => [\n                                                  \'series_categories_name_idx\',\n                                                  {\n                                                    \'FIELDS\' => [\n                                                                  \'name\'\n                                                                ],\n                                                    \'TYPE\' => \'UNIQUE\'\n                                                  }\n                                                ]\n                                 },\n          \'series_data\' => {\n                             \'FIELDS\' => [\n                                           \'series_id\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'REFERENCES\' => {\n                                                               \'COLUMN\' => \'series_id\',\n                                                               \'DELETE\' => \'CASCADE\',\n                                                               \'TABLE\' => \'series\',\n                                                               \'created\' => 1\n                                                             },\n                                             \'TYPE\' => \'INT3\'\n                                           },\n                                           \'series_date\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'DATETIME\'\n                                           },\n                                           \'series_value\',\n                                           {\n                                             \'NOTNULL\' => 1,\n                                             \'TYPE\' => \'INT3\'\n                                           }\n                                         ],\n                             \'INDEXES\' => [\n                                            \'series_data_series_id_idx\',\n                                            {\n                                              \'FIELDS\' => [\n                                                            \'series_id\',\n                                                            \'series_date\'\n                                                          ],\n                                              \'TYPE\' => \'UNIQUE\'\n                                            }\n                                          ]\n                           },\n          \'setting\' => {\n                         \'FIELDS\' => [\n                                       \'name\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'PRIMARYKEY\' => 1,\n                                         \'TYPE\' => \'varchar(32)\'\n                                       },\n                                       \'default_value\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'TYPE\' => \'varchar(32)\'\n                                       },\n                                       \'is_enabled\',\n                                       {\n                                         \'DEFAULT\' => \'TRUE\',\n                                         \'NOTNULL\' => 1,\n                                         \'TYPE\' => \'BOOLEAN\'\n                                       },\n                                       \'subclass\',\n                                       {\n                                         \'TYPE\' => \'varchar(32)\'\n                                       }\n                                     ]\n                       },\n          \'setting_value\' => {\n                               \'FIELDS\' => [\n                                             \'name\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'name\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'setting\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'varchar(32)\'\n                                             },\n                                             \'value\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'varchar(32)\'\n                                             },\n                                             \'sortindex\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'INT2\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'setting_value_nv_unique_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'name\',\n                                                              \'value\'\n                                                            ],\n                                                \'TYPE\' => \'UNIQUE\'\n                                              },\n                                              \'setting_value_ns_unique_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'name\',\n                                                              \'sortindex\'\n                                                            ],\n                                                \'TYPE\' => \'UNIQUE\'\n                                              }\n                                            ]\n                             },\n          \'status_workflow\' => {\n                                 \'FIELDS\' => [\n                                               \'old_status\',\n                                               {\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'id\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'bug_status\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT2\'\n                                               },\n                                               \'new_status\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'id\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'bug_status\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT2\'\n                                               },\n                                               \'require_comment\',\n                                               {\n                                                 \'DEFAULT\' => 0,\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'INT1\'\n                                               }\n                                             ],\n                                 \'INDEXES\' => [\n                                                \'status_workflow_idx\',\n                                                {\n                                                  \'FIELDS\' => [\n                                                                \'old_status\',\n                                                                \'new_status\'\n                                                              ],\n                                                  \'TYPE\' => \'UNIQUE\'\n                                                }\n                                              ]\n                               },\n          \'tag\' => {\n                     \'FIELDS\' => [\n                                   \'id\',\n                                   {\n                                     \'NOTNULL\' => 1,\n                                     \'PRIMARYKEY\' => 1,\n                                     \'TYPE\' => \'MEDIUMSERIAL\'\n                                   },\n                                   \'name\',\n                                   {\n                                     \'NOTNULL\' => 1,\n                                     \'TYPE\' => \'varchar(64)\'\n                                   },\n                                   \'user_id\',\n                                   {\n                                     \'NOTNULL\' => 1,\n                                     \'REFERENCES\' => {\n                                                       \'COLUMN\' => \'userid\',\n                                                       \'DELETE\' => \'CASCADE\',\n                                                       \'TABLE\' => \'profiles\',\n                                                       \'created\' => 1\n                                                     },\n                                     \'TYPE\' => \'INT3\'\n                                   }\n                                 ],\n                     \'INDEXES\' => [\n                                    \'tag_user_id_idx\',\n                                    {\n                                      \'FIELDS\' => [\n                                                    \'user_id\',\n                                                    \'name\'\n                                                  ],\n                                      \'TYPE\' => \'UNIQUE\'\n                                    }\n                                  ]\n                   },\n          \'tokens\' => {\n                        \'FIELDS\' => [\n                                      \'userid\',\n                                      {\n                                        \'REFERENCES\' => {\n                                                          \'COLUMN\' => \'userid\',\n                                                          \'DELETE\' => \'CASCADE\',\n                                                          \'TABLE\' => \'profiles\',\n                                                          \'created\' => 1\n                                                        },\n                                        \'TYPE\' => \'INT3\'\n                                      },\n                                      \'issuedate\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'DATETIME\'\n                                      },\n                                      \'token\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'PRIMARYKEY\' => 1,\n                                        \'TYPE\' => \'varchar(16)\'\n                                      },\n                                      \'tokentype\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'varchar(16)\'\n                                      },\n                                      \'eventdata\',\n                                      {\n                                        \'TYPE\' => \'TINYTEXT\'\n                                      }\n                                    ],\n                        \'INDEXES\' => [\n                                       \'tokens_userid_idx\',\n                                       [\n                                         \'userid\'\n                                       ]\n                                     ]\n                      },\n          \'ts_error\' => {\n                          \'FIELDS\' => [\n                                        \'error_time\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'INT4\'\n                                        },\n                                        \'jobid\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'INT4\'\n                                        },\n                                        \'message\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(255)\'\n                                        },\n                                        \'funcid\',\n                                        {\n                                          \'DEFAULT\' => 0,\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'INT4\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'ts_error_funcid_idx\',\n                                         [\n                                           \'funcid\',\n                                           \'error_time\'\n                                         ],\n                                         \'ts_error_error_time_idx\',\n                                         [\n                                           \'error_time\'\n                                         ],\n                                         \'ts_error_jobid_idx\',\n                                         [\n                                           \'jobid\'\n                                         ]\n                                       ]\n                        },\n          \'ts_exitstatus\' => {\n                               \'FIELDS\' => [\n                                             \'jobid\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'PRIMARYKEY\' => 1,\n                                               \'TYPE\' => \'INTSERIAL\'\n                                             },\n                                             \'funcid\',\n                                             {\n                                               \'DEFAULT\' => 0,\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'INT4\'\n                                             },\n                                             \'status\',\n                                             {\n                                               \'TYPE\' => \'INT2\'\n                                             },\n                                             \'completion_time\',\n                                             {\n                                               \'TYPE\' => \'INT4\'\n                                             },\n                                             \'delete_after\',\n                                             {\n                                               \'TYPE\' => \'INT4\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'ts_exitstatus_funcid_idx\',\n                                              [\n                                                \'funcid\'\n                                              ],\n                                              \'ts_exitstatus_delete_after_idx\',\n                                              [\n                                                \'delete_after\'\n                                              ]\n                                            ]\n                             },\n          \'ts_funcmap\' => {\n                            \'FIELDS\' => [\n                                          \'funcid\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'PRIMARYKEY\' => 1,\n                                            \'TYPE\' => \'INTSERIAL\'\n                                          },\n                                          \'funcname\',\n                                          {\n                                            \'NOTNULL\' => 1,\n                                            \'TYPE\' => \'varchar(255)\'\n                                          }\n                                        ],\n                            \'INDEXES\' => [\n                                           \'ts_funcmap_funcname_idx\',\n                                           {\n                                             \'FIELDS\' => [\n                                                           \'funcname\'\n                                                         ],\n                                             \'TYPE\' => \'UNIQUE\'\n                                           }\n                                         ]\n                          },\n          \'ts_job\' => {\n                        \'FIELDS\' => [\n                                      \'jobid\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'PRIMARYKEY\' => 1,\n                                        \'TYPE\' => \'INTSERIAL\'\n                                      },\n                                      \'funcid\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'INT4\'\n                                      },\n                                      \'arg\',\n                                      {\n                                        \'TYPE\' => \'LONGBLOB\'\n                                      },\n                                      \'uniqkey\',\n                                      {\n                                        \'TYPE\' => \'varchar(255)\'\n                                      },\n                                      \'insert_time\',\n                                      {\n                                        \'TYPE\' => \'INT4\'\n                                      },\n                                      \'run_after\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'INT4\'\n                                      },\n                                      \'grabbed_until\',\n                                      {\n                                        \'NOTNULL\' => 1,\n                                        \'TYPE\' => \'INT4\'\n                                      },\n                                      \'priority\',\n                                      {\n                                        \'TYPE\' => \'INT2\'\n                                      },\n                                      \'coalesce\',\n                                      {\n                                        \'TYPE\' => \'varchar(255)\'\n                                      }\n                                    ],\n                        \'INDEXES\' => [\n                                       \'ts_job_funcid_idx\',\n                                       {\n                                         \'FIELDS\' => [\n                                                       \'funcid\',\n                                                       \'uniqkey\'\n                                                     ],\n                                         \'TYPE\' => \'UNIQUE\'\n                                       },\n                                       \'ts_job_run_after_idx\',\n                                       [\n                                         \'run_after\',\n                                         \'funcid\'\n                                       ],\n                                       \'ts_job_coalesce_idx\',\n                                       [\n                                         \'coalesce\',\n                                         \'funcid\'\n                                       ]\n                                     ]\n                      },\n          \'ts_note\' => {\n                         \'FIELDS\' => [\n                                       \'jobid\',\n                                       {\n                                         \'NOTNULL\' => 1,\n                                         \'TYPE\' => \'INT4\'\n                                       },\n                                       \'notekey\',\n                                       {\n                                         \'TYPE\' => \'varchar(255)\'\n                                       },\n                                       \'value\',\n                                       {\n                                         \'TYPE\' => \'LONGBLOB\'\n                                       }\n                                     ],\n                         \'INDEXES\' => [\n                                        \'ts_note_jobid_idx\',\n                                        {\n                                          \'FIELDS\' => [\n                                                        \'jobid\',\n                                                        \'notekey\'\n                                                      ],\n                                          \'TYPE\' => \'UNIQUE\'\n                                        }\n                                      ]\n                       },\n          \'user_api_keys\' => {\n                               \'FIELDS\' => [\n                                             \'id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'PRIMARYKEY\' => 1,\n                                               \'TYPE\' => \'INTSERIAL\'\n                                             },\n                                             \'user_id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'userid\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'profiles\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'api_key\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'VARCHAR(40)\'\n                                             },\n                                             \'description\',\n                                             {\n                                               \'TYPE\' => \'VARCHAR(255)\'\n                                             },\n                                             \'revoked\',\n                                             {\n                                               \'DEFAULT\' => \'FALSE\',\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'BOOLEAN\'\n                                             },\n                                             \'last_used\',\n                                             {\n                                               \'TYPE\' => \'DATETIME\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'user_api_keys_api_key_idx\',\n                                              {\n                                                \'FIELDS\' => [\n                                                              \'api_key\'\n                                                            ],\n                                                \'TYPE\' => \'UNIQUE\'\n                                              },\n                                              \'user_api_keys_user_id_idx\',\n                                              [\n                                                \'user_id\'\n                                              ]\n                                            ]\n                             },\n          \'user_group_map\' => {\n                                \'FIELDS\' => [\n                                              \'user_id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'userid\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'profiles\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              },\n                                              \'group_id\',\n                                              {\n                                                \'NOTNULL\' => 1,\n                                                \'REFERENCES\' => {\n                                                                  \'COLUMN\' => \'id\',\n                                                                  \'DELETE\' => \'CASCADE\',\n                                                                  \'TABLE\' => \'groups\',\n                                                                  \'created\' => 1\n                                                                },\n                                                \'TYPE\' => \'INT3\'\n                                              },\n                                              \'isbless\',\n                                              {\n                                                \'DEFAULT\' => \'FALSE\',\n                                                \'NOTNULL\' => 1,\n                                                \'TYPE\' => \'BOOLEAN\'\n                                              },\n                                              \'grant_type\',\n                                              {\n                                                \'DEFAULT\' => 0,\n                                                \'NOTNULL\' => 1,\n                                                \'TYPE\' => \'INT1\'\n                                              }\n                                            ],\n                                \'INDEXES\' => [\n                                               \'user_group_map_user_id_idx\',\n                                               {\n                                                 \'FIELDS\' => [\n                                                               \'user_id\',\n                                                               \'group_id\',\n                                                               \'grant_type\',\n                                                               \'isbless\'\n                                                             ],\n                                                 \'TYPE\' => \'UNIQUE\'\n                                               }\n                                             ]\n                              },\n          \'versions\' => {\n                          \'FIELDS\' => [\n                                        \'id\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'PRIMARYKEY\' => 1,\n                                          \'TYPE\' => \'MEDIUMSERIAL\'\n                                        },\n                                        \'value\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'varchar(64)\'\n                                        },\n                                        \'product_id\',\n                                        {\n                                          \'NOTNULL\' => 1,\n                                          \'REFERENCES\' => {\n                                                            \'COLUMN\' => \'id\',\n                                                            \'DELETE\' => \'CASCADE\',\n                                                            \'TABLE\' => \'products\',\n                                                            \'created\' => 1\n                                                          },\n                                          \'TYPE\' => \'INT2\'\n                                        },\n                                        \'isactive\',\n                                        {\n                                          \'DEFAULT\' => \'TRUE\',\n                                          \'NOTNULL\' => 1,\n                                          \'TYPE\' => \'BOOLEAN\'\n                                        }\n                                      ],\n                          \'INDEXES\' => [\n                                         \'versions_product_id_idx\',\n                                         {\n                                           \'FIELDS\' => [\n                                                         \'product_id\',\n                                                         \'value\'\n                                                       ],\n                                           \'TYPE\' => \'UNIQUE\'\n                                         }\n                                       ]\n                        },\n          \'watch\' => {\n                       \'FIELDS\' => [\n                                     \'watcher\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'userid\',\n                                                         \'DELETE\' => \'CASCADE\',\n                                                         \'TABLE\' => \'profiles\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     },\n                                     \'watched\',\n                                     {\n                                       \'NOTNULL\' => 1,\n                                       \'REFERENCES\' => {\n                                                         \'COLUMN\' => \'userid\',\n                                                         \'DELETE\' => \'CASCADE\',\n                                                         \'TABLE\' => \'profiles\',\n                                                         \'created\' => 1\n                                                       },\n                                       \'TYPE\' => \'INT3\'\n                                     }\n                                   ],\n                       \'INDEXES\' => [\n                                      \'watch_watcher_idx\',\n                                      {\n                                        \'FIELDS\' => [\n                                                      \'watcher\',\n                                                      \'watched\'\n                                                    ],\n                                        \'TYPE\' => \'UNIQUE\'\n                                      },\n                                      \'watch_watched_idx\',\n                                      [\n                                        \'watched\'\n                                      ]\n                                    ]\n                     },\n          \'whine_events\' => {\n                              \'FIELDS\' => [\n                                            \'id\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'PRIMARYKEY\' => 1,\n                                              \'TYPE\' => \'MEDIUMSERIAL\'\n                                            },\n                                            \'owner_userid\',\n                                            {\n                                              \'NOTNULL\' => 1,\n                                              \'REFERENCES\' => {\n                                                                \'COLUMN\' => \'userid\',\n                                                                \'DELETE\' => \'CASCADE\',\n                                                                \'TABLE\' => \'profiles\',\n                                                                \'created\' => 1\n                                                              },\n                                              \'TYPE\' => \'INT3\'\n                                            },\n                                            \'subject\',\n                                            {\n                                              \'TYPE\' => \'varchar(128)\'\n                                            },\n                                            \'body\',\n                                            {\n                                              \'TYPE\' => \'MEDIUMTEXT\'\n                                            },\n                                            \'mailifnobugs\',\n                                            {\n                                              \'DEFAULT\' => \'FALSE\',\n                                              \'NOTNULL\' => 1,\n                                              \'TYPE\' => \'BOOLEAN\'\n                                            }\n                                          ]\n                            },\n          \'whine_queries\' => {\n                               \'FIELDS\' => [\n                                             \'id\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'PRIMARYKEY\' => 1,\n                                               \'TYPE\' => \'MEDIUMSERIAL\'\n                                             },\n                                             \'eventid\',\n                                             {\n                                               \'NOTNULL\' => 1,\n                                               \'REFERENCES\' => {\n                                                                 \'COLUMN\' => \'id\',\n                                                                 \'DELETE\' => \'CASCADE\',\n                                                                 \'TABLE\' => \'whine_events\',\n                                                                 \'created\' => 1\n                                                               },\n                                               \'TYPE\' => \'INT3\'\n                                             },\n                                             \'query_name\',\n                                             {\n                                               \'DEFAULT\' => \'\\\'\\\'\',\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'varchar(64)\'\n                                             },\n                                             \'sortkey\',\n                                             {\n                                               \'DEFAULT\' => \'0\',\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'INT2\'\n                                             },\n                                             \'onemailperbug\',\n                                             {\n                                               \'DEFAULT\' => \'FALSE\',\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'BOOLEAN\'\n                                             },\n                                             \'title\',\n                                             {\n                                               \'DEFAULT\' => \'\\\'\\\'\',\n                                               \'NOTNULL\' => 1,\n                                               \'TYPE\' => \'varchar(128)\'\n                                             }\n                                           ],\n                               \'INDEXES\' => [\n                                              \'whine_queries_eventid_idx\',\n                                              [\n                                                \'eventid\'\n                                              ]\n                                            ]\n                             },\n          \'whine_schedules\' => {\n                                 \'FIELDS\' => [\n                                               \'id\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'PRIMARYKEY\' => 1,\n                                                 \'TYPE\' => \'MEDIUMSERIAL\'\n                                               },\n                                               \'eventid\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'REFERENCES\' => {\n                                                                   \'COLUMN\' => \'id\',\n                                                                   \'DELETE\' => \'CASCADE\',\n                                                                   \'TABLE\' => \'whine_events\',\n                                                                   \'created\' => 1\n                                                                 },\n                                                 \'TYPE\' => \'INT3\'\n                                               },\n                                               \'run_day\',\n                                               {\n                                                 \'TYPE\' => \'varchar(32)\'\n                                               },\n                                               \'run_time\',\n                                               {\n                                                 \'TYPE\' => \'varchar(32)\'\n                                               },\n                                               \'run_next\',\n                                               {\n                                                 \'TYPE\' => \'DATETIME\'\n                                               },\n                                               \'mailto\',\n                                               {\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'INT3\'\n                                               },\n                                               \'mailto_type\',\n                                               {\n                                                 \'DEFAULT\' => \'0\',\n                                                 \'NOTNULL\' => 1,\n                                                 \'TYPE\' => \'INT2\'\n                                               }\n                                             ],\n                                 \'INDEXES\' => [\n                                                \'whine_schedules_run_next_idx\',\n                                                [\n                                                  \'run_next\'\n                                                ],\n                                                \'whine_schedules_eventid_idx\',\n                                                [\n                                                  \'eventid\'\n                                                ]\n                                              ]\n                               }\n        };\n',3.00);
/*!40000 ALTER TABLE `bz_schema` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category_group_map`
--

DROP TABLE IF EXISTS `category_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category_group_map` (
  `category_id` smallint(6) NOT NULL,
  `group_id` mediumint(9) NOT NULL,
  UNIQUE KEY `category_group_map_category_id_idx` (`category_id`,`group_id`),
  KEY `fk_category_group_map_group_id_groups_id` (`group_id`),
  CONSTRAINT `fk_category_group_map_category_id_series_categories_id` FOREIGN KEY (`category_id`) REFERENCES `series_categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_category_group_map_group_id_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category_group_map`
--

LOCK TABLES `category_group_map` WRITE;
/*!40000 ALTER TABLE `category_group_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `category_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cc`
--

DROP TABLE IF EXISTS `cc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cc` (
  `bug_id` mediumint(9) NOT NULL,
  `who` mediumint(9) NOT NULL,
  UNIQUE KEY `cc_bug_id_idx` (`bug_id`,`who`),
  KEY `cc_who_idx` (`who`),
  CONSTRAINT `fk_cc_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cc_who_profiles_userid` FOREIGN KEY (`who`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cc`
--

LOCK TABLES `cc` WRITE;
/*!40000 ALTER TABLE `cc` DISABLE KEYS */;
/*!40000 ALTER TABLE `cc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classifications`
--

DROP TABLE IF EXISTS `classifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classifications` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` mediumtext DEFAULT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `classifications_name_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classifications`
--

LOCK TABLES `classifications` WRITE;
/*!40000 ALTER TABLE `classifications` DISABLE KEYS */;
INSERT INTO `classifications` VALUES (1,'Unclassified','Not assigned to any classification',0);
/*!40000 ALTER TABLE `classifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `component_cc`
--

DROP TABLE IF EXISTS `component_cc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `component_cc` (
  `user_id` mediumint(9) NOT NULL,
  `component_id` mediumint(9) NOT NULL,
  UNIQUE KEY `component_cc_user_id_idx` (`component_id`,`user_id`),
  KEY `fk_component_cc_user_id_profiles_userid` (`user_id`),
  CONSTRAINT `fk_component_cc_component_id_components_id` FOREIGN KEY (`component_id`) REFERENCES `components` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_component_cc_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `component_cc`
--

LOCK TABLES `component_cc` WRITE;
/*!40000 ALTER TABLE `component_cc` DISABLE KEYS */;
/*!40000 ALTER TABLE `component_cc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `components`
--

DROP TABLE IF EXISTS `components`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `components` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `product_id` smallint(6) NOT NULL,
  `initialowner` mediumint(9) NOT NULL,
  `initialqacontact` mediumint(9) DEFAULT NULL,
  `description` mediumtext NOT NULL,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `components_product_id_idx` (`product_id`,`name`),
  KEY `components_name_idx` (`name`),
  KEY `fk_components_initialqacontact_profiles_userid` (`initialqacontact`),
  KEY `fk_components_initialowner_profiles_userid` (`initialowner`),
  CONSTRAINT `fk_components_initialowner_profiles_userid` FOREIGN KEY (`initialowner`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE,
  CONSTRAINT `fk_components_initialqacontact_profiles_userid` FOREIGN KEY (`initialqacontact`) REFERENCES `profiles` (`userid`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_components_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `components`
--

LOCK TABLES `components` WRITE;
/*!40000 ALTER TABLE `components` DISABLE KEYS */;
INSERT INTO `components` VALUES (1,'TestComponent',1,1,NULL,'This is a test component in the test product database. This ought to be blown away and replaced with real stuff in a finished installation of Bugzilla.',1),(2,'python-bugzilla',2,1,NULL,'Lorem ipsum dolor sit amet',1),(3,'Kernel',3,1,NULL,'Lorem ipsum',1),(4,'Containers',3,1,NULL,'Lorem ipsum',1);
/*!40000 ALTER TABLE `components` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dependencies`
--

DROP TABLE IF EXISTS `dependencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dependencies` (
  `blocked` mediumint(9) NOT NULL,
  `dependson` mediumint(9) NOT NULL,
  UNIQUE KEY `dependencies_blocked_idx` (`blocked`,`dependson`),
  KEY `dependencies_dependson_idx` (`dependson`),
  CONSTRAINT `fk_dependencies_blocked_bugs_bug_id` FOREIGN KEY (`blocked`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_dependencies_dependson_bugs_bug_id` FOREIGN KEY (`dependson`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dependencies`
--

LOCK TABLES `dependencies` WRITE;
/*!40000 ALTER TABLE `dependencies` DISABLE KEYS */;
/*!40000 ALTER TABLE `dependencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `duplicates`
--

DROP TABLE IF EXISTS `duplicates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `duplicates` (
  `dupe_of` mediumint(9) NOT NULL,
  `dupe` mediumint(9) NOT NULL,
  PRIMARY KEY (`dupe`),
  KEY `fk_duplicates_dupe_of_bugs_bug_id` (`dupe_of`),
  CONSTRAINT `fk_duplicates_dupe_bugs_bug_id` FOREIGN KEY (`dupe`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_duplicates_dupe_of_bugs_bug_id` FOREIGN KEY (`dupe_of`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `duplicates`
--

LOCK TABLES `duplicates` WRITE;
/*!40000 ALTER TABLE `duplicates` DISABLE KEYS */;
/*!40000 ALTER TABLE `duplicates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_bug_ignore`
--

DROP TABLE IF EXISTS `email_bug_ignore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_bug_ignore` (
  `user_id` mediumint(9) NOT NULL,
  `bug_id` mediumint(9) NOT NULL,
  UNIQUE KEY `email_bug_ignore_user_id_idx` (`user_id`,`bug_id`),
  KEY `fk_email_bug_ignore_bug_id_bugs_bug_id` (`bug_id`),
  CONSTRAINT `fk_email_bug_ignore_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_email_bug_ignore_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_bug_ignore`
--

LOCK TABLES `email_bug_ignore` WRITE;
/*!40000 ALTER TABLE `email_bug_ignore` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_bug_ignore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_setting`
--

DROP TABLE IF EXISTS `email_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_setting` (
  `user_id` mediumint(9) NOT NULL,
  `relationship` tinyint(4) NOT NULL,
  `event` tinyint(4) NOT NULL,
  UNIQUE KEY `email_setting_user_id_idx` (`user_id`,`relationship`,`event`),
  CONSTRAINT `fk_email_setting_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_setting`
--

LOCK TABLES `email_setting` WRITE;
/*!40000 ALTER TABLE `email_setting` DISABLE KEYS */;
INSERT INTO `email_setting` VALUES (1,0,0),(1,0,1),(1,0,2),(1,0,3),(1,0,4),(1,0,5),(1,0,6),(1,0,7),(1,0,9),(1,0,10),(1,0,11),(1,0,50),(1,1,0),(1,1,1),(1,1,2),(1,1,3),(1,1,4),(1,1,5),(1,1,6),(1,1,7),(1,1,9),(1,1,10),(1,1,11),(1,1,50),(1,2,0),(1,2,1),(1,2,2),(1,2,3),(1,2,4),(1,2,5),(1,2,6),(1,2,7),(1,2,8),(1,2,9),(1,2,10),(1,2,11),(1,2,50),(1,3,0),(1,3,1),(1,3,2),(1,3,3),(1,3,4),(1,3,5),(1,3,6),(1,3,7),(1,3,9),(1,3,10),(1,3,11),(1,3,50),(1,5,0),(1,5,1),(1,5,2),(1,5,3),(1,5,4),(1,5,5),(1,5,6),(1,5,7),(1,5,9),(1,5,10),(1,5,11),(1,5,50),(1,100,100),(1,100,101);
/*!40000 ALTER TABLE `email_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `field_visibility`
--

DROP TABLE IF EXISTS `field_visibility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `field_visibility` (
  `field_id` mediumint(9) DEFAULT NULL,
  `value_id` smallint(6) NOT NULL,
  UNIQUE KEY `field_visibility_field_id_idx` (`field_id`,`value_id`),
  CONSTRAINT `fk_field_visibility_field_id_fielddefs_id` FOREIGN KEY (`field_id`) REFERENCES `fielddefs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `field_visibility`
--

LOCK TABLES `field_visibility` WRITE;
/*!40000 ALTER TABLE `field_visibility` DISABLE KEYS */;
/*!40000 ALTER TABLE `field_visibility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fielddefs`
--

DROP TABLE IF EXISTS `fielddefs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fielddefs` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `type` smallint(6) NOT NULL DEFAULT 0,
  `custom` tinyint(4) NOT NULL DEFAULT 0,
  `description` tinytext NOT NULL,
  `long_desc` varchar(255) NOT NULL DEFAULT '',
  `mailhead` tinyint(4) NOT NULL DEFAULT 0,
  `sortkey` smallint(6) NOT NULL,
  `obsolete` tinyint(4) NOT NULL DEFAULT 0,
  `enter_bug` tinyint(4) NOT NULL DEFAULT 0,
  `buglist` tinyint(4) NOT NULL DEFAULT 0,
  `visibility_field_id` mediumint(9) DEFAULT NULL,
  `value_field_id` mediumint(9) DEFAULT NULL,
  `reverse_desc` tinytext DEFAULT NULL,
  `is_mandatory` tinyint(4) NOT NULL DEFAULT 0,
  `is_numeric` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fielddefs_name_idx` (`name`),
  KEY `fielddefs_sortkey_idx` (`sortkey`),
  KEY `fielddefs_value_field_id_idx` (`value_field_id`),
  KEY `fielddefs_is_mandatory_idx` (`is_mandatory`),
  KEY `fk_fielddefs_visibility_field_id_fielddefs_id` (`visibility_field_id`),
  CONSTRAINT `fk_fielddefs_value_field_id_fielddefs_id` FOREIGN KEY (`value_field_id`) REFERENCES `fielddefs` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_fielddefs_visibility_field_id_fielddefs_id` FOREIGN KEY (`visibility_field_id`) REFERENCES `fielddefs` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fielddefs`
--

LOCK TABLES `fielddefs` WRITE;
/*!40000 ALTER TABLE `fielddefs` DISABLE KEYS */;
INSERT INTO `fielddefs` VALUES (1,'bug_id',0,0,'Bug #','',1,100,0,0,1,NULL,NULL,NULL,0,1),(2,'short_desc',0,0,'Summary','',1,200,0,0,1,NULL,NULL,NULL,1,0),(3,'classification',2,0,'Classification','',1,300,0,0,1,NULL,NULL,NULL,0,0),(4,'product',2,0,'Product','',1,400,0,0,1,NULL,NULL,NULL,1,0),(5,'version',0,0,'Version','',1,500,0,0,1,NULL,NULL,NULL,1,0),(6,'rep_platform',2,0,'Platform','',1,600,0,0,1,NULL,NULL,NULL,0,0),(7,'bug_file_loc',0,0,'URL','',1,700,0,0,1,NULL,NULL,NULL,0,0),(8,'op_sys',2,0,'OS/Version','',1,800,0,0,1,NULL,NULL,NULL,0,0),(9,'bug_status',2,0,'Status','',1,900,0,0,1,NULL,NULL,NULL,0,0),(10,'status_whiteboard',0,0,'Status Whiteboard','',1,1000,0,0,1,NULL,NULL,NULL,0,0),(11,'keywords',8,0,'Keywords','',1,1100,0,0,1,NULL,NULL,NULL,0,0),(12,'resolution',2,0,'Resolution','',0,1200,0,0,1,NULL,NULL,NULL,0,0),(13,'bug_severity',2,0,'Severity','',1,1300,0,0,1,NULL,NULL,NULL,0,0),(14,'priority',2,0,'Priority','',1,1400,0,0,1,NULL,NULL,NULL,0,0),(15,'component',2,0,'Component','',1,1500,0,0,1,NULL,NULL,NULL,1,0),(16,'assigned_to',0,0,'AssignedTo','',1,1600,0,0,1,NULL,NULL,NULL,0,0),(17,'reporter',0,0,'ReportedBy','',1,1700,0,0,1,NULL,NULL,NULL,0,0),(18,'qa_contact',0,0,'QAContact','',1,1800,0,0,1,NULL,NULL,NULL,0,0),(19,'assigned_to_realname',0,0,'AssignedToName','',0,1900,0,0,1,NULL,NULL,NULL,0,0),(20,'reporter_realname',0,0,'ReportedByName','',0,2000,0,0,1,NULL,NULL,NULL,0,0),(21,'qa_contact_realname',0,0,'QAContactName','',0,2100,0,0,1,NULL,NULL,NULL,0,0),(22,'cc',0,0,'CC','',1,2200,0,0,0,NULL,NULL,NULL,0,0),(23,'dependson',0,0,'Depends on','',1,2300,0,0,1,NULL,NULL,NULL,0,1),(24,'blocked',0,0,'Blocks','',1,2400,0,0,1,NULL,NULL,NULL,0,1),(25,'attachments.description',0,0,'Attachment description','',0,2500,0,0,0,NULL,NULL,NULL,0,0),(26,'attachments.filename',0,0,'Attachment filename','',0,2600,0,0,0,NULL,NULL,NULL,0,0),(27,'attachments.mimetype',0,0,'Attachment mime type','',0,2700,0,0,0,NULL,NULL,NULL,0,0),(28,'attachments.ispatch',0,0,'Attachment is patch','',0,2800,0,0,0,NULL,NULL,NULL,0,1),(29,'attachments.isobsolete',0,0,'Attachment is obsolete','',0,2900,0,0,0,NULL,NULL,NULL,0,1),(30,'attachments.isprivate',0,0,'Attachment is private','',0,3000,0,0,0,NULL,NULL,NULL,0,1),(31,'attachments.submitter',0,0,'Attachment creator','',0,3100,0,0,0,NULL,NULL,NULL,0,0),(32,'target_milestone',0,0,'Target Milestone','',1,3200,0,0,1,NULL,NULL,NULL,0,0),(33,'creation_ts',0,0,'Creation date','',0,3300,0,0,1,NULL,NULL,NULL,0,0),(34,'delta_ts',0,0,'Last changed date','',0,3400,0,0,1,NULL,NULL,NULL,0,0),(35,'longdesc',0,0,'Comment','',0,3500,0,0,0,NULL,NULL,NULL,0,0),(36,'longdescs.isprivate',0,0,'Comment is private','',0,3600,0,0,0,NULL,NULL,NULL,0,1),(37,'longdescs.count',0,0,'Number of Comments','',0,3700,0,0,1,NULL,NULL,NULL,0,1),(38,'alias',0,0,'Alias','',0,3800,0,0,1,NULL,NULL,NULL,0,0),(39,'everconfirmed',0,0,'Ever Confirmed','',0,3900,0,0,0,NULL,NULL,NULL,0,1),(40,'reporter_accessible',0,0,'Reporter Accessible','',0,4000,0,0,0,NULL,NULL,NULL,0,1),(41,'cclist_accessible',0,0,'CC Accessible','',0,4100,0,0,0,NULL,NULL,NULL,0,1),(42,'bug_group',0,0,'Group','',1,4200,0,0,0,NULL,NULL,NULL,0,0),(43,'estimated_time',0,0,'Estimated Hours','',1,4300,0,0,1,NULL,NULL,NULL,0,1),(44,'remaining_time',0,0,'Remaining Hours','',0,4400,0,0,1,NULL,NULL,NULL,0,1),(45,'deadline',5,0,'Deadline','',1,4500,0,0,1,NULL,NULL,NULL,0,0),(46,'commenter',0,0,'Commenter','',0,4600,0,0,0,NULL,NULL,NULL,0,0),(47,'flagtypes.name',0,0,'Flags','',0,4700,0,0,1,NULL,NULL,NULL,0,0),(48,'requestees.login_name',0,0,'Flag Requestee','',0,4800,0,0,0,NULL,NULL,NULL,0,0),(49,'setters.login_name',0,0,'Flag Setter','',0,4900,0,0,0,NULL,NULL,NULL,0,0),(50,'work_time',0,0,'Hours Worked','',0,5000,0,0,1,NULL,NULL,NULL,0,1),(51,'percentage_complete',0,0,'Percentage Complete','',0,5100,0,0,1,NULL,NULL,NULL,0,1),(52,'content',0,0,'Content','',0,5200,0,0,0,NULL,NULL,NULL,0,0),(53,'attach_data.thedata',0,0,'Attachment data','',0,5300,0,0,0,NULL,NULL,NULL,0,0),(54,'owner_idle_time',0,0,'Time Since Assignee Touched','',0,5400,0,0,0,NULL,NULL,NULL,0,0),(55,'see_also',7,0,'See Also','',0,5500,0,0,0,NULL,NULL,NULL,0,0),(56,'tag',8,0,'Personal Tags','',0,5600,0,0,1,NULL,NULL,NULL,0,0),(57,'last_visit_ts',5,0,'Last Visit','',0,5700,0,0,1,NULL,NULL,NULL,0,0),(58,'comment_tag',0,0,'Comment Tag','',0,5800,0,0,0,NULL,NULL,NULL,0,0),(59,'days_elapsed',0,0,'Days since bug changed','',0,5900,0,0,0,NULL,NULL,NULL,0,0);
/*!40000 ALTER TABLE `fielddefs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flagexclusions`
--

DROP TABLE IF EXISTS `flagexclusions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flagexclusions` (
  `type_id` mediumint(9) NOT NULL,
  `product_id` smallint(6) DEFAULT NULL,
  `component_id` mediumint(9) DEFAULT NULL,
  UNIQUE KEY `flagexclusions_type_id_idx` (`type_id`,`product_id`,`component_id`),
  KEY `fk_flagexclusions_component_id_components_id` (`component_id`),
  KEY `fk_flagexclusions_product_id_products_id` (`product_id`),
  CONSTRAINT `fk_flagexclusions_component_id_components_id` FOREIGN KEY (`component_id`) REFERENCES `components` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flagexclusions_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flagexclusions_type_id_flagtypes_id` FOREIGN KEY (`type_id`) REFERENCES `flagtypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flagexclusions`
--

LOCK TABLES `flagexclusions` WRITE;
/*!40000 ALTER TABLE `flagexclusions` DISABLE KEYS */;
/*!40000 ALTER TABLE `flagexclusions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flaginclusions`
--

DROP TABLE IF EXISTS `flaginclusions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flaginclusions` (
  `type_id` mediumint(9) NOT NULL,
  `product_id` smallint(6) DEFAULT NULL,
  `component_id` mediumint(9) DEFAULT NULL,
  UNIQUE KEY `flaginclusions_type_id_idx` (`type_id`,`product_id`,`component_id`),
  KEY `fk_flaginclusions_component_id_components_id` (`component_id`),
  KEY `fk_flaginclusions_product_id_products_id` (`product_id`),
  CONSTRAINT `fk_flaginclusions_component_id_components_id` FOREIGN KEY (`component_id`) REFERENCES `components` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flaginclusions_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flaginclusions_type_id_flagtypes_id` FOREIGN KEY (`type_id`) REFERENCES `flagtypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flaginclusions`
--

LOCK TABLES `flaginclusions` WRITE;
/*!40000 ALTER TABLE `flaginclusions` DISABLE KEYS */;
/*!40000 ALTER TABLE `flaginclusions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flags`
--

DROP TABLE IF EXISTS `flags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flags` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `type_id` mediumint(9) NOT NULL,
  `status` char(1) NOT NULL,
  `bug_id` mediumint(9) NOT NULL,
  `attach_id` mediumint(9) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `modification_date` datetime DEFAULT NULL,
  `setter_id` mediumint(9) NOT NULL,
  `requestee_id` mediumint(9) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `flags_bug_id_idx` (`bug_id`,`attach_id`),
  KEY `flags_setter_id_idx` (`setter_id`),
  KEY `flags_requestee_id_idx` (`requestee_id`),
  KEY `flags_type_id_idx` (`type_id`),
  KEY `fk_flags_attach_id_attachments_attach_id` (`attach_id`),
  CONSTRAINT `fk_flags_attach_id_attachments_attach_id` FOREIGN KEY (`attach_id`) REFERENCES `attachments` (`attach_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flags_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_flags_requestee_id_profiles_userid` FOREIGN KEY (`requestee_id`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE,
  CONSTRAINT `fk_flags_setter_id_profiles_userid` FOREIGN KEY (`setter_id`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE,
  CONSTRAINT `fk_flags_type_id_flagtypes_id` FOREIGN KEY (`type_id`) REFERENCES `flagtypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flags`
--

LOCK TABLES `flags` WRITE;
/*!40000 ALTER TABLE `flags` DISABLE KEYS */;
/*!40000 ALTER TABLE `flags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flagtypes`
--

DROP TABLE IF EXISTS `flagtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flagtypes` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` mediumtext NOT NULL,
  `cc_list` varchar(200) DEFAULT NULL,
  `target_type` char(1) NOT NULL DEFAULT 'b',
  `is_active` tinyint(4) NOT NULL DEFAULT 1,
  `is_requestable` tinyint(4) NOT NULL DEFAULT 0,
  `is_requesteeble` tinyint(4) NOT NULL DEFAULT 0,
  `is_multiplicable` tinyint(4) NOT NULL DEFAULT 0,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `grant_group_id` mediumint(9) DEFAULT NULL,
  `request_group_id` mediumint(9) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_flagtypes_request_group_id_groups_id` (`request_group_id`),
  KEY `fk_flagtypes_grant_group_id_groups_id` (`grant_group_id`),
  CONSTRAINT `fk_flagtypes_grant_group_id_groups_id` FOREIGN KEY (`grant_group_id`) REFERENCES `groups` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_flagtypes_request_group_id_groups_id` FOREIGN KEY (`request_group_id`) REFERENCES `groups` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flagtypes`
--

LOCK TABLES `flagtypes` WRITE;
/*!40000 ALTER TABLE `flagtypes` DISABLE KEYS */;
/*!40000 ALTER TABLE `flagtypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_control_map`
--

DROP TABLE IF EXISTS `group_control_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_control_map` (
  `group_id` mediumint(9) NOT NULL,
  `product_id` smallint(6) NOT NULL,
  `entry` tinyint(4) NOT NULL DEFAULT 0,
  `membercontrol` tinyint(4) NOT NULL DEFAULT 0,
  `othercontrol` tinyint(4) NOT NULL DEFAULT 0,
  `canedit` tinyint(4) NOT NULL DEFAULT 0,
  `editcomponents` tinyint(4) NOT NULL DEFAULT 0,
  `editbugs` tinyint(4) NOT NULL DEFAULT 0,
  `canconfirm` tinyint(4) NOT NULL DEFAULT 0,
  UNIQUE KEY `group_control_map_product_id_idx` (`product_id`,`group_id`),
  KEY `group_control_map_group_id_idx` (`group_id`),
  CONSTRAINT `fk_group_control_map_group_id_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_group_control_map_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_control_map`
--

LOCK TABLES `group_control_map` WRITE;
/*!40000 ALTER TABLE `group_control_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `group_control_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_group_map`
--

DROP TABLE IF EXISTS `group_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_group_map` (
  `member_id` mediumint(9) NOT NULL,
  `grantor_id` mediumint(9) NOT NULL,
  `grant_type` tinyint(4) NOT NULL DEFAULT 0,
  UNIQUE KEY `group_group_map_member_id_idx` (`member_id`,`grantor_id`,`grant_type`),
  KEY `fk_group_group_map_grantor_id_groups_id` (`grantor_id`),
  CONSTRAINT `fk_group_group_map_grantor_id_groups_id` FOREIGN KEY (`grantor_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_group_group_map_member_id_groups_id` FOREIGN KEY (`member_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_group_map`
--

LOCK TABLES `group_group_map` WRITE;
/*!40000 ALTER TABLE `group_group_map` DISABLE KEYS */;
INSERT INTO `group_group_map` VALUES (1,1,0),(1,1,1),(1,1,2),(1,2,0),(1,2,1),(1,2,2),(1,3,0),(1,3,1),(1,3,2),(1,4,0),(1,4,1),(1,4,2),(1,5,0),(1,5,1),(1,5,2),(1,6,0),(1,6,1),(1,6,2),(1,7,0),(1,7,1),(1,7,2),(1,8,0),(1,8,1),(1,8,2),(1,9,0),(1,9,1),(1,9,2),(1,10,0),(1,10,1),(1,10,2),(1,11,0),(1,11,1),(1,11,2),(8,11,0),(10,11,0),(1,12,0),(1,12,1),(1,12,2),(1,13,0),(1,13,1),(1,13,2),(12,13,0),(1,14,0),(1,14,1),(1,14,2);
/*!40000 ALTER TABLE `group_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` mediumtext NOT NULL,
  `isbuggroup` tinyint(4) NOT NULL,
  `userregexp` tinytext NOT NULL DEFAULT '',
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `icon_url` tinytext DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `groups_name_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'admin','Administrators',0,'',1,NULL),(2,'tweakparams','Can change Parameters',0,'',1,NULL),(3,'editusers','Can edit or disable users',0,'',1,NULL),(4,'creategroups','Can create and destroy groups',0,'',1,NULL),(5,'editclassifications','Can create, destroy, and edit classifications',0,'',1,NULL),(6,'editcomponents','Can create, destroy, and edit components',0,'',1,NULL),(7,'editkeywords','Can create, destroy, and edit keywords',0,'',1,NULL),(8,'editbugs','Can edit all bug fields',0,'.*',1,NULL),(9,'canconfirm','Can confirm a bug or mark it a duplicate',0,'',1,NULL),(10,'bz_canusewhineatothers','Can configure whine reports for other users',0,'',1,NULL),(11,'bz_canusewhines','User can configure whine reports for self',0,'',1,NULL),(12,'bz_sudoers','Can perform actions as other users',0,'',1,NULL),(13,'bz_sudo_protect','Can not be impersonated by other users',0,'',1,NULL),(14,'bz_quip_moderators','Can moderate quips',0,'',1,NULL);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keyworddefs`
--

DROP TABLE IF EXISTS `keyworddefs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keyworddefs` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `keyworddefs_name_idx` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keyworddefs`
--

LOCK TABLES `keyworddefs` WRITE;
/*!40000 ALTER TABLE `keyworddefs` DISABLE KEYS */;
/*!40000 ALTER TABLE `keyworddefs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `keywords`
--

DROP TABLE IF EXISTS `keywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `keywords` (
  `bug_id` mediumint(9) NOT NULL,
  `keywordid` smallint(6) NOT NULL,
  UNIQUE KEY `keywords_bug_id_idx` (`bug_id`,`keywordid`),
  KEY `keywords_keywordid_idx` (`keywordid`),
  CONSTRAINT `fk_keywords_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_keywords_keywordid_keyworddefs_id` FOREIGN KEY (`keywordid`) REFERENCES `keyworddefs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keywords`
--

LOCK TABLES `keywords` WRITE;
/*!40000 ALTER TABLE `keywords` DISABLE KEYS */;
/*!40000 ALTER TABLE `keywords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_failure`
--

DROP TABLE IF EXISTS `login_failure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login_failure` (
  `user_id` mediumint(9) NOT NULL,
  `login_time` datetime NOT NULL,
  `ip_addr` varchar(40) NOT NULL,
  KEY `login_failure_user_id_idx` (`user_id`),
  CONSTRAINT `fk_login_failure_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_failure`
--

LOCK TABLES `login_failure` WRITE;
/*!40000 ALTER TABLE `login_failure` DISABLE KEYS */;
/*!40000 ALTER TABLE `login_failure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logincookies`
--

DROP TABLE IF EXISTS `logincookies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logincookies` (
  `cookie` varchar(16) NOT NULL,
  `userid` mediumint(9) NOT NULL,
  `ipaddr` varchar(40) DEFAULT NULL,
  `lastused` datetime NOT NULL,
  PRIMARY KEY (`cookie`),
  KEY `logincookies_lastused_idx` (`lastused`),
  KEY `fk_logincookies_userid_profiles_userid` (`userid`),
  CONSTRAINT `fk_logincookies_userid_profiles_userid` FOREIGN KEY (`userid`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logincookies`
--

LOCK TABLES `logincookies` WRITE;
/*!40000 ALTER TABLE `logincookies` DISABLE KEYS */;
INSERT INTO `logincookies` VALUES ('Ypt6rPqHjG',1,NULL,'2023-11-27 15:53:08');
/*!40000 ALTER TABLE `logincookies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `longdescs`
--

DROP TABLE IF EXISTS `longdescs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `longdescs` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `bug_id` mediumint(9) NOT NULL,
  `who` mediumint(9) NOT NULL,
  `bug_when` datetime NOT NULL,
  `work_time` decimal(7,2) NOT NULL DEFAULT 0.00,
  `thetext` mediumtext NOT NULL,
  `isprivate` tinyint(4) NOT NULL DEFAULT 0,
  `already_wrapped` tinyint(4) NOT NULL DEFAULT 0,
  `type` smallint(6) NOT NULL DEFAULT 0,
  `extra_data` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `longdescs_bug_id_idx` (`bug_id`,`work_time`),
  KEY `longdescs_who_idx` (`who`,`bug_id`),
  KEY `longdescs_bug_when_idx` (`bug_when`),
  CONSTRAINT `fk_longdescs_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_longdescs_who_profiles_userid` FOREIGN KEY (`who`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `longdescs`
--

LOCK TABLES `longdescs` WRITE;
/*!40000 ALTER TABLE `longdescs` DISABLE KEYS */;
INSERT INTO `longdescs` VALUES (1,1,1,'2023-11-27 15:35:33',0.00,'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nAt vero eos et accusam et justo duo dolores et ea rebum.',0,0,0,NULL),(2,1,1,'2023-11-27 15:37:05',0.00,'Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.',0,0,0,NULL),(3,2,1,'2023-11-27 15:38:45',0.00,'Nobody expects the Spanish Inquisition! \n\nOur chief weapon is surprise, surprise and fear, fear and surprise. \n\nOur two weapons are fear and surprise, and ruthless efficiency. \n\nOur three weapons are fear and surprise and ruthless efficiency and an almost fanatical dedication to the pope.',0,0,0,NULL);
/*!40000 ALTER TABLE `longdescs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `longdescs_tags`
--

DROP TABLE IF EXISTS `longdescs_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `longdescs_tags` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `comment_id` int(11) DEFAULT NULL,
  `tag` varchar(24) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `longdescs_tags_idx` (`comment_id`,`tag`),
  CONSTRAINT `fk_longdescs_tags_comment_id_longdescs_comment_id` FOREIGN KEY (`comment_id`) REFERENCES `longdescs` (`comment_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `longdescs_tags`
--

LOCK TABLES `longdescs_tags` WRITE;
/*!40000 ALTER TABLE `longdescs_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `longdescs_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `longdescs_tags_activity`
--

DROP TABLE IF EXISTS `longdescs_tags_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `longdescs_tags_activity` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `bug_id` mediumint(9) NOT NULL,
  `comment_id` int(11) DEFAULT NULL,
  `who` mediumint(9) NOT NULL,
  `bug_when` datetime NOT NULL,
  `added` varchar(24) DEFAULT NULL,
  `removed` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `longdescs_tags_activity_bug_id_idx` (`bug_id`),
  KEY `fk_longdescs_tags_activity_comment_id_longdescs_comment_id` (`comment_id`),
  KEY `fk_longdescs_tags_activity_who_profiles_userid` (`who`),
  CONSTRAINT `fk_longdescs_tags_activity_bug_id_bugs_bug_id` FOREIGN KEY (`bug_id`) REFERENCES `bugs` (`bug_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_longdescs_tags_activity_comment_id_longdescs_comment_id` FOREIGN KEY (`comment_id`) REFERENCES `longdescs` (`comment_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_longdescs_tags_activity_who_profiles_userid` FOREIGN KEY (`who`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `longdescs_tags_activity`
--

LOCK TABLES `longdescs_tags_activity` WRITE;
/*!40000 ALTER TABLE `longdescs_tags_activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `longdescs_tags_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `longdescs_tags_weights`
--

DROP TABLE IF EXISTS `longdescs_tags_weights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `longdescs_tags_weights` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `tag` varchar(24) NOT NULL,
  `weight` mediumint(9) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `longdescs_tags_weights_tag_idx` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `longdescs_tags_weights`
--

LOCK TABLES `longdescs_tags_weights` WRITE;
/*!40000 ALTER TABLE `longdescs_tags_weights` DISABLE KEYS */;
/*!40000 ALTER TABLE `longdescs_tags_weights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mail_staging`
--

DROP TABLE IF EXISTS `mail_staging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_staging` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` longblob NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail_staging`
--

LOCK TABLES `mail_staging` WRITE;
/*!40000 ALTER TABLE `mail_staging` DISABLE KEYS */;
/*!40000 ALTER TABLE `mail_staging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `milestones`
--

DROP TABLE IF EXISTS `milestones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `milestones` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `product_id` smallint(6) NOT NULL,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `milestones_product_id_idx` (`product_id`,`value`),
  CONSTRAINT `fk_milestones_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `milestones`
--

LOCK TABLES `milestones` WRITE;
/*!40000 ALTER TABLE `milestones` DISABLE KEYS */;
INSERT INTO `milestones` VALUES (1,1,'---',0,1),(2,2,'---',0,1),(3,3,'---',0,1);
/*!40000 ALTER TABLE `milestones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `namedqueries`
--

DROP TABLE IF EXISTS `namedqueries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `namedqueries` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `userid` mediumint(9) NOT NULL,
  `name` varchar(64) NOT NULL,
  `query` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `namedqueries_userid_idx` (`userid`,`name`),
  CONSTRAINT `fk_namedqueries_userid_profiles_userid` FOREIGN KEY (`userid`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `namedqueries`
--

LOCK TABLES `namedqueries` WRITE;
/*!40000 ALTER TABLE `namedqueries` DISABLE KEYS */;
/*!40000 ALTER TABLE `namedqueries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `namedqueries_link_in_footer`
--

DROP TABLE IF EXISTS `namedqueries_link_in_footer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `namedqueries_link_in_footer` (
  `namedquery_id` mediumint(9) NOT NULL,
  `user_id` mediumint(9) NOT NULL,
  UNIQUE KEY `namedqueries_link_in_footer_id_idx` (`namedquery_id`,`user_id`),
  KEY `namedqueries_link_in_footer_userid_idx` (`user_id`),
  CONSTRAINT `fk_namedqueries_link_in_footer_namedquery_id_namedqueries_id` FOREIGN KEY (`namedquery_id`) REFERENCES `namedqueries` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_namedqueries_link_in_footer_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `namedqueries_link_in_footer`
--

LOCK TABLES `namedqueries_link_in_footer` WRITE;
/*!40000 ALTER TABLE `namedqueries_link_in_footer` DISABLE KEYS */;
/*!40000 ALTER TABLE `namedqueries_link_in_footer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `namedquery_group_map`
--

DROP TABLE IF EXISTS `namedquery_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `namedquery_group_map` (
  `namedquery_id` mediumint(9) NOT NULL,
  `group_id` mediumint(9) NOT NULL,
  UNIQUE KEY `namedquery_group_map_namedquery_id_idx` (`namedquery_id`),
  KEY `namedquery_group_map_group_id_idx` (`group_id`),
  CONSTRAINT `fk_namedquery_group_map_group_id_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_namedquery_group_map_namedquery_id_namedqueries_id` FOREIGN KEY (`namedquery_id`) REFERENCES `namedqueries` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `namedquery_group_map`
--

LOCK TABLES `namedquery_group_map` WRITE;
/*!40000 ALTER TABLE `namedquery_group_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `namedquery_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `op_sys`
--

DROP TABLE IF EXISTS `op_sys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `op_sys` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `op_sys_value_idx` (`value`),
  KEY `op_sys_sortkey_idx` (`sortkey`,`value`),
  KEY `op_sys_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `op_sys`
--

LOCK TABLES `op_sys` WRITE;
/*!40000 ALTER TABLE `op_sys` DISABLE KEYS */;
INSERT INTO `op_sys` VALUES (1,'All',100,1,NULL),(2,'Windows',200,1,NULL),(3,'Mac OS',300,1,NULL),(4,'Linux',400,1,NULL),(5,'Other',500,1,NULL);
/*!40000 ALTER TABLE `op_sys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `priority`
--

DROP TABLE IF EXISTS `priority`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `priority` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `priority_value_idx` (`value`),
  KEY `priority_sortkey_idx` (`sortkey`,`value`),
  KEY `priority_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `priority`
--

LOCK TABLES `priority` WRITE;
/*!40000 ALTER TABLE `priority` DISABLE KEYS */;
INSERT INTO `priority` VALUES (1,'Highest',100,1,NULL),(2,'High',200,1,NULL),(3,'Normal',300,1,NULL),(4,'Low',400,1,NULL),(5,'Lowest',500,1,NULL),(6,'---',600,1,NULL);
/*!40000 ALTER TABLE `priority` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `classification_id` smallint(6) NOT NULL DEFAULT 1,
  `description` mediumtext NOT NULL,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `defaultmilestone` varchar(64) NOT NULL DEFAULT '---',
  `allows_unconfirmed` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `products_name_idx` (`name`),
  KEY `fk_products_classification_id_classifications_id` (`classification_id`),
  CONSTRAINT `fk_products_classification_id_classifications_id` FOREIGN KEY (`classification_id`) REFERENCES `classifications` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'TestProduct',1,'This is a test product. This ought to be blown away and replaced with real stuff in a finished installation of bugzilla.',1,'---',1),(2,'Red Hat Enterprise Linux 9',1,'Lorem ipsum',1,'---',1),(3,'SUSE Linux Enterprise Server 15 SP6',1,'Lorem ipsum dolor sit amet',1,'---',1);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_search`
--

DROP TABLE IF EXISTS `profile_search`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profile_search` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` mediumint(9) NOT NULL,
  `bug_list` mediumtext NOT NULL,
  `list_order` mediumtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `profile_search_user_id_idx` (`user_id`),
  CONSTRAINT `fk_profile_search_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_search`
--

LOCK TABLES `profile_search` WRITE;
/*!40000 ALTER TABLE `profile_search` DISABLE KEYS */;
INSERT INTO `profile_search` VALUES (1,1,'1','bug_status,priority,assigned_to,bug_id');
/*!40000 ALTER TABLE `profile_search` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_setting`
--

DROP TABLE IF EXISTS `profile_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profile_setting` (
  `user_id` mediumint(9) NOT NULL,
  `setting_name` varchar(32) NOT NULL,
  `setting_value` varchar(32) NOT NULL,
  UNIQUE KEY `profile_setting_value_unique_idx` (`user_id`,`setting_name`),
  KEY `fk_profile_setting_setting_name_setting_name` (`setting_name`),
  CONSTRAINT `fk_profile_setting_setting_name_setting_name` FOREIGN KEY (`setting_name`) REFERENCES `setting` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_profile_setting_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_setting`
--

LOCK TABLES `profile_setting` WRITE;
/*!40000 ALTER TABLE `profile_setting` DISABLE KEYS */;
/*!40000 ALTER TABLE `profile_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles`
--

DROP TABLE IF EXISTS `profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profiles` (
  `userid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `login_name` varchar(255) NOT NULL,
  `cryptpassword` varchar(128) DEFAULT NULL,
  `realname` varchar(255) NOT NULL DEFAULT '',
  `disabledtext` mediumtext NOT NULL DEFAULT '',
  `disable_mail` tinyint(4) NOT NULL DEFAULT 0,
  `mybugslink` tinyint(4) NOT NULL DEFAULT 1,
  `extern_id` varchar(64) DEFAULT NULL,
  `is_enabled` tinyint(4) NOT NULL DEFAULT 1,
  `last_seen_date` datetime DEFAULT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `profiles_login_name_idx` (`login_name`),
  UNIQUE KEY `profiles_extern_id_idx` (`extern_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles`
--

LOCK TABLES `profiles` WRITE;
/*!40000 ALTER TABLE `profiles` DISABLE KEYS */;
INSERT INTO `profiles` VALUES (1,'andreas@hasenkopf.xyz','2207pp7o,ialUTtf7x78ge5SbbN7+W+1lXGJBXmMlYt26C1egd4g{SHA-256}','Andreas','',0,1,NULL,1,'2023-11-27 00:00:00');
/*!40000 ALTER TABLE `profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles_activity`
--

DROP TABLE IF EXISTS `profiles_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profiles_activity` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `userid` mediumint(9) NOT NULL,
  `who` mediumint(9) NOT NULL,
  `profiles_when` datetime NOT NULL,
  `fieldid` mediumint(9) NOT NULL,
  `oldvalue` tinytext DEFAULT NULL,
  `newvalue` tinytext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `profiles_activity_userid_idx` (`userid`),
  KEY `profiles_activity_profiles_when_idx` (`profiles_when`),
  KEY `profiles_activity_fieldid_idx` (`fieldid`),
  KEY `fk_profiles_activity_who_profiles_userid` (`who`),
  CONSTRAINT `fk_profiles_activity_fieldid_fielddefs_id` FOREIGN KEY (`fieldid`) REFERENCES `fielddefs` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_profiles_activity_userid_profiles_userid` FOREIGN KEY (`userid`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_profiles_activity_who_profiles_userid` FOREIGN KEY (`who`) REFERENCES `profiles` (`userid`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles_activity`
--

LOCK TABLES `profiles_activity` WRITE;
/*!40000 ALTER TABLE `profiles_activity` DISABLE KEYS */;
INSERT INTO `profiles_activity` VALUES (1,1,1,'2023-09-20 13:12:55',33,NULL,'2023-09-20 13:12:55');
/*!40000 ALTER TABLE `profiles_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quips`
--

DROP TABLE IF EXISTS `quips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `quips` (
  `quipid` mediumint(9) NOT NULL AUTO_INCREMENT,
  `userid` mediumint(9) DEFAULT NULL,
  `quip` varchar(512) NOT NULL,
  `approved` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`quipid`),
  KEY `fk_quips_userid_profiles_userid` (`userid`),
  CONSTRAINT `fk_quips_userid_profiles_userid` FOREIGN KEY (`userid`) REFERENCES `profiles` (`userid`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quips`
--

LOCK TABLES `quips` WRITE;
/*!40000 ALTER TABLE `quips` DISABLE KEYS */;
/*!40000 ALTER TABLE `quips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rep_platform`
--

DROP TABLE IF EXISTS `rep_platform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rep_platform` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rep_platform_value_idx` (`value`),
  KEY `rep_platform_sortkey_idx` (`sortkey`,`value`),
  KEY `rep_platform_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rep_platform`
--

LOCK TABLES `rep_platform` WRITE;
/*!40000 ALTER TABLE `rep_platform` DISABLE KEYS */;
INSERT INTO `rep_platform` VALUES (1,'All',100,1,NULL),(2,'PC',200,1,NULL),(3,'Macintosh',300,1,NULL),(4,'Other',400,1,NULL);
/*!40000 ALTER TABLE `rep_platform` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reports`
--

DROP TABLE IF EXISTS `reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reports` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `user_id` mediumint(9) NOT NULL,
  `name` varchar(64) NOT NULL,
  `query` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reports_user_id_idx` (`user_id`,`name`),
  CONSTRAINT `fk_reports_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reports`
--

LOCK TABLES `reports` WRITE;
/*!40000 ALTER TABLE `reports` DISABLE KEYS */;
/*!40000 ALTER TABLE `reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resolution`
--

DROP TABLE IF EXISTS `resolution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resolution` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  `visibility_value_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resolution_value_idx` (`value`),
  KEY `resolution_sortkey_idx` (`sortkey`,`value`),
  KEY `resolution_visibility_value_id_idx` (`visibility_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resolution`
--

LOCK TABLES `resolution` WRITE;
/*!40000 ALTER TABLE `resolution` DISABLE KEYS */;
INSERT INTO `resolution` VALUES (1,'',100,1,NULL),(2,'FIXED',200,1,NULL),(3,'INVALID',300,1,NULL),(4,'WONTFIX',400,1,NULL),(5,'DUPLICATE',500,1,NULL),(6,'WORKSFORME',600,1,NULL);
/*!40000 ALTER TABLE `resolution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `series`
--

DROP TABLE IF EXISTS `series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series` (
  `series_id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `creator` mediumint(9) DEFAULT NULL,
  `category` smallint(6) NOT NULL,
  `subcategory` smallint(6) NOT NULL,
  `name` varchar(64) NOT NULL,
  `frequency` smallint(6) NOT NULL,
  `query` mediumtext NOT NULL,
  `is_public` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`series_id`),
  UNIQUE KEY `series_category_idx` (`category`,`subcategory`,`name`),
  KEY `series_creator_idx` (`creator`),
  KEY `fk_series_subcategory_series_categories_id` (`subcategory`),
  CONSTRAINT `fk_series_category_series_categories_id` FOREIGN KEY (`category`) REFERENCES `series_categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_series_creator_profiles_userid` FOREIGN KEY (`creator`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_series_subcategory_series_categories_id` FOREIGN KEY (`subcategory`) REFERENCES `series_categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `series`
--

LOCK TABLES `series` WRITE;
/*!40000 ALTER TABLE `series` DISABLE KEYS */;
INSERT INTO `series` VALUES (1,1,1,2,'UNCONFIRMED',1,'bug_status=UNCONFIRMED&product=Red%20Hat%20Enterprise%20Linux%209',1),(2,1,1,2,'CONFIRMED',1,'bug_status=CONFIRMED&product=Red%20Hat%20Enterprise%20Linux%209',1),(3,1,1,2,'IN_PROGRESS',1,'bug_status=IN_PROGRESS&product=Red%20Hat%20Enterprise%20Linux%209',1),(4,1,1,2,'RESOLVED',1,'bug_status=RESOLVED&product=Red%20Hat%20Enterprise%20Linux%209',1),(5,1,1,2,'VERIFIED',1,'bug_status=VERIFIED&product=Red%20Hat%20Enterprise%20Linux%209',1),(6,1,1,2,'FIXED',1,'resolution=FIXED&product=Red%20Hat%20Enterprise%20Linux%209',1),(7,1,1,2,'INVALID',1,'resolution=INVALID&product=Red%20Hat%20Enterprise%20Linux%209',1),(8,1,1,2,'WONTFIX',1,'resolution=WONTFIX&product=Red%20Hat%20Enterprise%20Linux%209',1),(9,1,1,2,'DUPLICATE',1,'resolution=DUPLICATE&product=Red%20Hat%20Enterprise%20Linux%209',1),(10,1,1,2,'WORKSFORME',1,'resolution=WORKSFORME&product=Red%20Hat%20Enterprise%20Linux%209',1),(11,1,1,2,'All Open',1,'bug_status=UNCONFIRMED&bug_status=CONFIRMED&bug_status=IN_PROGRESS&product=Red%20Hat%20Enterprise%20Linux%209',1),(12,1,1,3,'All Open',1,'field0-0-0=resolution&type0-0-0=notregexp&value0-0-0=.&product=Red%20Hat%20Enterprise%20Linux%209&component=python-bugzilla',1),(13,1,1,3,'All Closed',1,'field0-0-0=resolution&type0-0-0=regexp&value0-0-0=.&product=Red%20Hat%20Enterprise%20Linux%209&component=python-bugzilla',1),(14,1,4,2,'UNCONFIRMED',1,'bug_status=UNCONFIRMED&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(15,1,4,2,'CONFIRMED',1,'bug_status=CONFIRMED&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(16,1,4,2,'IN_PROGRESS',1,'bug_status=IN_PROGRESS&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(17,1,4,2,'RESOLVED',1,'bug_status=RESOLVED&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(18,1,4,2,'VERIFIED',1,'bug_status=VERIFIED&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(19,1,4,2,'FIXED',1,'resolution=FIXED&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(20,1,4,2,'INVALID',1,'resolution=INVALID&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(21,1,4,2,'WONTFIX',1,'resolution=WONTFIX&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(22,1,4,2,'DUPLICATE',1,'resolution=DUPLICATE&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(23,1,4,2,'WORKSFORME',1,'resolution=WORKSFORME&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(24,1,4,2,'All Open',1,'bug_status=UNCONFIRMED&bug_status=CONFIRMED&bug_status=IN_PROGRESS&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6',1),(25,1,4,5,'All Open',1,'field0-0-0=resolution&type0-0-0=notregexp&value0-0-0=.&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6&component=Kernel',1),(26,1,4,5,'All Closed',1,'field0-0-0=resolution&type0-0-0=regexp&value0-0-0=.&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6&component=Kernel',1),(27,1,4,6,'All Open',1,'field0-0-0=resolution&type0-0-0=notregexp&value0-0-0=.&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6&component=Containers',1),(28,1,4,6,'All Closed',1,'field0-0-0=resolution&type0-0-0=regexp&value0-0-0=.&product=SUSE%20Linux%20Enterprise%20Server%2015%20SP6&component=Containers',1);
/*!40000 ALTER TABLE `series` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `series_categories`
--

DROP TABLE IF EXISTS `series_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series_categories` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `series_categories_name_idx` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `series_categories`
--

LOCK TABLES `series_categories` WRITE;
/*!40000 ALTER TABLE `series_categories` DISABLE KEYS */;
INSERT INTO `series_categories` VALUES (2,'-All-'),(6,'Containers'),(5,'Kernel'),(3,'python-bugzilla'),(1,'Red Hat Enterprise Linux 9'),(4,'SUSE Linux Enterprise Server 15 SP6');
/*!40000 ALTER TABLE `series_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `series_data`
--

DROP TABLE IF EXISTS `series_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series_data` (
  `series_id` mediumint(9) NOT NULL,
  `series_date` datetime NOT NULL,
  `series_value` mediumint(9) NOT NULL,
  UNIQUE KEY `series_data_series_id_idx` (`series_id`,`series_date`),
  CONSTRAINT `fk_series_data_series_id_series_series_id` FOREIGN KEY (`series_id`) REFERENCES `series` (`series_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `series_data`
--

LOCK TABLES `series_data` WRITE;
/*!40000 ALTER TABLE `series_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `series_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setting`
--

DROP TABLE IF EXISTS `setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setting` (
  `name` varchar(32) NOT NULL,
  `default_value` varchar(32) NOT NULL,
  `is_enabled` tinyint(4) NOT NULL DEFAULT 1,
  `subclass` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setting`
--

LOCK TABLES `setting` WRITE;
/*!40000 ALTER TABLE `setting` DISABLE KEYS */;
INSERT INTO `setting` VALUES ('bugmail_new_prefix','on',1,NULL),('comment_box_position','before_comments',1,NULL),('comment_sort_order','oldest_to_newest',1,NULL),('csv_colsepchar',',',1,NULL),('display_quips','on',1,NULL),('email_format','html',1,NULL),('lang','en',1,'Lang'),('possible_duplicates','on',1,NULL),('post_bug_submit_action','next_bug',1,NULL),('quicksearch_fulltext','on',1,NULL),('quote_replies','quoted_reply',1,NULL),('requestee_cc','on',1,NULL),('skin','Dusk',1,'Skin'),('state_addselfcc','cc_unless_role',1,NULL),('timezone','local',1,'Timezone'),('zoom_textareas','on',1,NULL);
/*!40000 ALTER TABLE `setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setting_value`
--

DROP TABLE IF EXISTS `setting_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setting_value` (
  `name` varchar(32) NOT NULL,
  `value` varchar(32) NOT NULL,
  `sortindex` smallint(6) NOT NULL,
  UNIQUE KEY `setting_value_nv_unique_idx` (`name`,`value`),
  UNIQUE KEY `setting_value_ns_unique_idx` (`name`,`sortindex`),
  CONSTRAINT `fk_setting_value_name_setting_name` FOREIGN KEY (`name`) REFERENCES `setting` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setting_value`
--

LOCK TABLES `setting_value` WRITE;
/*!40000 ALTER TABLE `setting_value` DISABLE KEYS */;
INSERT INTO `setting_value` VALUES ('bugmail_new_prefix','on',5),('bugmail_new_prefix','off',10),('comment_box_position','before_comments',5),('comment_box_position','after_comments',10),('comment_sort_order','oldest_to_newest',5),('comment_sort_order','newest_to_oldest',10),('comment_sort_order','newest_to_oldest_desc_first',15),('csv_colsepchar',',',5),('csv_colsepchar',';',10),('display_quips','on',5),('display_quips','off',10),('email_format','html',5),('email_format','text_only',10),('possible_duplicates','on',5),('possible_duplicates','off',10),('post_bug_submit_action','next_bug',5),('post_bug_submit_action','same_bug',10),('post_bug_submit_action','nothing',15),('quicksearch_fulltext','on',5),('quicksearch_fulltext','off',10),('quote_replies','quoted_reply',5),('quote_replies','simple_reply',10),('quote_replies','off',15),('requestee_cc','on',5),('requestee_cc','off',10),('state_addselfcc','always',5),('state_addselfcc','never',10),('state_addselfcc','cc_unless_role',15),('zoom_textareas','on',5),('zoom_textareas','off',10);
/*!40000 ALTER TABLE `setting_value` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status_workflow`
--

DROP TABLE IF EXISTS `status_workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status_workflow` (
  `old_status` smallint(6) DEFAULT NULL,
  `new_status` smallint(6) NOT NULL,
  `require_comment` tinyint(4) NOT NULL DEFAULT 0,
  UNIQUE KEY `status_workflow_idx` (`old_status`,`new_status`),
  KEY `fk_status_workflow_new_status_bug_status_id` (`new_status`),
  CONSTRAINT `fk_status_workflow_new_status_bug_status_id` FOREIGN KEY (`new_status`) REFERENCES `bug_status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_status_workflow_old_status_bug_status_id` FOREIGN KEY (`old_status`) REFERENCES `bug_status` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status_workflow`
--

LOCK TABLES `status_workflow` WRITE;
/*!40000 ALTER TABLE `status_workflow` DISABLE KEYS */;
INSERT INTO `status_workflow` VALUES (NULL,1,0),(NULL,2,0),(NULL,3,0),(1,2,0),(1,3,0),(1,4,0),(2,3,0),(2,4,0),(3,2,0),(3,4,0),(4,1,0),(4,2,0),(4,5,0),(5,1,0),(5,2,0);
/*!40000 ALTER TABLE `status_workflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `user_id` mediumint(9) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_user_id_idx` (`user_id`,`name`),
  CONSTRAINT `fk_tag_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tokens`
--

DROP TABLE IF EXISTS `tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tokens` (
  `userid` mediumint(9) DEFAULT NULL,
  `issuedate` datetime NOT NULL,
  `token` varchar(16) NOT NULL,
  `tokentype` varchar(16) NOT NULL,
  `eventdata` tinytext DEFAULT NULL,
  PRIMARY KEY (`token`),
  KEY `tokens_userid_idx` (`userid`),
  CONSTRAINT `fk_tokens_userid_profiles_userid` FOREIGN KEY (`userid`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tokens`
--

LOCK TABLES `tokens` WRITE;
/*!40000 ALTER TABLE `tokens` DISABLE KEYS */;
INSERT INTO `tokens` VALUES (1,'2023-11-27 15:46:15','5HVJhRRo6t','session','edit_parameters'),(1,'2023-11-27 12:25:54','a9MgwT7N7x','session','edit_product'),(1,'2023-11-27 15:42:50','CRSwDhzaXc','session','edit_parameters'),(1,'2023-11-27 12:29:18','DXFuAIZ5GH','session','edit_product'),(1,'2023-09-20 13:13:14','ery9F3ZaAV','session','edit_user_prefs'),(1,'2023-11-27 15:44:26','gnPazrbni2','session','edit_product'),(1,'2023-11-27 15:43:10','GZT1mYgIAF','session','edit_settings'),(1,'2023-11-27 15:42:57','hYkjAGXNIj','session','add_field'),(1,'2023-11-27 15:46:35','ibDe8MPzGE','session','edit_parameters'),(1,'2023-09-20 13:13:14','oukIJJwYod','api_token',''),(1,'2023-11-27 12:26:29','PIjhZLJ29K','session','edit_product'),(1,'2023-11-27 12:23:39','pIrqNpsRDo','api_token',''),(1,'2023-11-27 15:44:36','rkyOtDBxr4','session','edit_group_controls'),(1,'2023-09-20 13:13:20','VLrgLovfH9','session','edit_user_prefs'),(1,'2023-11-27 15:45:59','xgQpxIS10M','session','edit_user_prefs');
/*!40000 ALTER TABLE `tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_error`
--

DROP TABLE IF EXISTS `ts_error`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ts_error` (
  `error_time` int(11) NOT NULL,
  `jobid` int(11) NOT NULL,
  `message` varchar(255) NOT NULL,
  `funcid` int(11) NOT NULL DEFAULT 0,
  KEY `ts_error_funcid_idx` (`funcid`,`error_time`),
  KEY `ts_error_error_time_idx` (`error_time`),
  KEY `ts_error_jobid_idx` (`jobid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_error`
--

LOCK TABLES `ts_error` WRITE;
/*!40000 ALTER TABLE `ts_error` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_error` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_exitstatus`
--

DROP TABLE IF EXISTS `ts_exitstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ts_exitstatus` (
  `jobid` int(11) NOT NULL AUTO_INCREMENT,
  `funcid` int(11) NOT NULL DEFAULT 0,
  `status` smallint(6) DEFAULT NULL,
  `completion_time` int(11) DEFAULT NULL,
  `delete_after` int(11) DEFAULT NULL,
  PRIMARY KEY (`jobid`),
  KEY `ts_exitstatus_funcid_idx` (`funcid`),
  KEY `ts_exitstatus_delete_after_idx` (`delete_after`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_exitstatus`
--

LOCK TABLES `ts_exitstatus` WRITE;
/*!40000 ALTER TABLE `ts_exitstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_exitstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_funcmap`
--

DROP TABLE IF EXISTS `ts_funcmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ts_funcmap` (
  `funcid` int(11) NOT NULL AUTO_INCREMENT,
  `funcname` varchar(255) NOT NULL,
  PRIMARY KEY (`funcid`),
  UNIQUE KEY `ts_funcmap_funcname_idx` (`funcname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_funcmap`
--

LOCK TABLES `ts_funcmap` WRITE;
/*!40000 ALTER TABLE `ts_funcmap` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_funcmap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_job`
--

DROP TABLE IF EXISTS `ts_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ts_job` (
  `jobid` int(11) NOT NULL AUTO_INCREMENT,
  `funcid` int(11) NOT NULL,
  `arg` longblob DEFAULT NULL,
  `uniqkey` varchar(255) DEFAULT NULL,
  `insert_time` int(11) DEFAULT NULL,
  `run_after` int(11) NOT NULL,
  `grabbed_until` int(11) NOT NULL,
  `priority` smallint(6) DEFAULT NULL,
  `coalesce` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`jobid`),
  UNIQUE KEY `ts_job_funcid_idx` (`funcid`,`uniqkey`),
  KEY `ts_job_run_after_idx` (`run_after`,`funcid`),
  KEY `ts_job_coalesce_idx` (`coalesce`,`funcid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_job`
--

LOCK TABLES `ts_job` WRITE;
/*!40000 ALTER TABLE `ts_job` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_job` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ts_note`
--

DROP TABLE IF EXISTS `ts_note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ts_note` (
  `jobid` int(11) NOT NULL,
  `notekey` varchar(255) DEFAULT NULL,
  `value` longblob DEFAULT NULL,
  UNIQUE KEY `ts_note_jobid_idx` (`jobid`,`notekey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ts_note`
--

LOCK TABLES `ts_note` WRITE;
/*!40000 ALTER TABLE `ts_note` DISABLE KEYS */;
/*!40000 ALTER TABLE `ts_note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_api_keys`
--

DROP TABLE IF EXISTS `user_api_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_api_keys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` mediumint(9) NOT NULL,
  `api_key` varchar(40) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `revoked` tinyint(4) NOT NULL DEFAULT 0,
  `last_used` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_api_keys_api_key_idx` (`api_key`),
  KEY `user_api_keys_user_id_idx` (`user_id`),
  CONSTRAINT `fk_user_api_keys_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_api_keys`
--

LOCK TABLES `user_api_keys` WRITE;
/*!40000 ALTER TABLE `user_api_keys` DISABLE KEYS */;
INSERT INTO `user_api_keys` VALUES (1,1,'AxBntHGSL97CmoTahkey8RNyo2K65NEfJBuk5ATe','',0,NULL);
/*!40000 ALTER TABLE `user_api_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_map`
--

DROP TABLE IF EXISTS `user_group_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_map` (
  `user_id` mediumint(9) NOT NULL,
  `group_id` mediumint(9) NOT NULL,
  `isbless` tinyint(4) NOT NULL DEFAULT 0,
  `grant_type` tinyint(4) NOT NULL DEFAULT 0,
  UNIQUE KEY `user_group_map_user_id_idx` (`user_id`,`group_id`,`grant_type`,`isbless`),
  KEY `fk_user_group_map_group_id_groups_id` (`group_id`),
  CONSTRAINT `fk_user_group_map_group_id_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_group_map_user_id_profiles_userid` FOREIGN KEY (`user_id`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_map`
--

LOCK TABLES `user_group_map` WRITE;
/*!40000 ALTER TABLE `user_group_map` DISABLE KEYS */;
INSERT INTO `user_group_map` VALUES (1,1,0,0),(1,1,1,0),(1,3,0,0),(1,8,0,2);
/*!40000 ALTER TABLE `user_group_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `versions`
--

DROP TABLE IF EXISTS `versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `versions` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `value` varchar(64) NOT NULL,
  `product_id` smallint(6) NOT NULL,
  `isactive` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `versions_product_id_idx` (`product_id`,`value`),
  CONSTRAINT `fk_versions_product_id_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `versions`
--

LOCK TABLES `versions` WRITE;
/*!40000 ALTER TABLE `versions` DISABLE KEYS */;
INSERT INTO `versions` VALUES (1,'unspecified',1,1),(2,'unspecified',2,1),(3,'9.0',2,1),(4,'9.1',2,1),(5,'unspecified',3,1);
/*!40000 ALTER TABLE `versions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `watch`
--

DROP TABLE IF EXISTS `watch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `watch` (
  `watcher` mediumint(9) NOT NULL,
  `watched` mediumint(9) NOT NULL,
  UNIQUE KEY `watch_watcher_idx` (`watcher`,`watched`),
  KEY `watch_watched_idx` (`watched`),
  CONSTRAINT `fk_watch_watched_profiles_userid` FOREIGN KEY (`watched`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_watch_watcher_profiles_userid` FOREIGN KEY (`watcher`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `watch`
--

LOCK TABLES `watch` WRITE;
/*!40000 ALTER TABLE `watch` DISABLE KEYS */;
/*!40000 ALTER TABLE `watch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whine_events`
--

DROP TABLE IF EXISTS `whine_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whine_events` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `owner_userid` mediumint(9) NOT NULL,
  `subject` varchar(128) DEFAULT NULL,
  `body` mediumtext DEFAULT NULL,
  `mailifnobugs` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `fk_whine_events_owner_userid_profiles_userid` (`owner_userid`),
  CONSTRAINT `fk_whine_events_owner_userid_profiles_userid` FOREIGN KEY (`owner_userid`) REFERENCES `profiles` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whine_events`
--

LOCK TABLES `whine_events` WRITE;
/*!40000 ALTER TABLE `whine_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `whine_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whine_queries`
--

DROP TABLE IF EXISTS `whine_queries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whine_queries` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `eventid` mediumint(9) NOT NULL,
  `query_name` varchar(64) NOT NULL DEFAULT '',
  `sortkey` smallint(6) NOT NULL DEFAULT 0,
  `onemailperbug` tinyint(4) NOT NULL DEFAULT 0,
  `title` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `whine_queries_eventid_idx` (`eventid`),
  CONSTRAINT `fk_whine_queries_eventid_whine_events_id` FOREIGN KEY (`eventid`) REFERENCES `whine_events` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whine_queries`
--

LOCK TABLES `whine_queries` WRITE;
/*!40000 ALTER TABLE `whine_queries` DISABLE KEYS */;
/*!40000 ALTER TABLE `whine_queries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whine_schedules`
--

DROP TABLE IF EXISTS `whine_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whine_schedules` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `eventid` mediumint(9) NOT NULL,
  `run_day` varchar(32) DEFAULT NULL,
  `run_time` varchar(32) DEFAULT NULL,
  `run_next` datetime DEFAULT NULL,
  `mailto` mediumint(9) NOT NULL,
  `mailto_type` smallint(6) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `whine_schedules_run_next_idx` (`run_next`),
  KEY `whine_schedules_eventid_idx` (`eventid`),
  CONSTRAINT `fk_whine_schedules_eventid_whine_events_id` FOREIGN KEY (`eventid`) REFERENCES `whine_events` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whine_schedules`
--

LOCK TABLES `whine_schedules` WRITE;
/*!40000 ALTER TABLE `whine_schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `whine_schedules` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-11-27 16:56:56
