PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	role TEXT NOT NULL CHECK(role IN ('admin', 'autorite_sanitaire')),
	nom TEXT NOT NULL,
	prenom TEXT NOT NULL,
	email TEXT NOT NULL,
	telephone TEXT,
	province TEXT,
	zone_sante TEXT,
	notification_email INTEGER DEFAULT 1,
	notification_sms INTEGER DEFAULT 0,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_login TIMESTAMP,
	is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS epidemiological_data (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	disease TEXT NOT NULL,
	week INTEGER NOT NULL,
	year INTEGER NOT NULL,
	province TEXT NOT NULL,
	zone_sante TEXT NOT NULL,
	total_cases INTEGER DEFAULT 0,
	total_deaths INTEGER DEFAULT 0,
	incidence_rate REAL,
	mortality_rate REAL,
	entered_by INTEGER,
	entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	validated INTEGER DEFAULT 0,
	FOREIGN KEY (entered_by) REFERENCES users(id) ON DELETE SET NULL,
	UNIQUE(disease, week, year, province, zone_sante)
);

CREATE TABLE IF NOT EXISTS alerts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	disease TEXT NOT NULL,
	province TEXT NOT NULL,
	zone_sante TEXT NOT NULL,
	week INTEGER NOT NULL,
	year INTEGER NOT NULL,
	current_cases INTEGER,
	predicted_cases REAL,
	growth_rate REAL,
	alert_level TEXT,
	message TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	is_read INTEGER DEFAULT 0,
	pdf_generated INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notifications (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER,
	alert_id INTEGER,
	title TEXT,
	message TEXT,
	is_read INTEGER DEFAULT 0,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prediction_runs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	disease TEXT NOT NULL,
	province TEXT NOT NULL,
	zone_sante TEXT NOT NULL,
	target_date TEXT NOT NULL,
	week INTEGER NOT NULL,
	year INTEGER NOT NULL,
	previous_cases INTEGER DEFAULT 0,
	predicted_cases INTEGER DEFAULT 0,
	model_r2 REAL,
	delivery_mode TEXT,
	delivery_target TEXT,
	emitted_by INTEGER,
	alert_id INTEGER,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (emitted_by) REFERENCES users(id) ON DELETE SET NULL,
	FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX IF NOT EXISTS idx_epi_period ON epidemiological_data(year, week, province, zone_sante);
CREATE INDEX IF NOT EXISTS idx_alerts_period ON alerts(year, week, province, zone_sante);
CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prediction_runs_created ON prediction_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prediction_runs_scope ON prediction_runs(province, zone_sante, year, week);
