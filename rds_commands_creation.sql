-- COMMANDS TO CREATE/USE THE DATABASE CONFIGURATION (SCHEMA, DATABASE, TABLES, ...)

-- SCHEMA CREATION
-- CREATE SCHEMA `solar_db` ;

use solar_db;

-- LEADS_TABLE CREATION
CREATE TABLE `solar_db`.`leads_table` (
  `pk_leads` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `lead_id` VARCHAR(50) NOT NULL,
  `first_name` VARCHAR(30) NULL,
  `last_name` VARCHAR(30) NULL,
  `business_name` VARCHAR(28) NULL,
  `street_name` VARCHAR(64) NULL,
  `city` VARCHAR(50) NULL,
  `county` VARCHAR(50) NULL,
  `zip_code` VARCHAR(5) NULL,
  `state` VARCHAR(2) NULL,
  `phone_no` VARCHAR(10) NULL,
  `email_address` VARCHAR(50) NULL,
  `street_address2` VARCHAR(64) NULL,
  `income` VARCHAR(10) NULL,
  `age` VARCHAR(3) NULL,
  `homeowner` VARCHAR(1) NULL,
  `single_family_dwelling` VARCHAR(1) NULL,
  `target_value` VARCHAR(2) NULL,
  `utility_name` VARCHAR(10) NULL,
  `received_date_time` DATETIME NULL,
  `total_usage` INT NULL,
  `account_number` VARCHAR(30) NULL,
  PRIMARY KEY (`pk_leads`),
  UNIQUE INDEX `pk_leads_UNIQUE` (`pk_leads` ASC) VISIBLE)
COMMENT = 'Information about leads';

-- LOAD FAKE SAMPLE DATA TO TABLE
INSERT INTO `solar_db`.`leads_table` (`lead_id`, `first_name`, `last_name`, `street_name`, `city`, `county`, `zip_code`, `state`, `phone_no`, `email_address`, `income`, `age`, `homeowner`, `single_family_dwelling`, `target_value`, `received_date_time`, `account_number`)
  VALUES ('1234567890', 'RICHARD', 'ENGLISH', '39 Albany St', 'CAZENOVIA', '67', '13035', 'NY', '3156552225', 'tinaseegers0927@gmail.com', '100000', '42', 'Y', 'Y', 'A1', '2022-06-09 13:00:00', '12345647890');

INSERT INTO `solar_db`.`leads_table` (`lead_id`, `first_name`, `last_name`, `street_name`, `city`, `county`, `zip_code`, `state`, `phone_no`, `email_address`, `income`, `age`, `homeowner`, `single_family_dwelling`, `target_value`, `received_date_time`, `account_number`)
  VALUES ('3216549870', 'KASIMIR', 'LASZEWKSI', '15661 State Route 31', 'ALBION', '75', '14411', 'NY', '5855892533', 'dckhead66@yahoo.com', '300000', '55', 'Y', 'N', 'D1', '2022-06-09', '3216549875');

INSERT INTO `solar_db`.`leads_table` (`lead_id`, `first_name`, `last_name`, `street_name`, `city`, `county`, `zip_code`, `state`, `phone_no`, `email_address`, `income`, `age`, `homeowner`, `single_family_dwelling`, `target_value`, `received_date_time`, `account_number`)
  VALUES ('1234567895', 'SUE', 'THORNTON', '227 E Main St', 'ELBRIDGE', '159', '13060', 'NY', '3156893781', 'teresahelton61@yahoo.com', '250000', '60', 'Y', 'N', 'C2', '2022-06-07', '2345785632');

INSERT INTO `solar_db`.`leads_table` (`lead_id`, `first_name`, `last_name`, `street_name`, `city`, `county`, `zip_code`, `state`, `phone_no`, `email_address`, `income`, `age`, `homeowner`, `single_family_dwelling`, `target_value`, `received_date_time`, `account_number`)
  VALUES ('98789745649', 'FRANK', 'BERRISH', '1801 State Route 17C', 'OWEGO', '5', '13827', 'NY', '6077547900', '1jadatherealystharper@gmx.us', '232000', '62', 'Y', 'N', 'A3', '2022-05-06', '9875685254');

INSERT INTO `solar_db`.`leads_table` (`lead_id`, `first_name`, `last_name`, `street_name`, `city`, `county`, `zip_code`, `state`, `phone_no`, `email_address`, `income`, `age`, `homeowner`, `single_family_dwelling`, `target_value`, `received_date_time`, `account_number`)
  VALUES ('1231545646', 'RICK', 'PERKINS', '3027 Bear Creek Rd', 'FRANKLINVILLE', '44', '14737', 'NY', '7166762107', 'btomasina@msn.com', '150000', '45', 'Y', 'Y', 'B2', '2022-03-14 15:10:02', '1254698563');


-- API_RECORDS_TABLE CREATION
CREATE TABLE `solar_db`.`api_records_table` (
  `pk_api_records` INT NOT NULL AUTO_INCREMENT,
  `request_date_time` DATETIME NULL,
  `lead_id` VARCHAR(50) NULL,
  `agent_id` VARCHAR(50) NULL,
  `supplier_id` VARCHAR(50) NULL,
  `result` VARCHAR(1024) NULL,
  `source_ip` VARCHAR(128) NULL,
  `internal_aws_ip` VARCHAR(128) NULL,
  `extra_information` VARCHAR(1024) NULL,
  PRIMARY KEY (`pk_api_records`),
  UNIQUE INDEX `pk_api_records_UNIQUE` (`pk_api_records` ASC) VISIBLE);
