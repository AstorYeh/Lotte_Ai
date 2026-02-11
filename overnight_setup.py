"""
夜間執行腳本
1. 確保 XGBoost 安裝完成
2. 測試所有新模型
3. 記錄測試結果
"""
import subprocess
import sys
import time
from pathlib import Path

def install_xgboost():
    """安裝 XGBoost"""
    print("=" * 60)
    print("安裝 XGBoost...")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "xgboost"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 分鐘超時
        )
        
        if result.returncode == 0:
            print("[OK] XGBoost 安裝成功")
            return True
        else:
            print(f"[ERROR] 安裝失敗: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[WARNING] 安裝超時,但可能已完成")
        return False
    except Exception as e:
        print(f"[ERROR] 安裝過程發生錯誤: {e}")
        return False

def test_enhanced_models():
    """測試增強模型"""
    print("\n" + "=" * 60)
    print("測試增強模型...")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.enhanced_models"],
            capture_output=True,
            text=True,
            timeout=300  # 5 分鐘超時
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("[OK] 增強模型測試成功")
            return True
        else:
            print(f"[ERROR] 測試失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] 測試過程發生錯誤: {e}")
        return False

def save_results(results):
    """儲存測試結果"""
    output_file = Path("logs/overnight_test_results.txt")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("夜間測試結果\n")
        f.write("=" * 60 + "\n\n")
        
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    
    print(f"\n[OK] 測試結果已儲存: {output_file}")

def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("夜間執行腳本啟動")
    print("=" * 60)
    print(f"開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        "開始時間": time.strftime('%Y-%m-%d %H:%M:%S'),
        "XGBoost 安裝": "失敗",
        "模型測試": "未執行",
        "結束時間": ""
    }
    
    # 1. 安裝 XGBoost
    if install_xgboost():
        results["XGBoost 安裝"] = "成功"
        
        # 2. 測試模型
        if test_enhanced_models():
            results["模型測試"] = "成功"
        else:
            results["模型測試"] = "失敗"
    else:
        print("\n[WARNING] XGBoost 安裝未完成,跳過模型測試")
    
    results["結束時間"] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 3. 儲存結果
    save_results(results)
    
    print("\n" + "=" * 60)
    print("夜間執行完成")
    print("=" * 60)
    print(f"結束時間: {results['結束時間']}")
    
    # 顯示摘要
    print("\n摘要:")
    for key, value in results.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
