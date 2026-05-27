-- FitDex — schéma initial (compatible MariaDB / MySQL)

CREATE TABLE IF NOT EXISTS users (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  display_name VARCHAR(80) NOT NULL,
  is_admin TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS muscle_groups (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(64) NOT NULL UNIQUE,
  name_fr VARCHAR(80) NOT NULL,
  icon VARCHAR(64) NULL,
  sort_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS exercises (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(96) NOT NULL UNIQUE,
  name_fr VARCHAR(120) NOT NULL,
  muscle_group_id BIGINT NOT NULL,
  equipment VARCHAR(32) NOT NULL DEFAULT 'machine',
  image_path VARCHAR(255) NULL,
  description TEXT NULL,
  owner_user_id BIGINT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  CONSTRAINT fk_exercises_muscle FOREIGN KEY (muscle_group_id) REFERENCES muscle_groups (id),
  CONSTRAINT fk_exercises_owner FOREIGN KEY (owner_user_id) REFERENCES users (id) ON DELETE CASCADE,
  INDEX idx_exercises_muscle (muscle_group_id),
  INDEX idx_exercises_owner (owner_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS workout_days (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(80) NOT NULL,
  position INT NOT NULL DEFAULT 0,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  CONSTRAINT fk_workout_days_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  INDEX idx_workout_days_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS day_exercises (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  workout_day_id BIGINT NOT NULL,
  exercise_id BIGINT NOT NULL,
  position INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_day_exercises_day FOREIGN KEY (workout_day_id) REFERENCES workout_days (id) ON DELETE CASCADE,
  CONSTRAINT fk_day_exercises_exercise FOREIGN KEY (exercise_id) REFERENCES exercises (id),
  INDEX idx_day_exercises_day (workout_day_id),
  INDEX idx_day_exercises_exercise (exercise_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS workout_sessions (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  workout_day_id BIGINT NULL,
  performed_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  CONSTRAINT fk_workout_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_workout_sessions_day FOREIGN KEY (workout_day_id) REFERENCES workout_days (id) ON DELETE SET NULL,
  INDEX idx_workout_sessions_user (user_id),
  INDEX idx_workout_sessions_day (workout_day_id),
  INDEX idx_workout_sessions_performed (performed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS set_logs (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  session_id BIGINT NOT NULL,
  exercise_id BIGINT NOT NULL,
  set_number INT NOT NULL,
  reps INT NOT NULL,
  weight_kg DECIMAL(6, 2) NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  CONSTRAINT fk_set_logs_session FOREIGN KEY (session_id) REFERENCES workout_sessions (id) ON DELETE CASCADE,
  CONSTRAINT fk_set_logs_exercise FOREIGN KEY (exercise_id) REFERENCES exercises (id),
  INDEX idx_set_logs_session (session_id),
  INDEX idx_set_logs_exercise (exercise_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
