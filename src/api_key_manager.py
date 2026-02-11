"""
API Key 管理模組
提供 API Key 的安全儲存與讀取功能
"""
import os
import json
from pathlib import Path
import base64
import hashlib

# 嘗試導入 cryptography,如果失敗則使用簡單存儲
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    print("[WARNING] cryptography 未安裝,使用簡單 JSON 存儲 (不加密)")

class APIKeyManager:
    """API Key 管理器 - 提供加密儲存與讀取功能"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / ("api_keys.enc" if HAS_CRYPTOGRAPHY else "api_keys.json")
        self.salt_file = self.config_dir / ".salt"
        
    def _get_cipher(self):
        """生成加密器 (使用機器特定的密鑰)"""
        if not HAS_CRYPTOGRAPHY:
            return None
            
        # 使用機器特定資訊生成密鑰
        if not self.salt_file.exists():
            salt = os.urandom(32)
            self.salt_file.write_bytes(salt)
        else:
            salt = self.salt_file.read_bytes()
        
        # 使用 salt 生成密鑰
        key = base64.urlsafe_b64encode(hashlib.sha256(salt).digest())
        return Fernet(key)
    
    def save_api_key(self, service_name, api_key):
        """
        儲存 API Key
        
        Args:
            service_name: 服務名稱 (例如: 'google_gemini')
            api_key: API Key 字串
        """
        # 讀取現有的 keys
        keys = self.load_all_keys()
        
        # 更新或新增
        keys[service_name] = api_key
        
        # 加密並儲存 (如果有 cryptography) 或直接儲存
        if HAS_CRYPTOGRAPHY:
            cipher = self._get_cipher()
            encrypted_data = cipher.encrypt(json.dumps(keys).encode())
            self.key_file.write_bytes(encrypted_data)
        else:
            # 簡單 JSON 存儲 (不加密)
            with open(self.key_file, 'w', encoding='utf-8') as f:
                json.dump(keys, f, indent=2)
        
        return True
    
    def load_api_key(self, service_name):
        """
        讀取 API Key
        
        Args:
            service_name: 服務名稱
            
        Returns:
            str: API Key 或 None
        """
        keys = self.load_all_keys()
        return keys.get(service_name)
    
    def load_all_keys(self):
        """讀取所有 API Keys"""
        if not self.key_file.exists():
            return {}
        
        try:
            if HAS_CRYPTOGRAPHY:
                cipher = self._get_cipher()
                encrypted_data = self.key_file.read_bytes()
                decrypted_data = cipher.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
            else:
                # 簡單 JSON 讀取 (不加密)
                with open(self.key_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"讀取 API Keys 失敗: {e}")
            return {}
    
    def delete_api_key(self, service_name):
        """刪除指定的 API Key"""
        keys = self.load_all_keys()
        if service_name in keys:
            del keys[service_name]
            
            if HAS_CRYPTOGRAPHY:
                cipher = self._get_cipher()
                encrypted_data = cipher.encrypt(json.dumps(keys).encode())
                self.key_file.write_bytes(encrypted_data)
            else:
                # 簡單 JSON 存儲 (不加密)
                with open(self.key_file, 'w', encoding='utf-8') as f:
                    json.dump(keys, f, indent=2)
            return True
        return False
    
    def has_api_key(self, service_name):
        """檢查是否已設定 API Key"""
        return service_name in self.load_all_keys()

# 建立全域實例
api_key_manager = APIKeyManager()

if __name__ == "__main__":
    # 測試
    manager = APIKeyManager()
    
    # 儲存測試
    print("測試儲存 API Key...")
    manager.save_api_key("google_gemini", "test_key_12345")
    
    # 讀取測試
    print("測試讀取 API Key...")
    key = manager.load_api_key("google_gemini")
    print(f"讀取結果: {key}")
    
    # 檢查測試
    print(f"是否已設定: {manager.has_api_key('google_gemini')}")
    
    # 刪除測試
    print("測試刪除 API Key...")
    manager.delete_api_key("google_gemini")
    print(f"刪除後是否存在: {manager.has_api_key('google_gemini')}")
