import unittest
from datetime import date
from pathlib import Path

import joblib

from src.alert_system import AlertSystem
from utils.auth import AuthSystem


ROOT = Path(__file__).resolve().parent.parent


class AlertSystemContractTest(unittest.TestCase):
    def test_zero_tolerance_diseases_do_not_alert_without_cases(self):
        for disease in ["peste", "fha", "fievre jaune", "dracunculose"]:
            with self.subTest(disease=disease):
                self.assertEqual(AlertSystem.classify_alert_level(disease, 0, 0), "INFO")

    def test_zero_tolerance_diseases_become_critical_with_one_case(self):
        for disease in ["peste", "fha", "fievre jaune", "dracunculose"]:
            with self.subTest(disease=disease):
                self.assertEqual(AlertSystem.classify_alert_level(disease, 1, 0), "CRITIQUE")

    def test_growth_thresholds_follow_ordered_idsr_escalation(self):
        self.assertEqual(AlertSystem.classify_alert_level("cholera", 0, 0), "INFO")
        self.assertEqual(AlertSystem.classify_alert_level("cholera", 0, 10), "FAIBLE")
        self.assertEqual(AlertSystem.classify_alert_level("cholera", 0, 25), "MODEREE")
        self.assertEqual(AlertSystem.classify_alert_level("cholera", 0, 50), "HAUTE")
        self.assertEqual(AlertSystem.classify_alert_level("cholera", 0, 100), "CRITIQUE")

    def test_threshold_audit_exposes_reference_principles(self):
        audit = AlertSystem().get_threshold_audit("cholera")
        self.assertIn("thresholds", audit)
        self.assertIn("references", audit)
        self.assertTrue(audit["references"]["idsr"])
        self.assertTrue(audit["thresholds"]["note"])


class AuthSystemContractTest(unittest.TestCase):
    def test_user_registration_authentication_and_prediction_audit(self):
        db_path = ROOT / "database" / "test_contract_users.db"
        for candidate in [db_path, db_path.with_suffix(".db-wal"), db_path.with_suffix(".db-shm")]:
            if candidate.exists():
                candidate.unlink()
        auth = AuthSystem(db_path=db_path)

        ok, message = auth.register_authority(
            "autorite_test",
            "MotDePasse@2026",
            "Nom",
            "Prenom",
            "autorite.test@example.org",
            "+243000000000",
            "Kinshasa",
            "Kinshasa Centre",
        )
        self.assertTrue(ok, message)

        user = auth.authenticate("autorite_test", "MotDePasse@2026")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "autorite_sanitaire")

        conn = auth._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (
                disease, province, zone_sante, week, year, current_cases,
                predicted_cases, growth_rate, alert_level, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Choléra", "Kinshasa", "Kinshasa Centre", 28, 2026, 4, 9, 125.0, "CRITIQUE", "Alerte de test"),
        )
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        recorded = auth.record_prediction_run(
            disease="Choléra",
            province="Kinshasa",
            zone_sante="Kinshasa Centre",
            target_date=date(2026, 7, 8),
            week=28,
            year=2026,
            previous_cases=4,
            predicted_cases=9,
            model_r2=0.736,
            delivery_mode="Province de la saisie",
            delivery_target="Kinshasa",
            emitted_by=int(user["id"]),
            alert_id=int(alert_id),
        )
        self.assertTrue(recorded)
        self.assertEqual(len(auth.get_prediction_runs(limit=10)), 1)


class ModelBundleContractTest(unittest.TestCase):
    def test_model_bundle_contains_trained_models(self):
        bundle_path = ROOT / "models" / "trained" / "models.pkl"
        self.assertTrue(bundle_path.exists(), "models/trained/models.pkl est introuvable")
        bundle = joblib.load(bundle_path)
        self.assertIn("best_models", bundle)
        self.assertGreaterEqual(len(bundle["best_models"]), 1)


if __name__ == "__main__":
    unittest.main()
