-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 12-12-2022 a las 19:49:18
-- Versión del servidor: 10.4.25-MariaDB
-- Versión de PHP: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sounds`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito`
--

CREATE TABLE `carrito` (
  `fk_user_id` int(10) NOT NULL,
  `fk_id_producto` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(5) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `precio` float NOT NULL,
  `imagen` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre`, `precio`, `imagen`) VALUES
(23, 'Botella de tinta HP Color Negro', 2500, '2022122801Captura1.PNG'),
(24, 'Botella de tinta HP Color Amarillo', 2400, '2022000841gt52-amarillo.jpg'),
(25, 'Botella de tinta HP Color Magenta', 2400, '2022001215gt52-magenta.jpg'),
(27, 'Botella de tinta HP Color Cyan', 2400, '2022001844gt52-cyan.png'),
(28, 'Smart 43\" Samsung FHD', 189000, '2022001953Smart-43-FHD-T5300A-samsung.jpg'),
(29, 'Monitor 19\" Samsung A330N', 89000, '2022002119MONITOR 19 SAMSUNG A330N.jpg'),
(30, 'Impresora HP Ink Tank 315', 45000, '2022002154hp-ink-tank-315.jpg'),
(32, 'Samsung Galaxy J7 2015 (J700m)', 20000, '2022115102galaxyj7-2015.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `user_id` int(10) NOT NULL,
  `user_name` varchar(25) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_pass` varchar(120) NOT NULL,
  `user_role` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`user_id`, `user_name`, `user_email`, `user_pass`, `user_role`) VALUES
(2, 'walter', 'walter@mail.com', 'pbkdf2:sha256:260000$Sn7tmT8OhxVaNsNy$db41af15ef2ead225ed847fcd837d9152371099c71e2bd8795aecd9db83b9593', 0),
(3, 'walterino', 'walter@mail.com', 'pbkdf2:sha256:260000$FH8wZG8tWmonTnqq$47dc304be4ee03039adcdb937ba0cc4ffa1b84e5fd76148730e3be65a9fa1264', 0),
(4, 'jonathan', 'jonka_romero@gmail.com', 'pbkdf2:sha256:260000$y8KAyvwXYu5yw1q9$c76636a188b15acbaea226d33b8b316f129fbcca27561de69b91da35d5c6a8d2', 0),
(5, 'eduardo', 'eduardo@gmail.com', 'pbkdf2:sha256:260000$BZYORQRhSgv951ZH$5bd3720453f559fd89576400f9160ffb4e2a44dd35bbbff6473b95ff20239283', 0),
(11, 'walterCordobes', 'walterDeCordoba@fernet.con.coca', 'pbkdf2:sha256:260000$sqoebQsd7Bv2i03E$d3c7a5fe24e6c39ecfd1f46a995c8599c87e064e165acbb18b6095d820f05bb0', 0),
(12, 'ezequiel', 'eze@gmail.com', 'pbkdf2:sha256:260000$GsZohzKUu2eUKkib$0ec11f951288495e63206c266cf20c6600b557256151a6a0d68e4d9816fc8b59', 0),
(13, 'admin', 'walkeriorus472@gmail.com', 'pbkdf2:sha256:260000$3KZUTArRLeFjIaIG$98f2c82edf0e474d3b7183f011721c9adfc3113911a09ca732b3acbce808006b', 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD KEY `user_id` (`fk_user_id`),
  ADD KEY `prod` (`fk_id_producto`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `user_name` (`user_name`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `user_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD CONSTRAINT `prod` FOREIGN KEY (`fk_id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `user_id` FOREIGN KEY (`fk_user_id`) REFERENCES `usuarios` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
