#!/usr/bin/env python3
"""
Data Source Reference Management System
Manages references to original data sources without storing actual content
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class DataSourceManager:
    """
    Manages references to original data sources while keeping Room Two clean
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.room_two_dir = self.base_dir / "room_two_database"
        self.sources_file = self.room_two_dir / "data_sources.json"
        self.index_file = self.room_two_dir / "source_index.json"

        # Load existing data
        self.sources = self._load_sources()
        self.index = self._load_index()

    def _load_sources(self) -> Dict:
        """Load data source references"""
        if self.sources_file.exists():
            with open(self.sources_file, 'r') as f:
                return json.load(f)
        return {}

    def _load_index(self) -> Dict:
        """Load source index for quick lookup"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {
            'by_batch_id': {},
            'by_path': {},
            'by_checksum': {},
            'by_date': {}
        }

    def _save_sources(self):
        """Save data source references"""
        with open(self.sources_file, 'w') as f:
            json.dump(self.sources, f, indent=2)

    def _save_index(self):
        """Save source index"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except:
            return "unreadable_file"

    def register_source(self, source_path: str, batch_id: str, metadata: Dict = None) -> str:
        """
        Register a data source reference without storing content
        Returns source_id
        """

        source_path = Path(source_path)
        if not source_path.exists():
            raise ValueError(f"Source not found: {source_path}")

        source_id = f"src_{hashlib.sha256(str(source_path).encode()).hexdigest()[:16]}"

        # Calculate checksum for integrity verification
        checksum = self._calculate_checksum(str(source_path))

        # Create source reference
        source_ref = {
            'source_id': source_id,
            'batch_id': batch_id,
            'original_path': str(source_path),
            'file_name': source_path.name,
            'file_size': source_path.stat().st_size if source_path.exists() else 0,
            'last_modified': source_path.stat().st_mtime if source_path.exists() else 0,
            'checksum': checksum,
            'file_type': source_path.suffix.lower(),
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata or {},
            'access_count': 0,
            'last_accessed': None
        }

        # Store source reference
        self.sources[source_id] = source_ref

        # Update index
        self._update_index(source_id, source_ref)

        print(f"📋 Registered source: {source_path.name} -> {source_id}")
        return source_id

    def _update_index(self, source_id: str, source_ref: Dict):
        """Update search indexes"""

        # By batch_id
        batch_id = source_ref['batch_id']
        if batch_id not in self.index['by_batch_id']:
            self.index['by_batch_id'][batch_id] = []
        if source_id not in self.index['by_batch_id'][batch_id]:
            self.index['by_batch_id'][batch_id].append(source_id)

        # By path
        path = source_ref['original_path']
        if path not in self.index['by_path']:
            self.index['by_path'][path] = source_id

        # By checksum
        checksum = source_ref['checksum']
        if checksum not in self.index['by_checksum']:
            self.index['by_checksum'][checksum] = []
        self.index['by_checksum'][checksum].append(source_id)

        # By date
        date_key = source_ref['registered_at'][:10]  # YYYY-MM-DD
        if date_key not in self.index['by_date']:
            self.index['by_date'][date_key] = []
        self.index['by_date'][date_key].append(source_id)

        self._save_index()

    def get_source(self, source_id: str) -> Optional[Dict]:
        """Get source reference by ID"""
        if source_id in self.sources:
            # Update access count
            self.sources[source_id]['access_count'] += 1
            self.sources[source_id]['last_accessed'] = datetime.now().isoformat()
            self._save_sources()
            return self.sources[source_id]
        return None

    def get_sources_by_batch(self, batch_id: str) -> List[Dict]:
        """Get all sources for a specific batch"""
        if batch_id in self.index['by_batch_id']:
            source_ids = self.index['by_batch_id'][batch_id]
            return [self.sources[sid] for sid in source_ids if sid in self.sources]
        return []

    def verify_source_integrity(self, source_id: str) -> bool:
        """Verify if original source still exists and is unchanged"""
        source = self.get_source(source_id)
        if not source:
            return False

        original_path = Path(source['original_path'])
        if not original_path.exists():
            return False

        current_checksum = self._calculate_checksum(str(original_path))
        return current_checksum == source['checksum']

    def find_duplicate_sources(self) -> List[List[str]]:
        """Find sources with identical content (by checksum)"""
        duplicates = []
        processed_checksums = set()

        for checksum, source_ids in self.index['by_checksum'].items():
            if len(source_ids) > 1 and checksum not in processed_checksums:
                duplicates.append(source_ids)
                processed_checksums.add(checksum)

        return duplicates

    def cleanup_missing_sources(self, dry_run: bool = True) -> List[str]:
        """Clean up references to missing sources"""
        missing_sources = []

        for source_id, source_ref in self.sources.items():
            if not self.verify_source_integrity(source_id):
                missing_sources.append(source_id)

        if not dry_run and missing_sources:
            print(f"🧹 Removing {len(missing_sources)} missing source references")
            for source_id in missing_sources:
                self.remove_source(source_id)

        return missing_sources

    def remove_source(self, source_id: str):
        """Remove a source reference"""
        if source_id not in self.sources:
            return

        source_ref = self.sources[source_id]

        # Remove from indexes
        batch_id = source_ref['batch_id']
        if batch_id in self.index['by_batch_id'] and source_id in self.index['by_batch_id'][batch_id]:
            self.index['by_batch_id'][batch_id].remove(source_id)

        path = source_ref['original_path']
        if path in self.index['by_path']:
            del self.index['by_path'][path]

        checksum = source_ref['checksum']
        if checksum in self.index['by_checksum'] and source_id in self.index['by_checksum'][checksum]:
            self.index['by_checksum'][checksum].remove(source_id)

        registered_date = source_ref['registered_at'][:10]
        if registered_date in self.index['by_date'] and source_id in self.index['by_date'][registered_date]:
            self.index['by_date'][registered_date].remove(source_id)

        # Remove from main storage
        del self.sources[source_id]

        # Save changes
        self._save_sources()
        self._save_index()

        print(f"🗑️  Removed source reference: {source_id}")

    def get_statistics(self) -> Dict:
        """Get data source statistics"""
        stats = {
            'total_sources': len(self.sources),
            'total_batches': len(self.index['by_batch_id']),
            'unique_paths': len(self.index['by_path']),
            'unique_checksums': len(self.index['by_checksum']),
            'date_range': {},
            'file_types': {},
            'batch_sizes': {},
            'integrity_status': {}
        }

        # Calculate file type distribution
        for source_ref in self.sources.values():
            file_type = source_ref['file_type']
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1

        # Calculate batch sizes
        for batch_id, source_ids in self.index['by_batch_id'].items():
            stats['batch_sizes'][batch_id] = len(source_ids)

        # Check integrity status
        verified_count = 0
        missing_count = 0
        for source_id in self.sources:
            if self.verify_source_integrity(source_id):
                verified_count += 1
            else:
                missing_count += 1

        stats['integrity_status'] = {
            'verified': verified_count,
            'missing': missing_count,
            'verification_rate': verified_count / len(self.sources) if self.sources else 0
        }

        # Date range
        dates = list(self.index['by_date'].keys())
        if dates:
            stats['date_range'] = {
                'earliest': min(dates),
                'latest': max(dates),
                'total_days': len(dates)
            }

        return stats

    def export_source_report(self, output_path: str = None):
        """Export comprehensive source report"""
        if not output_path:
            output_path = self.room_two_dir / "source_report.json"

        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'sources': self.sources,
            'duplicates': self.find_duplicate_sources(),
            'missing_sources': self.cleanup_missing_sources(dry_run=True)
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Source report exported to: {output_path}")
        return output_path

    def search_sources(self, query: str, search_type: str = "filename") -> List[Dict]:
        """Search sources by various criteria"""
        results = []

        query = query.lower()

        for source_ref in self.sources.values():
            match = False

            if search_type == "filename":
                match = query in source_ref['file_name'].lower()
            elif search_type == "path":
                match = query in source_ref['original_path'].lower()
            elif search_type == "batch":
                match = query in source_ref['batch_id'].lower()
            elif search_type == "filetype":
                match = query == source_ref['file_type'].lower()

            if match:
                results.append(source_ref)

        return results

def main():
    """Test data source manager"""

    print("📋 DATA SOURCE REFERENCE MANAGER")
    print("=" * 40)

    manager = DataSourceManager()

    # Demo operations
    print("📊 Current Statistics:")
    stats = manager.get_statistics()
    print(f"  Total sources: {stats['total_sources']}")
    print(f"  Total batches: {stats['total_batches']}")
    print(f"  Integrity rate: {stats['integrity_status']['verification_rate']:.1%}")

    if stats['missing_sources']:
        print(f"  ⚠️  Missing sources: {len(stats['missing_sources'])}")

    # Search demo
    search_query = input("\n🔍 Search sources (filename, press Enter to skip): ").strip()
    if search_query:
        results = manager.search_sources(search_query)
        print(f"Found {len(results)} matching sources:")
        for result in results[:5]:  # Show first 5
            print(f"  • {result['file_name']} ({result['batch_id']})")

    # Export report
    report_path = manager.export_source_report()
    print(f"\n📄 Full report: {report_path}")

if __name__ == "__main__":
    main()
