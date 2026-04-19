#!/usr/bin/env python3
"""
Privacy Controls for Room Two Database
Provides fine-grained control over data retention and deletion
"""

import sqlite3
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

class PrivacyControls:
    """
    Comprehensive privacy controls for Room Two database
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.room_two_dir = self.base_dir / "room_two_database"
        self.db_path = self.room_two_dir / "speech_patterns.db"
        self.settings_file = self.room_two_dir / "privacy_settings.json"
        self.audit_log_path = self.room_two_dir / "privacy_audit.log"

        # Load privacy settings
        self.settings = self._load_settings()

        # Ensure directories exist
        self.room_two_dir.mkdir(parents=True, exist_ok=True)

    def _load_settings(self) -> Dict:
        """Load privacy settings"""
        default_settings = {
            'auto_cleanup_enabled': True,
            'retention_days': 365,  # Default: keep data for 1 year
            'batch_retention_days': 180,  # Keep individual batches for 6 months
            'allow_export': True,
            'require_confirmation_for_deletion': True,
            'audit_enabled': True,
            'data_minimization_enabled': True,
            'anonymous_mode': False,
            'backup_enabled': False,
            'backup_retention_days': 30
        }

        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    user_settings = json.load(f)
                    default_settings.update(user_settings)
            except:
                pass

        return default_settings

    def _save_settings(self):
        """Save privacy settings"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def _log_audit_event(self, event_type: str, details: Dict):
        """Log privacy audit event"""
        if not self.settings['audit_enabled']:
            return

        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'user_initiated': True
        }

        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')

    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        if not self.db_path.exists():
            return {'exists': False}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {
            'exists': True,
            'file_size_mb': self.db_path.stat().st_size / (1024 * 1024),
            'tables': {},
            'total_patterns': 0,
            'oldest_data': None,
            'newest_data': None,
            'batches': {}
        }

        # Get table statistics
        tables = [
            'linguistic_patterns', 'function_words', 'structural_patterns',
            'vocabulary_metrics', 'style_markers', 'processing_batches'
        ]

        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                stats['tables'][table] = count
                stats['total_patterns'] += count
            except:
                pass

        # Get date range
        try:
            cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM processing_batches')
            oldest, newest = cursor.fetchone()
            stats['oldest_data'] = oldest
            stats['newest_data'] = newest
        except:
            pass

        # Get batch statistics
        try:
            cursor.execute('''
                SELECT processing_status, COUNT(*), SUM(total_words_processed)
                FROM processing_batches
                GROUP BY processing_status
            ''')
            for status, count, words in cursor.fetchall():
                stats['batches'][status] = {
                    'count': count,
                    'total_words': words or 0
                }
        except:
            pass

        conn.close()

        return stats

    def cleanup_expired_data(self, dry_run: bool = True) -> Dict:
        """
        Clean up expired data based on retention policies
        """
        if not self.settings['auto_cleanup_enabled']:
            return {'enabled': False, 'message': 'Auto cleanup disabled'}

        stats = self.get_database_stats()
        if not stats['exists']:
            return {'error': 'Database does not exist'}

        cutoff_date = datetime.now() - timedelta(days=self.settings['retention_days'])
        batch_cutoff = datetime.now() - timedelta(days=self.settings['batch_retention_days'])

        cleanup_report = {
            'dry_run': dry_run,
            'cutoff_date': cutoff_date.isoformat(),
            'batch_cutoff_date': batch_cutoff.isoformat(),
            'items_to_remove': {},
            'space_to_free_mb': 0
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Find expired batches
        cursor.execute('''
            SELECT batch_id, total_words_processed, created_at
            FROM processing_batches
            WHERE created_at < ?
            AND processing_status = 'complete'
        ''', (cutoff_date.isoformat(),))

        expired_batches = cursor.fetchall()
        cleanup_report['items_to_remove']['batches'] = len(expired_batches)

        if expired_batches:
            total_words = sum(batch[1] for batch in expired_batches)
            cleanup_report['items_to_remove']['total_words'] = total_words

        # Estimate space freed (rough calculation)
        if cleanup_report['items_to_remove']['batches'] > 0:
            cleanup_report['space_to_free_mb'] = (
                cleanup_report['items_to_remove']['batches'] *
                stats['file_size_mb'] / max(stats['total_patterns'], 1)
            )

        if not dry_run and expired_batches:
            print(f"🧹 Cleaning up {len(expired_batches)} expired batches...")

            # Delete patterns from expired batches
            for batch_id, _, _ in expired_batches:
                tables_to_clean = [
                    'linguistic_patterns', 'function_words', 'structural_patterns',
                    'vocabulary_metrics', 'style_markers'
                ]

                for table in tables_to_clean:
                    cursor.execute(f'DELETE FROM {table} WHERE source_batch_id = ?', (batch_id,))

                # Delete the batch record
                cursor.execute('DELETE FROM processing_batches WHERE batch_id = ?', (batch_id,))

            conn.commit()

            self._log_audit_event('cleanup_expired_data', {
                'batches_removed': len(expired_batches),
                'total_words_removed': total_words,
                'cutoff_date': cutoff_date.isoformat()
            })

        conn.close()

        return cleanup_report

    def delete_all_data(self, confirm: str = None, backup: bool = True) -> Dict:
        """
        Delete all data from Room Two with confirmation
        """
        if self.settings['require_confirmation_for_deletion']:
            if confirm != "DELETE_ALL_DATA":
                return {
                    'success': False,
                    'message': 'Confirmation required. Pass confirm="DELETE_ALL_DATA"'
                }

        # Create backup if enabled
        backup_path = None
        if backup and self.settings['backup_enabled']:
            backup_path = self._create_backup()

        # Delete database
        if self.db_path.exists():
            original_size = self.db_path.stat().st_size
            self.db_path.unlink()
        else:
            original_size = 0

        # Delete settings and logs if requested
        metadata_deleted = False
        if confirm == "DELETE_ALL_DATA":
            if self.settings_file.exists():
                self.settings_file.unlink()
            if self.audit_log_path.exists():
                self.audit_log_path.unlink()
            metadata_deleted = True

        # Reinitialize empty database
        from nuclear_safe_room import NuclearSafeRoom
        safe_room = NuclearSafeRoom(str(self.base_dir))

        self._log_audit_event('delete_all_data', {
            'original_size_bytes': original_size,
            'backup_created': backup_path is not None,
            'backup_path': str(backup_path) if backup_path else None,
            'metadata_deleted': metadata_deleted
        })

        return {
            'success': True,
            'original_size_mb': original_size / (1024 * 1024),
            'backup_created': backup_path is not None,
            'backup_path': str(backup_path) if backup_path else None,
            'database_reinitialized': True
        }

    def _create_backup(self) -> Optional[Path]:
        """Create backup of current database"""
        if not self.settings['backup_enabled']:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.room_two_dir / f"backup_{timestamp}.db"

        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"💾 Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def export_data(self, output_path: str = None, format: str = 'json') -> Optional[str]:
        """
        Export data from Room Two
        """
        if not self.settings['allow_export']:
            print("❌ Data export disabled by privacy settings")
            return None

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.room_two_dir / f"export_{timestamp}.{format}"

        output_path = Path(output_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        export_data = {
            'exported_at': datetime.now().isoformat(),
            'privacy_settings': self.settings,
            'statistics': self.get_database_stats(),
            'data': {}
        }

        # Export each table
        tables = [
            'linguistic_patterns', 'function_words', 'structural_patterns',
            'vocabulary_metrics', 'style_markers', 'processing_batches'
        ]

        for table in tables:
            try:
                cursor.execute(f'SELECT * FROM {table}')
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                export_data['data'][table] = {
                    'columns': columns,
                    'rows': rows
                }
            except Exception as e:
                print(f"⚠️  Failed to export {table}: {e}")

        conn.close()

        # Save export
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format == 'csv':
            # Convert to CSV format (simplified)
            import csv
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                for table, data in export_data['data'].items():
                    writer.writerow([f"Table: {table}"])
                    writer.writerow(data['columns'])
                    for row in data['rows']:
                        writer.writerow(row)
                    writer.writerow([])  # Empty row between tables

        self._log_audit_event('export_data', {
            'output_path': str(output_path),
            'format': format,
            'tables_exported': len(export_data['data'])
        })

        print(f"📤 Data exported to: {output_path}")
        return str(output_path)

    def anonymize_data(self, dry_run: bool = True) -> Dict:
        """
        Remove potentially identifying information from data
        """
        if not self.settings['anonymous_mode']:
            return {'enabled': False, 'message': 'Anonymous mode disabled'}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        anonymization_report = {
            'dry_run': dry_run,
            'items_anonymized': {},
            'tables_processed': []
        }

        # Anonymize batch IDs (they might contain timestamps or identifiers)
        try:
            cursor.execute('SELECT batch_id FROM processing_batches')
            original_batch_ids = [row[0] for row in cursor.fetchall()]

            if original_batch_ids:
                anonymization_report['tables_processed'].append('processing_batches')
                anonymization_report['items_anonymized']['batch_ids'] = len(original_batch_ids)

                if not dry_run:
                    for original_id in original_batch_ids:
                        # Generate anonymous batch ID
                        import hashlib
                        anonymous_id = f"batch_{hashlib.sha256(original_id.encode()).hexdigest()[:8]}"

                        # Update all references to this batch ID
                        tables_to_update = [
                            'linguistic_patterns', 'function_words', 'structural_patterns',
                            'vocabulary_metrics', 'style_markers', 'processing_batches'
                        ]

                        for table in tables_to_update:
                            try:
                                cursor.execute(f'''
                                    UPDATE {table}
                                    SET source_batch_id = ?
                                    WHERE source_batch_id = ?
                                ''', (anonymous_id, original_id))
                            except:
                                pass

        except Exception as e:
            print(f"⚠️  Batch anonymization failed: {e}")

        if not dry_run:
            conn.commit()
            self._log_audit_event('anonymize_data', anonymization_report)

        conn.close()

        return anonymization_report

    def update_privacy_settings(self, new_settings: Dict) -> Dict:
        """Update privacy settings"""
        old_settings = self.settings.copy()
        self.settings.update(new_settings)
        self._save_settings()

        self._log_audit_event('update_privacy_settings', {
            'changed_settings': [
                key for key in new_settings.keys()
                if old_settings.get(key) != new_settings[key]
            ]
        })

        return {
            'success': True,
            'old_settings': old_settings,
            'new_settings': self.settings
        }

    def get_privacy_status(self) -> Dict:
        """Get comprehensive privacy status"""
        stats = self.get_database_stats()
        cleanup_needed = self.cleanup_expired_data(dry_run=True)

        return {
            'settings': self.settings,
            'database_stats': stats,
            'cleanup_needed': cleanup_needed.get('items_to_remove', {}),
            'audit_log_exists': self.audit_log_path.exists(),
            'backup_exists': any('backup' in f.name for f in self.room_two_dir.glob('*.db')),
            'retention_status': {
                'days_until_cleanup': (
                    (datetime.now() - timedelta(days=self.settings['retention_days'])) -
                    datetime.fromisoformat(stats['oldest_data']) if stats.get('oldest_data') else timedelta(days=365)
                ).days
            }
        }

    def run_privacy_check(self) -> Dict:
        """Run comprehensive privacy check"""
        status = self.get_privacy_status()

        privacy_score = 100
        issues = []

        # Check settings
        if not status['settings']['auto_cleanup_enabled']:
            privacy_score -= 10
            issues.append("Auto cleanup disabled")

        if status['settings']['retention_days'] > 730:  # More than 2 years
            privacy_score -= 5
            issues.append("Long retention period")

        if not status['settings']['audit_enabled']:
            privacy_score -= 5
            issues.append("Audit logging disabled")

        # Check data
        if status['database_stats']['exists']:
            oldest_data = status['database_stats'].get('oldest_data')
            if oldest_data:
                data_age = (datetime.now() - datetime.fromisoformat(oldest_data)).days
                if data_age > status['settings']['retention_days']:
                    privacy_score -= 15
                    issues.append("Expired data not cleaned up")

        # Check for sensitive data patterns
        if status['database_stats'].get('file_size_mb', 0) > 100:  # Large database
            privacy_score -= 5
            issues.append("Large database size")

        return {
            'privacy_score': max(0, privacy_score),
            'issues': issues,
            'recommendations': self._generate_recommendations(issues),
            'status': status
        }

    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate privacy improvement recommendations"""
        recommendations = []

        if "Auto cleanup disabled" in issues:
            recommendations.append("Enable automatic data cleanup")

        if "Expired data not cleaned up" in issues:
            recommendations.append("Run cleanup to remove expired data")

        if "Long retention period" in issues:
            recommendations.append("Consider reducing data retention period")

        if "Audit logging disabled" in issues:
            recommendations.append("Enable audit logging for better tracking")

        if "Large database size" in issues:
            recommendations.append("Consider data minimization or cleanup")

        return recommendations

def main():
    """Privacy controls interface"""

    print("🔐 PRIVACY CONTROLS FOR ROOM TWO")
    print("=" * 40)

    controls = PrivacyControls()

    while True:
        print("\n📋 Privacy Status:")
        status = controls.get_privacy_status()
        stats = status['database_stats']

        if stats['exists']:
            print(f"  Database size: {stats['file_size_mb']:.1f} MB")
            print(f"  Total patterns: {stats['total_patterns']:,}")
            if stats['oldest_data']:
                print(f"  Oldest data: {stats['oldest_data'][:10]}")
        else:
            print("  No database found")

        print("\n🔧 Options:")
        print("1. View detailed statistics")
        print("2. Run privacy check")
        print("3. Clean up expired data")
        print("4. Export data")
        print("5. Update privacy settings")
        print("6. Delete all data")
        print("7. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            stats = controls.get_database_stats()
            print(json.dumps(stats, indent=2))

        elif choice == "2":
            check = controls.run_privacy_check()
            print(f"\n🔍 Privacy Score: {check['privacy_score']}/100")
            if check['issues']:
                print("\n⚠️  Issues:")
                for issue in check['issues']:
                    print(f"  • {issue}")
            if check['recommendations']:
                print("\n💡 Recommendations:")
                for rec in check['recommendations']:
                    print(f"  • {rec}")

        elif choice == "3":
            result = controls.cleanup_expired_data(dry_run=True)
            print("\n🧹 Cleanup Report:")
            print(json.dumps(result, indent=2))
            if result.get('items_to_remove', {}).get('batches', 0) > 0:
                confirm = input("Proceed with cleanup? (y/N): ").lower()
                if confirm == 'y':
                    controls.cleanup_expired_data(dry_run=False)

        elif choice == "4":
            result = controls.export_data()
            if result:
                print(f"✅ Data exported to: {result}")

        elif choice == "5":
            print("\nCurrent settings:")
            print(json.dumps(controls.settings, indent=2))
            print("\nEnter new settings (JSON format or 'skip'):")
            new_settings = input().strip()
            if new_settings != 'skip':
                try:
                    settings = json.loads(new_settings)
                    controls.update_privacy_settings(settings)
                    print("✅ Settings updated")
                except:
                    print("❌ Invalid JSON")

        elif choice == "6":
            confirm = input("Type 'DELETE_ALL_DATA' to confirm: ")
            if confirm == "DELETE_ALL_DATA":
                result = controls.delete_all_data(confirm=confirm)
                print("✅ All data deleted")
            else:
                print("❌ Deletion cancelled")

        elif choice == "7":
            break

if __name__ == "__main__":
    main()
