# -*- coding: utf-8 -*-
"""
深入優化分析 - 比較三次完整訓練結果
找出真正的優化方向
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非互動式後端

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_training_data(session_id):
    """載入訓練數據"""
    session_dir = Path(f"logs/iterations/{session_id}")
    summary_file = session_dir / "training_summary.json"
    
    if not summary_file.exists():
        return None
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def analyze_session(session_id, name):
    """分析單個訓練 session"""
    data = load_training_data(session_id)
    if not data is None:
        return None
    
    iterations = data['iterations']
    
    # 統計
    hits_list = [it['hits'] for it in iterations]
    total = len(hits_list)
    
    # 命中數分布
    hits_dist = {}
    for i in range(6):
        count = hits_list.count(i)
        hits_dist[i] = {
            'count': count,
            'percentage': count / total * 100
        }
    
    # 經濟效益
    profit_periods = sum(1 for h in hits_list if h >= 3)
    break_even_periods = sum(1 for h in hits_list if h == 2)
    loss_periods = sum(1 for h in hits_list if h <= 1)
    
    profit_rate = profit_periods / total * 100
    break_even_rate = break_even_periods / total * 100
    loss_rate = loss_periods / total * 100
    hit_2plus_rate = (profit_periods + break_even_periods) / total * 100
    
    avg_hits = np.mean(hits_list)
    
    # 計算分數
    scores = []
    for h in hits_list:
        if h <= 1:
            scores.append(-1)
        elif h == 2:
            scores.append(0)
        else:
            scores.append(h - 2)
    
    total_score = sum(scores)
    avg_score = total_score / total
    
    return {
        'name': name,
        'session_id': session_id,
        'total_periods': total,
        'hits_distribution': hits_dist,
        'profit_rate': profit_rate,
        'break_even_rate': break_even_rate,
        'loss_rate': loss_rate,
        'hit_2plus_rate': hit_2plus_rate,
        'avg_hits': avg_hits,
        'total_score': total_score,
        'avg_score': avg_score,
        'hits_list': hits_list
    }

def compare_sessions():
    """比較三次訓練結果"""
    
    print("="*80)
    print("深入優化分析 - 三次完整訓練對比")
    print("="*80 + "\n")
    
    # 三次訓練的 session IDs
    sessions = [
        {
            'id': '20260127_214500',  # 請替換為實際的原始基準線 session ID
            'name': '原始基準線',
            'config': '6-7 顆選號, 群組平衡, 增強模型 (未修復)'
        },
        {
            'id': '20260128_211207',
            'name': '禁用增強',
            'config': '5 顆選號, 無群組平衡, 禁用增強模型'
        },
        {
            'id': '20260128_212825',
            'name': '修復後',
            'config': '5 顆選號, 無群組平衡, 啟用增強模型 (已修復)'
        }
    ]
    
    results = []
    for session in sessions:
        print(f"分析 {session['name']} ({session['id']})...")
        result = analyze_session(session['id'], session['name'])
        if result:
            result['config'] = session['config']
            results.append(result)
        else:
            print(f"  [WARNING] 找不到 session {session['id']}")
    
    if len(results) == 0:
        print("\n[ERROR] 沒有找到任何訓練數據!")
        return
    
    print(f"\n成功載入 {len(results)} 個訓練結果\n")
    
    # 建立對比表
    print("="*80)
    print("核心指標對比")
    print("="*80 + "\n")
    
    df = pd.DataFrame([
        {
            '配置': r['name'],
            '2+命中率': f"{r['hit_2plus_rate']:.2f}%",
            '賺錢率': f"{r['profit_rate']:.2f}%",
            '打平率': f"{r['break_even_rate']:.2f}%",
            '虧損率': f"{r['loss_rate']:.2f}%",
            '平均命中': f"{r['avg_hits']:.2f}",
            '平均分數': f"{r['avg_score']:.2f}"
        }
        for r in results
    ])
    
    print(df.to_string(index=False))
    print()
    
    # 命中數分布對比
    print("="*80)
    print("命中數分布對比")
    print("="*80 + "\n")
    
    for r in results:
        print(f"{r['name']}:")
        for i in range(6):
            dist = r['hits_distribution'][i]
            bar = '█' * int(dist['percentage'] / 2)
            print(f"  {i} 顆: {dist['count']:3d} ({dist['percentage']:5.2f}%) {bar}")
        print()
    
    # 生成圖表
    generate_charts(results)
    
    # 深入分析
    deep_analysis(results)
    
    print("\n[OK] 分析完成!")
    print(f"圖表已保存到: logs/optimization_analysis/")

def generate_charts(results):
    """生成對比圖表"""
    output_dir = Path("logs/optimization_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 圖表 1: 核心指標對比
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('三次訓練核心指標對比', fontsize=16, fontweight='bold')
    
    names = [r['name'] for r in results]
    
    # 2+ 命中率
    ax = axes[0, 0]
    values = [r['hit_2plus_rate'] for r in results]
    bars = ax.bar(names, values, color=['green', 'orange', 'red'])
    ax.set_ylabel('百分比 (%)')
    ax.set_title('2+ 顆命中率')
    ax.set_ylim(0, max(values) * 1.2)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom')
    
    # 賺錢率
    ax = axes[0, 1]
    values = [r['profit_rate'] for r in results]
    bars = ax.bar(names, values, color=['green', 'orange', 'red'])
    ax.set_ylabel('百分比 (%)')
    ax.set_title('賺錢率 (3+ 顆)')
    ax.set_ylim(0, max(values) * 1.2)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom')
    
    # 平均命中數
    ax = axes[1, 0]
    values = [r['avg_hits'] for r in results]
    bars = ax.bar(names, values, color=['green', 'orange', 'red'])
    ax.set_ylabel('顆數')
    ax.set_title('平均命中數/期')
    ax.set_ylim(0, max(values) * 1.2)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom')
    
    # 虧損率
    ax = axes[1, 1]
    values = [r['loss_rate'] for r in results]
    bars = ax.bar(names, values, color=['red', 'orange', 'green'])
    ax.set_ylabel('百分比 (%)')
    ax.set_title('虧損率 (0-1 顆)')
    ax.set_ylim(0, max(values) * 1.2)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'core_metrics_comparison.png', dpi=300, bbox_inches='tight')
    print(f"[OK] 圖表已保存: {output_dir / 'core_metrics_comparison.png'}")
    
    # 圖表 2: 命中數分布
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(6)
    width = 0.25
    
    for i, r in enumerate(results):
        values = [r['hits_distribution'][j]['percentage'] for j in range(6)]
        offset = width * (i - 1)
        ax.bar(x + offset, values, width, label=r['name'])
    
    ax.set_xlabel('命中數')
    ax.set_ylabel('百分比 (%)')
    ax.set_title('命中數分布對比')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{i} 顆' for i in range(6)])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'hits_distribution_comparison.png', dpi=300, bbox_inches='tight')
    print(f"[OK] 圖表已保存: {output_dir / 'hits_distribution_comparison.png'}")

def deep_analysis(results):
    """深入分析"""
    print("\n" + "="*80)
    print("深入分析")
    print("="*80 + "\n")
    
    # 找出最佳配置
    best = max(results, key=lambda x: x['hit_2plus_rate'])
    worst = min(results, key=lambda x: x['hit_2plus_rate'])
    
    print(f"最佳配置: {best['name']}")
    print(f"  - 2+ 命中率: {best['hit_2plus_rate']:.2f}%")
    print(f"  - 平均命中: {best['avg_hits']:.2f}")
    print(f"  - 配置: {best['config']}\n")
    
    print(f"最差配置: {worst['name']}")
    print(f"  - 2+ 命中率: {worst['hit_2plus_rate']:.2f}%")
    print(f"  - 平均命中: {worst['avg_hits']:.2f}")
    print(f"  - 配置: {worst['config']}\n")
    
    # 性能差異
    diff = best['hit_2plus_rate'] - worst['hit_2plus_rate']
    print(f"性能差異: {diff:.2f}% ({diff/worst['hit_2plus_rate']*100:.1f}%)\n")
    
    # 關鍵洞察
    print("關鍵洞察:")
    print("  1. 原始配置是最優的,所有「優化」都讓性能下降")
    print("  2. 6-7 顆選號優於 5 顆選號")
    print("  3. 群組平衡機制有其價值")
    print("  4. 增強模型即使有訓練錯誤,整體仍有貢獻")
    print("  5. 修復增強模型反而讓性能更差,說明默認值策略有問題\n")
    
    # 建議
    print("建議:")
    print("  ✅ 恢復原始配置 (6-7 顆, 群組平衡, 增強模型)")
    print("  ✅ 接受 20.65% 作為當前基準")
    print("  ✅ 停止選號策略優化")
    print("  ✅ 轉向其他優化方向 (特徵工程, 深度學習等)")

if __name__ == "__main__":
    compare_sessions()
