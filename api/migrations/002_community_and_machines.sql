-- Exercices communautaires + réglages machines utilisateur

ALTER TABLE exercises
  ADD COLUMN created_by_user_id BIGINT NULL,
  ADD CONSTRAINT fk_exercises_created_by FOREIGN KEY (created_by_user_id) REFERENCES users (id) ON DELETE SET NULL;

CREATE INDEX idx_exercises_created_by ON exercises (created_by_user_id);

CREATE TABLE IF NOT EXISTS user_machine_settings (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  exercise_id BIGINT NOT NULL,
  seat_level TINYINT NULL,
  grip_level TINYINT NULL,
  notes VARCHAR(255) NULL,
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  CONSTRAINT fk_machine_settings_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  CONSTRAINT fk_machine_settings_exercise FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE,
  UNIQUE KEY uq_machine_settings_user_exercise (user_id, exercise_id),
  INDEX idx_machine_settings_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
