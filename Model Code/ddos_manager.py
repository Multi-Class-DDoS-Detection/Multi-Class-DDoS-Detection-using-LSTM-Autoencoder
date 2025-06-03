import argparse
import os
import subprocess
import threading
import time
from pathlib import Path

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs("attack_reports", exist_ok=True)

def run_receiver():
    """Run the file receiver script"""
    print("Starting file receiver...")
    from receiver import receive_file
    receive_file()
    print("File receiver completed.")

def run_model(input_file=None):
    """Run the DDoS detection model"""
    print("Starting DDoS detection model...")
    
    if input_file is None:
        # Look for CSV files in the current directory
        csv_files = list(Path('.').glob('*.csv'))
        if not csv_files:
            print("No CSV files found. Please provide an input file with --input")
            return
        input_file = str(csv_files[0])
        print(f"Using {input_file} as input")
    
    from Model import detect_and_classify
    import pandas as pd
    
    # Load the data and run detection
    df = pd.read_csv(input_file)
    results, summary_file = detect_and_classify(df)
    
    print(f"Model processing completed. Results written to {summary_file}")
    return summary_file

def run_webapp():
    """Run the Flask web application"""
    print("Starting Flask web application...")
    from app import app
    # Run Flask app in debug mode
    app.run(debug=True, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='DDoS Detection System')
    parser.add_argument('--mode', type=str, default='all', 
                        choices=['all', 'receiver', 'model', 'webapp', 'model-webapp', 'receiver-model'],
                        help='Mode to run (default: all)')
    parser.add_argument('--input', type=str, help='Input CSV file for the model')
    args = parser.parse_args()
    
    if args.mode == 'receiver':
        run_receiver()
    
    elif args.mode == 'model':
        run_model(args.input)
    
    elif args.mode == 'webapp':
        run_webapp()
    
    elif args.mode == 'model-webapp':
        # Run the model and then start the webapp
        summary_file = run_model(args.input)
        run_webapp()
    
    elif args.mode == 'receiver-model':
        # Run the receiver to get the file, then process with the model
        run_receiver()
        # Look for the most recently created CSV file
        csv_files = list(Path('.').glob('*.csv'))
        if csv_files:
            # Get the most recently modified file
            most_recent = max(csv_files, key=os.path.getmtime)
            print(f"Processing most recently received file: {most_recent}")
            run_model(str(most_recent))
        else:
            print("No CSV files found after receiving. Cannot run model.")
    
    elif args.mode == 'all':
        # Start receiver in a separate thread
        receiver_thread = threading.Thread(target=run_receiver)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        print("Waiting for file to be received...")
        # Wait for some time for a file to be received
        time.sleep(3)
        
        # Check for the file periodically
        max_wait = 30  # Maximum wait time in seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            csv_files = list(Path('.').glob('*.csv'))
            if csv_files:
                # Get the most recently modified file
                most_recent = max(csv_files, key=os.path.getmtime)
                print(f"Processing file: {most_recent}")
                run_model(str(most_recent))
                break
            time.sleep(2)
        
        # Run the web app regardless of whether we received a file
        run_webapp()

if __name__ == "__main__":
    main()