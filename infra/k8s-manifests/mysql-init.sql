CREATE DATABASE IF NOT EXISTS nekocafe_reservation CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS nekocafe_member CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON nekocafe_reservation.* TO 'nekocafe'@'%';
GRANT ALL PRIVILEGES ON nekocafe_member.* TO 'nekocafe'@'%';
FLUSH PRIVILEGES;
