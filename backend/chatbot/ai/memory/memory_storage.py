import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class MemoryStorage:
    """Persistent storage for conversation memory"""
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent / 'storage'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.storage_dir / 'conversation_memory.json'
    
    def _serialize_schemes(self, schemes):
        """Convert schemes to serializable format"""
        if not schemes:
            return []
        
        serialized = []
        for scheme in schemes:
            if scheme is None:
                continue
            if isinstance(scheme, dict):
                serialized.append(scheme)
            else:
                # Convert Scheme object to dict
                try:
                    serialized.append({
                        'scheme_name': getattr(scheme, 'scheme_name', 'Unknown'),
                        'details': getattr(scheme, 'details', ''),
                        'benefits': getattr(scheme, 'benefits', ''),
                        'eligibility': getattr(scheme, 'eligibility', ''),
                        'application': getattr(scheme, 'application', ''),
                        'documents': getattr(scheme, 'documents', ''),
                        'schemeCategory': getattr(scheme, 'schemeCategory', ''),
                        'level': getattr(scheme, 'level', ''),
                        'id': str(getattr(scheme, 'id', ''))
                    })
                except Exception as e:
                    print(f"⚠️ Could not serialize scheme: {e}")
                    serialized.append({'scheme_name': 'Unknown'})
        
        return serialized
    
    def _deserialize_schemes(self, schemes_data):
        """Convert serialized schemes back to dict format"""
        return schemes_data if schemes_data else []
    
    def save_memory(self, session_id: str, memory_data: Dict):
        """Save memory data to file"""
        try:
            # Load existing data
            all_data = self.load_all_memories()
            
            # Serialize schemes in memory data
            if 'context' in memory_data and 'last_schemes' in memory_data['context']:
                memory_data['context']['last_schemes'] = self._serialize_schemes(
                    memory_data['context']['last_schemes']
                )
            
            # Also serialize last_referenced_scheme if present
            if 'context' in memory_data and 'last_referenced_scheme' in memory_data['context']:
                ref_scheme = memory_data['context']['last_referenced_scheme']
                if ref_scheme and ref_scheme.get('data'):
                    ref_scheme['data'] = self._serialize_schemes([ref_scheme['data']])[0] if ref_scheme['data'] else None
            
            # Update with new data
            all_data[session_id] = {
                'memory': memory_data,
                'last_updated': datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_memory(self, session_id: str) -> Optional[Dict]:
        """Load memory data from file"""
        try:
            all_data = self.load_all_memories()
            if session_id in all_data:
                memory_data = all_data[session_id].get('memory')
                # Deserialize schemes
                if memory_data and 'context' in memory_data and 'last_schemes' in memory_data['context']:
                    memory_data['context']['last_schemes'] = self._deserialize_schemes(
                        memory_data['context']['last_schemes']
                    )
                return memory_data
            return None
        except Exception as e:
            print(f"Error loading memory: {e}")
            return None
    
    def load_all_memories(self) -> Dict:
        """Load all memory data"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Backup corrupted file
            if self.memory_file.exists():
                backup = self.memory_file.with_suffix('.json.bak')
                import shutil
                shutil.copy(self.memory_file, backup)
                print(f"📁 Corrupted file backed up to: {backup}")
                # Reset the file
                self.memory_file.unlink()
            return {}
        except Exception as e:
            print(f"Error loading all memories: {e}")
            return {}
    
    def delete_memory(self, session_id: str):
        """Delete memory for a session"""
        try:
            all_data = self.load_all_memories()
            if session_id in all_data:
                del all_data[session_id]
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def get_all_session_ids(self) -> List[str]:
        """Get all session IDs with stored memory"""
        all_data = self.load_all_memories()
        return list(all_data.keys())
    
    def clear_all(self):
        """Clear all stored memories"""
        try:
            if self.memory_file.exists():
                self.memory_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False


# Singleton instance
_storage = None

def get_memory_storage():
    global _storage
    if _storage is None:
        _storage = MemoryStorage()
    return _storage