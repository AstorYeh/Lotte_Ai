# -*- coding: utf-8 -*-
"""
Analyze Training Results with Profit Evaluator
Analyze the latest training session to get baseline profit rate
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.profit_evaluator import ProfitEvaluator


def analyze_training_session(session_id):
    """Analyze a specific training session"""
    
    log_dir = Path(f"logs/iterations/{session_id}")
    
    if not log_dir.exists():
        print(f"[ERROR] Session not found: {session_id}")
        return None
    
    print(f"\n{'='*60}")
    print(f"Analyzing Training Session: {session_id}")
    print(f"{'='*60}\n")
    
    # Load training summary
    summary_file = log_dir / "training_summary.json"
    
    if not summary_file.exists():
        print(f"[ERROR] training_summary.json not found")
        return None
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create profit evaluator
    evaluator = ProfitEvaluator()
    
    # Process each iteration
    for iteration in data['iterations']:
        period = iteration['period']
        hits = iteration['hits']
        
        # We don't have predicted/actual numbers in summary, use placeholders
        predicted = []
        actual = []
        
        evaluator.add_result(period, predicted, actual, hits)
    
    # Display summary
    evaluator.print_summary()
    
    # Save profit analysis
    output_file = log_dir / "profit_analysis.json"
    evaluator.save_to_file(output_file)
    
    return evaluator


def find_latest_session():
    """Find the latest training session"""
    logs_dir = Path("logs/iterations")
    
    if not logs_dir.exists():
        print("[ERROR] logs/iterations directory not found")
        return None
    
    # Get all session directories
    sessions = [d for d in logs_dir.iterdir() if d.is_dir()]
    
    if not sessions:
        print("[ERROR] No training sessions found")
        return None
    
    # Sort by name (timestamp)
    sessions.sort(reverse=True)
    
    return sessions[0].name


if __name__ == "__main__":
    print("="*60)
    print("PROFIT RATE ANALYSIS - Training Results")
    print("="*60)
    
    # Find latest session
    latest_session = find_latest_session()
    
    if latest_session:
        print(f"\nLatest session: {latest_session}")
        
        # Analyze it
        evaluator = analyze_training_session(latest_session)
        
        if evaluator:
            print("\n[OK] Analysis completed!")
            print(f"\nKey Metrics:")
            summary = evaluator.get_summary()
            print(f"  - Profit Rate (3+ hits): {summary['profit_rate']*100:.2f}%")
            print(f"  - Loss Rate (0-1 hits): {summary['loss_rate']*100:.2f}%")
            print(f"  - Total Score: {summary['total_score']:+d}")
    else:
        print("\n[ERROR] No training sessions found")
        print("\nAvailable sessions:")
        logs_dir = Path("logs/iterations")
        if logs_dir.exists():
            for session in sorted(logs_dir.iterdir(), reverse=True)[:10]:
                print(f"  - {session.name}")
