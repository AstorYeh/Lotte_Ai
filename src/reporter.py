import google.generativeai as genai
import os
import pandas as pd
from src.api_key_manager import api_key_manager

class GeminiReporter:
    def __init__(self):
        # 優先從 API Key Manager 讀取
        api_key = api_key_manager.load_api_key("google_gemini")
        
        # 如果沒有,嘗試從環境變數讀取
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. AI reporting will be disabled.")
            return
        
        # 設定環境變數 (供 SDK 使用)
        os.environ["GOOGLE_API_KEY"] = api_key
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')  # Gemini 2.5 Pro
        except Exception as e:
            self.model = None
            print(f"Error initializing Gemini: {e}")

    def generate_report(self, candidates, scores_df):
        if not self.model:
            return "AI Report unavailable (Missing API Key)."

        # Prepare data for prompt
        # Filter scores for candidate numbers only
        subset = scores_df.loc[candidates].copy()
        
        # Format the data string
        data_summary = ""
        for num in candidates:
            row = subset.loc[num]
            data_summary += (
                f"號碼 {num:02d}: "
                f"熱度(Freq)={row.get('freq',0):.2f}, "
                f"趨勢(Slope)={row.get('slope',0):.2f}, "
                f"動能(RSI)={row.get('rsi',0):.2f}, "
                f"機率(SVM)={row.get('svm',0):.2f}\n"
            )

        prompt = f"""
你是一位精通統計數據與趨勢分析的「539 樂透分析大師」。
請根據以下演算法模型計算出的數據，為使用者撰寫一份專業且充滿洞見的分析報告。
請使用繁體中文，語氣專業、自信且帶有鼓勵性。

## 本期推薦號碼
{candidates}

## 號碼數據指標
{data_summary}

## 報告要求
1. **整體盤勢解讀**：簡述本期號碼的分佈策略（例如偏重熱門號還是冷門補漲）。
2. **焦點號碼分析**：挑選 2-3 個數據表現最強的號碼進行重點點評，解釋為何模型看好它（引用具體指標，如 RSI 動能強、頻率高等）。
3. **投資建議**：給予簡單的投注建議組合（例如 234 星建議）。
4. **結語**：一句簡短的幸運祝福。

請直接輸出報告內容，不要有其他 Markdown 格式以外的贅字。
"""
        print("Sending request to Gemini...")
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating report: {e}"

if __name__ == "__main__":
    # Test stub
    rep = GeminiReporter()
    cands = [5, 12, 23, 33, 38]
    # Mock scores
    df_mock = pd.DataFrame(index=cands)
    df_mock['freq'] = [0.8, 0.5, 0.9, 0.2, 0.6]
    df_mock['slope'] = [0.1, -0.05, 0.2, 0.0, 0.1]
    df_mock['rsi'] = [0.9, 0.4, 0.85, 0.3, 0.7]
    df_mock['svm'] = [0.7, 0.3, 0.8, 0.4, 0.6]
    
    print(rep.generate_report(cands, df_mock))
