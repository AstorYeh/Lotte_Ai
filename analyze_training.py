"""
學習曲線分析與視覺化
分析 305 期訓練的命中率變化、權重演化、模型表現
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端
from pathlib import Path
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def analyze_training_results(session_dir):
    """分析訓練結果"""
    session_path = Path(session_dir)
    summary_file = session_path / "training_summary.json"
    
    # 載入訓練總結
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    iterations = summary['iterations']
    stats = summary['statistics']
    
    print("=" * 60)
    print("訓練結果分析")
    print("=" * 60)
    print(f"總期數: {stats['total_periods']}")
    print(f"平均命中率: {stats['average_accuracy']:.2%}")
    print(f"最佳命中率: {stats['best_accuracy']:.2%}")
    print(f"最差命中率: {stats['worst_accuracy']:.2%}")
    print(f"總命中數: {stats['total_hits']}")
    print()
    
    # 轉換為 DataFrame
    df = pd.DataFrame(iterations)
    
    # 1. 命中率分布
    print("命中率分布:")
    accuracy_counts = df['accuracy'].value_counts().sort_index(ascending=False)
    for acc, count in accuracy_counts.items():
        print(f"  {acc:.0%} (命中 {int(acc*5)}/5): {count} 期 ({count/len(df):.1%})")
    print()
    
    # 2. 移動平均
    df['ma_10'] = df['accuracy'].rolling(window=10).mean()
    df['ma_30'] = df['accuracy'].rolling(window=30).mean()
    
    # 3. 視覺化
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('2025 年訓練學習曲線分析', fontsize=16, fontweight='bold')
    
    # 3.1 命中率時間序列
    ax1 = axes[0, 0]
    ax1.plot(df['period'], df['accuracy'], alpha=0.3, label='實際命中率')
    ax1.plot(df['period'], df['ma_10'], label='10期移動平均', linewidth=2)
    ax1.plot(df['period'], df['ma_30'], label='30期移動平均', linewidth=2)
    ax1.axhline(y=stats['average_accuracy'], color='r', linestyle='--', label=f'平均 {stats["average_accuracy"]:.1%}')
    ax1.axhline(y=0.128, color='g', linestyle='--', label='隨機期望 12.8%')
    ax1.set_xlabel('期數')
    ax1.set_ylabel('命中率')
    ax1.set_title('命中率變化趨勢')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 3.2 命中率分布直方圖
    ax2 = axes[0, 1]
    ax2.hist(df['accuracy'], bins=6, edgecolor='black', alpha=0.7)
    ax2.axvline(x=stats['average_accuracy'], color='r', linestyle='--', linewidth=2, label=f'平均 {stats["average_accuracy"]:.1%}')
    ax2.set_xlabel('命中率')
    ax2.set_ylabel('期數')
    ax2.set_title('命中率分布')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3.3 累積命中數
    ax3 = axes[1, 0]
    df['cumulative_hits'] = df['hits'].cumsum()
    ax3.plot(df['period'], df['cumulative_hits'], linewidth=2)
    ax3.set_xlabel('期數')
    ax3.set_ylabel('累積命中數')
    ax3.set_title(f'累積命中數 (總計: {stats["total_hits"]} 顆)')
    ax3.grid(True, alpha=0.3)
    
    # 3.4 命中數分布
    ax4 = axes[1, 1]
    hits_counts = df['hits'].value_counts().sort_index()
    ax4.bar(hits_counts.index, hits_counts.values, edgecolor='black', alpha=0.7)
    ax4.set_xlabel('單期命中數')
    ax4.set_ylabel('期數')
    ax4.set_title('單期命中數分布')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 3.5 學習階段分析 (分成 5 個階段)
    ax5 = axes[2, 0]
    stage_size = len(df) // 5
    stages = []
    for i in range(5):
        start = i * stage_size
        end = (i + 1) * stage_size if i < 4 else len(df)
        stage_acc = df.iloc[start:end]['accuracy'].mean()
        stages.append(stage_acc)
    
    ax5.bar(range(1, 6), stages, edgecolor='black', alpha=0.7)
    ax5.axhline(y=stats['average_accuracy'], color='r', linestyle='--', label='總平均')
    ax5.set_xlabel('訓練階段')
    ax5.set_ylabel('平均命中率')
    ax5.set_title('各階段平均命中率')
    ax5.set_xticks(range(1, 6))
    ax5.set_xticklabels([f'階段{i}' for i in range(1, 6)])
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 3.6 命中率改善趨勢
    ax6 = axes[2, 1]
    # 計算每 20 期的平均命中率
    window = 20
    rolling_avg = df['accuracy'].rolling(window=window).mean()
    ax6.plot(df['period'], rolling_avg, linewidth=2, label=f'{window}期移動平均')
    
    # 線性趨勢
    z = np.polyfit(df['period'], df['accuracy'], 1)
    p = np.poly1d(z)
    ax6.plot(df['period'], p(df['period']), "r--", alpha=0.8, label=f'趨勢線 (斜率: {z[0]:.6f})')
    
    ax6.set_xlabel('期數')
    ax6.set_ylabel('命中率')
    ax6.set_title('學習改善趨勢')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 儲存圖表
    output_file = session_path / "learning_curves.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[OK] 學習曲線已儲存: {output_file}")
    
    return df, stats

def analyze_group_performance(session_dir):
    """分析各群組表現"""
    session_path = Path(session_dir)
    
    # 載入所有期數記錄
    group_stats = {
        'group1': {'hits': [], 'total': []},
        'group2': {'hits': [], 'total': []},
        'group3': {'hits': [], 'total': []},
        'group4': {'hits': [], 'total': []}
    }
    
    period_files = sorted(session_path.glob("period_*.json"))
    
    for period_file in period_files:
        with open(period_file, 'r', encoding='utf-8') as f:
            period_data = json.load(f)
        
        group_hits = period_data.get('verification', {}).get('group_hits', {})
        
        for group_id, hit_info in group_hits.items():
            if group_id in group_stats:
                group_stats[group_id]['hits'].append(hit_info.get('hits', 0))
                group_stats[group_id]['total'].append(hit_info.get('total', 0))
    
    # 計算各群組統計
    print("=" * 60)
    print("各群組表現分析")
    print("=" * 60)
    
    for group_id in ['group1', 'group2', 'group3', 'group4']:
        hits = group_stats[group_id]['hits']
        total = group_stats[group_id]['total']
        
        total_hits = sum(hits)
        total_predicted = sum(total)
        avg_accuracy = total_hits / total_predicted if total_predicted > 0 else 0
        
        print(f"{group_id} (號碼範圍):")
        print(f"  總預測數: {total_predicted}")
        print(f"  總命中數: {total_hits}")
        print(f"  命中率: {avg_accuracy:.2%}")
        print()

if __name__ == "__main__":
    # 找到最新的訓練 session
    iterations_dir = Path("logs/iterations")
    sessions = sorted(iterations_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if sessions:
        latest_session = sessions[0]
        print(f"分析最新訓練 session: {latest_session.name}\n")
        
        # 分析學習曲線
        df, stats = analyze_training_results(latest_session)
        
        # 分析群組表現
        analyze_group_performance(latest_session)
        
        print("\n分析完成!")
    else:
        print("找不到訓練記錄")
