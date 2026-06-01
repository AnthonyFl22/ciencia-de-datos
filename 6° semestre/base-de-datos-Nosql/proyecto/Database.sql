-- ───────────────────────────────
--  Base de datos: HotelAnalytics
-- ───────────────────────────────
DROP DATABASE IF EXISTS HotelAnalytics;
CREATE DATABASE HotelAnalytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE HotelAnalytics;

-- 1. Country ────────────────────
CREATE TABLE Country (
    country_id   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(80)  NOT NULL,
    iso_code     CHAR(2)      NOT NULL UNIQUE,
    currency     CHAR(3)      NOT NULL
) ENGINE=InnoDB;

-- 2. HotelChain ─────────────────
CREATE TABLE HotelChain (
    chain_id     INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    founded_year SMALLINT,
    hq_city      VARCHAR(120),
    country_id   INT NOT NULL,
    CONSTRAINT fk_chain_country
      FOREIGN KEY (country_id) REFERENCES Country(country_id)
) ENGINE=InnoDB;

-- 3. Hotel ──────────────────────
CREATE TABLE Hotel (
    hotel_id     INT AUTO_INCREMENT PRIMARY KEY,
    chain_id     INT NOT NULL,
    name         VARCHAR(150) NOT NULL,
    city         VARCHAR(120) NOT NULL,
    address      VARCHAR(255),
    stars        TINYINT      CHECK (stars BETWEEN 1 AND 5),
    CONSTRAINT fk_hotel_chain
      FOREIGN KEY (chain_id) REFERENCES HotelChain(chain_id)
) ENGINE=InnoDB;

-- 4. Room ───────────────────────
CREATE TABLE Room (
    room_id      INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id     INT  NOT NULL,
    room_number  VARCHAR(10) NOT NULL,
    room_type    ENUM('single','double','suite','deluxe') NOT NULL,
    capacity     TINYINT     NOT NULL,
    base_rate    DECIMAL(10,2) NOT NULL,
    UNIQUE KEY uk_room (hotel_id, room_number),
    CONSTRAINT fk_room_hotel
      FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
) ENGINE=InnoDB;

-- 5. Guest ──────────────────────
CREATE TABLE Guest (
    guest_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(60) NOT NULL,
    last_name    VARCHAR(60) NOT NULL,
    email        VARCHAR(120) NOT NULL UNIQUE,
    country_id   INT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_guest_country
      FOREIGN KEY (country_id) REFERENCES Country(country_id)
) ENGINE=InnoDB;

-- 6. Service ────────────────────
CREATE TABLE Service (
    service_id   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    category     ENUM('alimentos','spa','transporte','otros') NOT NULL,
    base_price   DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;

-- 7. Reservation ────────────────
CREATE TABLE Reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id       INT NOT NULL,
    room_id        INT NOT NULL,
    check_in       DATE NOT NULL,
    check_out      DATE NOT NULL,
    status         ENUM('booked','checked_in','checked_out','cancelled') DEFAULT 'booked',
    total_amount   DECIMAL(12,2) NOT NULL,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_checkin (check_in),
    CONSTRAINT fk_res_guest FOREIGN KEY (guest_id) REFERENCES Guest(guest_id),
    CONSTRAINT fk_res_room  FOREIGN KEY (room_id)  REFERENCES Room(room_id)
) ENGINE=InnoDB;

-- 8. ReservationService (puente) ─
CREATE TABLE ReservationService (
    reservation_id INT NOT NULL,
    service_id     INT NOT NULL,
    quantity       TINYINT NOT NULL DEFAULT 1,
    price_unit     DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (reservation_id, service_id),
    CONSTRAINT fk_rs_res  FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id),
    CONSTRAINT fk_rs_serv FOREIGN KEY (service_id)     REFERENCES Service(service_id)
) ENGINE=InnoDB;

-- ¡Listo!  (Catálogos y reservas se insertarán desde Python)
