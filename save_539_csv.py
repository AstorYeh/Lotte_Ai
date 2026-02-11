from src.multi_game_manager import MultiGameManager
from src.prediction_history import PredictionHistory

def fix_csv():
    manager = MultiGameManager()
    history = PredictionHistory()
    
    # Get pending prediction
    pending = history.get_pending_prediction()
    if pending:
        print(f"Found pending prediction: {pending['prediction_date']}")
        
        # Construct result format expected by _save_prediction_to_csv
        result = {
            'date': pending['prediction_date'],
            'predictions': pending['predicted_numbers']
        }
        
        manager._save_prediction_to_csv('539', result)
        print("Saved to CSV successfully.")
    else:
        print("No pending prediction found.")

if __name__ == "__main__":
    fix_csv()
