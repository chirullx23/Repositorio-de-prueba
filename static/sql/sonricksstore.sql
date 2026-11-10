-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 10-11-2026 a las 22:27:14
-- Versión del servidor: 8.0.46
-- Versión de PHP: 7.4.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sonricksstore`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administra`
--

CREATE TABLE `administra` (
  `idadministra` int NOT NULL,
  `idusuario` int NOT NULL,
  `idbalon` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `balon`
--

CREATE TABLE `balon` (
  `balon` int NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `marca` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL,
  `categoria` varchar(60) COLLATE utf8mb4_spanish_ci NOT NULL,
  `precio` float NOT NULL,
  `existencias` int NOT NULL,
  `imagen` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `balon`
--

INSERT INTO `balon` (`balon`, `nombre`, `marca`, `categoria`, `precio`, `existencias`, `imagen`) VALUES
(1, 'Balón de Fútbol Puma Orbita 5 Fusión, termosellado, talla 5, para partidos oficiales', 'Puma', 'Fútbol', 899, 25, 'BalonPumaOrbita5.jpg'),
(2, 'Balón de Fútbol Adidas Tango Pro, 32 paneles, talla 5, uso profesional en pasto', 'Adidas', 'Fútbol', 1299, 18, 'BalonAdidasTango.jpg'),
(3, 'Balón de Fútbol Nike Flight Premier League, talla 5, tecnología de vuelo preciso', 'Nike', 'Fútbol', 1799, 12, 'BalonNikeFlight.jpg'),
(4, 'Balón de Fútbol Mikasa Striker Hybrid, talla 5, cámara de látex, entrenamiento', 'Mikasa', 'Fútbol', 529, 30, 'BalonMikasaStrik.jpg'),
(5, 'Balón de Fútbol Voit Clásico Cosido, talla 5, cuero sintético resistente', 'Voit', 'Fútbol', 349, 40, 'BalonVoitClasico.jpg'),
(6, 'Balón de Fútbol Molten Vantaggio 3200, talla 5, cuero PU, partidos de liga', 'Molten', 'Fútbol', 749, 20, 'BalonMoltenVant.jpg'),
(7, 'Balón de Fútbol Umbro Neo Swerve, talla 4, ideal para categorías infantiles', 'Umbro', 'Fútbol', 459, 28, 'BalonUmbroNeo4.jpg'),
(8, 'Balón de Fútbol Under Armour Desafio 395, talla 5, entrenamiento y recreación', 'Under Armour', 'Fútbol', 599, 22, 'BalonUADesafio.jpg'),
(9, 'Balón de Fútbol Select Brillant Super, talla 5, aprobado FIFA Quality Pro', 'Select', 'Fútbol', 1499, 10, 'BalonSelectBrill.jpg'),
(10, 'Balón de Fútbol Joma Challenge II, talla 5, superficie antiderrapante', 'Joma', 'Fútbol', 389, 35, 'BalonJomaChall.jpg'),
(11, 'Balón de Basquetbol Spalding TF-1000 Legacy, talla 7, cuero compuesto interior', 'Spalding', 'Baloncesto', 1199, 15, 'BalonSpaldingTF.jpg'),
(12, 'Balón de Basquetbol Wilson Evolution, talla 7, microfibra, uso en duela', 'Wilson', 'Baloncesto', 1349, 14, 'BalonWilsonEvo.jpg'),
(13, 'Balón de Basquetbol Molten GG7X, talla 7, cuero sintético, agarre superior', 'Molten', 'Baloncesto', 1099, 16, 'BalonMoltenGG7X.jpg'),
(14, 'Balón de Basquetbol Nike Elite Championship, talla 7, uso interior y exterior', 'Nike', 'Baloncesto', 1099, 17, 'BalonNikeElite.jpg'),
(15, 'Balón de Basquetbol Spalding Street Phantom, talla 7, goma resistente exterior', 'Spalding', 'Baloncesto', 649, 26, 'BalonSpaldPhant.jpg'),
(16, 'Balón de Basquetbol Rawlings Sport Series, talla 6, para jugadoras y juveniles', 'Rawlings', 'Baloncesto', 499, 21, 'BalonRawlSport.jpg'),
(17, 'Balón de Basquetbol Voit Slam Dunk, talla 7, hule duradero para cancha de cemento', 'Voit', 'Baloncesto', 379, 33, 'BalonVoitSlam.jpg'),
(18, 'Balón de Basquetbol Adidas Pro 3.0, talla 7, cubierta texturizada de agarre', 'Adidas', 'Baloncesto', 899, 19, 'BalonAdidasPro3.jpg'),
(19, 'Balón de Basquetbol Mikasa BQ1000, talla 7, aprobado FIBA, cuero sintético', 'Mikasa', 'Baloncesto', 1249, 9, 'BalonMikasaBQ.jpg'),
(20, 'Balón de Basquetbol Wilson NBA Authentic, talla 7, edición réplica oficial', 'Wilson', 'Baloncesto', 1599, 8, 'BalonWilsonNBA.jpg'),
(21, 'Balón de Voleibol Mikasa V200W, 18 paneles, cuero sintético, uso en sala', 'Mikasa', 'Voleibol', 1450, 12, 'BalonMikasaV200.jpg'),
(22, 'Balón de Voleibol Molten V5M5000, aprobado FIVB, competencia profesional', 'Molten', 'Voleibol', 1699, 7, 'BalonMoltenV5M.jpg'),
(23, 'Balón de Voleibol Wilson AVP Soft Play, ligero y suave para recreación', 'Wilson', 'Voleibol', 429, 24, 'BalonWilsonAVP.jpg'),
(24, 'Balón de Voleibol Voit Sand Tech, resistente al agua, uso en arena', 'Voit', 'Voleibol', 389, 29, 'BalonVoitSand.jpg'),
(25, 'Balón de Voleibol Penalty 8.0 Pro, microfibra, costura termosellada', 'Penalty', 'Voleibol', 799, 15, 'BalonPenalty8Pro.jpg'),
(26, 'Balón de Voleibol Mikasa VLS300 Beach, para voleibol de playa, colores vivos', 'Mikasa', 'Voleibol', 549, 18, 'BalonMikasaBeach.jpg'),
(27, 'Balón de Futsal Select Futsal Master, bote controlado, talla 4, cancha dura', 'Select', 'Futsal', 679, 20, 'BalonSelectFutsl.jpg'),
(28, 'Balón de Futsal Joma Dali II, bote bajo, talla 62 cm, uso en duela', 'Joma', 'Futsal', 489, 23, 'BalonJomaDali.jpg'),
(29, 'Balón de Futsal Adidas Sala 65, talla 4, cosido a máquina, interior', 'Adidas', 'Futsal', 569, 17, 'BalonAdidasSala.jpg'),
(30, 'Balón de Futsal Puma Futsal Pro, bote reducido, uso en cancha techada', 'Puma', 'Futsal', 629, 14, 'BalonPumaFutsal.jpg'),
(31, 'Balón de Fútbol Playa Mikasa Beach Soccer, resistente a arena y agua salada', 'Mikasa', 'Fútbol Playa', 519, 16, 'BalonMikasaPlaya.jpg'),
(32, 'Balón de Fútbol Playa Nike Beach Pro, talla 5, cámara reforzada, arena', 'Nike', 'Fútbol Playa', 579, 13, 'BalonNikePlaya.jpg'),
(33, 'Balón de Handball Molten H2X3200, talla 2, agarre mejorado para competencia', 'Molten', 'Handball', 799, 11, 'BalonMoltenHand.jpg'),
(34, 'Balón de Handball Select Ultimate Replica, talla 1, juveniles y damas', 'Select', 'Handball', 649, 9, 'BalonSelectHand.jpg'),
(35, 'Balón de Handball Kempa Spectrum Synergy, talla 3, categoría varonil', 'Kempa', 'Handball', 959, 6, 'BalonKempaHand.jpg'),
(36, 'Balón de Fútbol Americano Wilson The Duke, cuero genuino, tamaño oficial NFL', 'Wilson', 'Fútbol Americano', 1899, 8, 'BalonWilsonDuke.jpg'),
(37, 'Balón de Fútbol Americano Wilson TDY Composite, tamaño juvenil, entrenamiento', 'Wilson', 'Fútbol Americano', 699, 15, 'BalonWilsonTDY.jpg'),
(38, 'Balón de Fútbol Americano Nike Vapor One, cuero sintético, agarre en lluvia', 'Nike', 'Fútbol Americano', 989, 10, 'BalonNikeVapor.jpg'),
(39, 'Balón de Fútbol Americano Franklin Grip-Rite, talla juvenil, uso recreativo', 'Franklin', 'Fútbol Americano', 449, 19, 'BalonFranklinGR.jpg'),
(40, 'Balón de Rugby Gilbert Match XV, talla 5, cuero sintético, partidos oficiales', 'Gilbert', 'Rugby', 1099, 7, 'BalonGilbertXV.jpg'),
(41, 'Balón de Rugby Gilbert Barbarian Training, talla 4, para entrenamiento', 'Gilbert', 'Rugby', 499, 12, 'BalonGilbertBarb.jpg'),
(42, 'Balón de Rugby Optimum Tribal, talla 5, goma texturizada, uso en pasto', 'Optimum', 'Rugby', 429, 14, 'BalonOptimTribal.jpg'),
(43, 'Balón de Water Polo Mikasa W6609W, talla 5, resistente al cloro, competencia', 'Mikasa', 'Water Polo', 879, 6, 'BalonMikasaWP.jpg'),
(44, 'Balón de Water Polo Turbo Training, talla 4, agarre en agua, juveniles', 'Turbo', 'Water Polo', 539, 8, 'BalonTurboWP.jpg'),
(45, 'Balón Medicinal Everlast Slam Ball 5 kg, goma sólida, entrenamiento funcional', 'Everlast', 'Entrenamiento', 689, 13, 'BalonEverlast5kg.jpg'),
(46, 'Balón de Entrenamiento Adidas Soft Touch, bote suave, práctica de dribleo', 'Adidas', 'Entrenamiento', 359, 27, 'BalonAdidasSoft.jpg'),
(47, 'Balón de Pilates Gaiam Pelota 65 cm, antiestallido, ejercicio y rehabilitación', 'Gaiam', 'Entrenamiento', 329, 31, 'BalonGaiamPil65.jpg'),
(48, 'Balón de Fútbol Pequeño Puma Mini Skills, talla 1, para practicar habilidades', 'Puma', 'Fútbol', 199, 45, 'BalonPumaMini.jpg'),
(49, 'Balón de Fútbol Nike Strike Team, talla 5, cámara de aire estable, entrenamiento', 'Nike', 'Fútbol', 499, 32, 'BalonNikeStrike.jpg'),
(50, 'Balón de Basquetbol Nike Dominate 8P, talla 6, goma exterior, uso diario', 'Nike', 'Baloncesto', 549, 22, 'BalonNikeDomin.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contiene`
--

CREATE TABLE `contiene` (
  `idcontiene` int NOT NULL,
  `idpedido` int NOT NULL,
  `idbalon` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `realiza`
--

CREATE TABLE `realiza` (
  `idrealiza` int NOT NULL,
  `idusuario` int NOT NULL,
  `idpedido` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id` int NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `clave` varchar(200) COLLATE utf8mb4_spanish_ci NOT NULL,
  `perfil` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci NOT NULL DEFAULT 'U'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id`, `nombre`, `correo`, `clave`, `perfil`) VALUES
(1, 'osvaldo noe', 'noepro@hotmail.com', 'scrypt:32768:8:1$26CwSCrzWjMPsONw$53aaa97c739acff3e9775bd52abdfa273e4ef9fbb85dc475f3572c3891920ba96ff574addcf581259d9e91e69a4c0e0c8e705c5002e32d0773d4dce2c33617b7', 'C'),
(3, 'terreneitor', 'terreneitor@hotmail.com', 'scrypt:32768:8:1$OZzX5X7GPTdlaiTy$05ef2d10977066536c79a187fff8403205edee88f5b46e3801cde6f2ccd58c29c4b544c8b96119eba51cd89515c471cfcb9c829720a5023d030b990caf53ffc0', 'A');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administra`
--
ALTER TABLE `administra`
  ADD PRIMARY KEY (`idadministra`),
  ADD KEY `idusuario` (`idusuario`),
  ADD KEY `idbalon` (`idbalon`);

--
-- Indices de la tabla `balon`
--
ALTER TABLE `balon`
  ADD PRIMARY KEY (`balon`);

--
-- Indices de la tabla `contiene`
--
ALTER TABLE `contiene`
  ADD PRIMARY KEY (`idcontiene`),
  ADD KEY `idpedido` (`idpedido`),
  ADD KEY `idbalon` (`idbalon`),
  ADD KEY `cantidad` (`cantidad`),
  ADD KEY `precio_unitario` (`precio_unitario`);

--
-- Indices de la tabla `realiza`
--
ALTER TABLE `realiza`
  ADD PRIMARY KEY (`idrealiza`),
  ADD KEY `idusuario` (`idusuario`),
  ADD KEY `idpedido` (`idpedido`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `administra`
--
ALTER TABLE `administra`
  MODIFY `idadministra` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `balon`
--
ALTER TABLE `balon`
  MODIFY `balon` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT de la tabla `contiene`
--
ALTER TABLE `contiene`
  MODIFY `idcontiene` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `realiza`
--
ALTER TABLE `realiza`
  MODIFY `idrealiza` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `administra`
--
ALTER TABLE `administra`
  ADD CONSTRAINT `administra_ibfk_1` FOREIGN KEY (`idadministra`) REFERENCES `usuario` (`id`);

--
-- Filtros para la tabla `contiene`
--
ALTER TABLE `contiene`
  ADD CONSTRAINT `contiene_ibfk_1` FOREIGN KEY (`idbalon`) REFERENCES `balon` (`balon`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
