import pandas as pd
import numpy as np
import json
import os

class StrategyEngine:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.weights = self.config.get('weights', {
            'hot': 1.0, 'stability': 1.0, 'cold': 1.0, 'random': 0.1
        })
        self.ranges = self.config.get('partition_ranges', [[1, 10], [11, 20], [21, 30], [31, 39]])

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_config(self):
        self.config['weights'] = self.weights
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def calculate_total_score(self, scores_df):
        print("Calculating weighted total scores...")
        w = self.weights
        
        # Formula mapping:
        # Hot: freq, rsi, svm
        # Stability: slope, markov, knn (knn is similarity/stability)
        # Cold: pca (variance) - specifically looking for low variance (stable) or high variance?
        # User spec: "Cold: Weighted PCA (catch up/rebound)". Actually PCA in my impl is stability.
        # Let's map loosely based on user spec:
        # Hot: freq, svm, rsi
        # Stability: slope, markov
        # Cold: pca
        # Random: random noise + knn
        
        # We need to ensure all columns exist
        for col in ['freq', 'rsi', 'slope', 'markov', 'knn', 'svm', 'pca']:
            if col not in scores_df.columns:
                scores_df[col] = 0

        # Calculate components
        hot_score = (scores_df['freq'] + scores_df['svm'] + scores_df['rsi']) / 3
        stability_score = (scores_df['slope'] + scores_df['markov']) / 2
        cold_score = scores_df['pca'] # My PCA score is stability-based, but let's use it.
        random_score = scores_df['knn'] # User mapped KNN to Random/Perturbation
        
        total = (
            hot_score * w['hot'] +
            stability_score * w['stability'] +
            cold_score * w['cold'] +
            random_score * w['random'] +
            np.random.rand(len(scores_df)) * 0.05 # Small pure random noise
        )
        
        scores_df['total_score'] = total
        return scores_df

    def partition_strategy(self, scores_df, top_k_per_partition=2):
        print("Executing Partition Strategy...")
        candidates = []
        
        # Ensure 'num' is available as column if it's index
        working_df = scores_df.copy()
        if 'num' not in working_df.columns:
            working_df['num'] = working_df.index
            
        for start, end in self.ranges:
            subset = working_df[(working_df['num'] >= start) & (working_df['num'] <= end)].copy()
            if subset.empty:
                continue
                
            # Normalize within partition
            max_s = subset['total_score'].max()
            if max_s > 0:
                subset['local_score'] = subset['total_score'] / max_s
            else:
                subset['local_score'] = 0
                
            # Select top K per partition
            selected = subset.sort_values(by='local_score', ascending=False).head(top_k_per_partition)
            # Filter by a threshold? Or just take top K.
            # User spec: "Select 1-3 high score numbers... if not enough 5, fill from global"
            
            # Let's verify quality - strictly > 0.8 local score?
            # Or just take the best 2.
            best_in_zone = selected[selected['local_score'] > 0.7] # loose threshold
            candidates.extend(best_in_zone['num'].tolist())
            
        # Deduplicate
        candidates = sorted(list(set(candidates)))
        
        # Fill if less than 5
        if len(candidates) < 5:
            remaining_needed = 5 - len(candidates)
            # Get global top not in candidates
            mask = ~working_df['num'].isin(candidates)
            extras = working_df[mask].sort_values(by='total_score', ascending=False).head(remaining_needed)
            candidates.extend(extras['num'].tolist())
            
        return sorted(candidates[:7]) # Return roughly 5-7 numbers

    def update_weights(self, last_prediction_accuracy):
        """
        Feedback loop:
        accuracy: float 0.0 to 1.0 (e.g. hits / 5)
        """
        print(f"Updating weights based on accuracy: {last_prediction_accuracy}")
        # Simple logic:
        # If High Accuracy (>0.6, i.e., 3+ hits): Boost Hot
        # If Low Accuracy (<0.2, i.e., 0-1 hit): Boost Stability/Random
        
        if last_prediction_accuracy >= 0.6:
            self.weights['hot'] += 0.05
            self.weights['random'] -= 0.01
        elif last_prediction_accuracy <= 0.2:
            self.weights['stability'] += 0.05
            self.weights['random'] += 0.05
            self.weights['hot'] -= 0.02
        
        # Clip weights to reasonable bounds
        for k in self.weights:
            self.weights[k] = max(0.1, min(2.0, self.weights[k]))
            
        self.save_config()

if __name__ == "__main__":
    # Test stub
    df = pd.DataFrame({
        'num': range(1, 40),
        'freq': np.random.rand(39),
        'svm': np.random.rand(39),
        'rsi': np.random.rand(39),
        'slope': np.random.rand(39),
        'markov': np.random.rand(39),
        'pca': np.random.rand(39),
        'knn': np.random.rand(39)
    })
    strat = StrategyEngine()
    scored = strat.calculate_total_score(df)
    picks = strat.partition_strategy(scored)
    print("Picks:", picks)
