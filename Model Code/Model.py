import argparse
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
import time
import os
import warnings
import random
warnings.filterwarnings('ignore')  

# Define attack category mapping based on the provided table
ATTACK_CATEGORIES = {
    'Benign': 'Normal',
    'DrDoS_MSSQL': 'TCP-based Reflection DDoS',
    'DrDoS_DNS': 'TCP/UDP-based reflection DDoS',
    'DrDoS_LDAP': 'TCP/UDP-based reflection DDoS',
    'DrDoS_NetBIOS': 'TCP/UDP-based reflection DDoS',
    'DrDoS_SNMP': 'TCP/UDP-based reflection DDoS',
    'DrDoS_Portmap': 'TCP/UDP-based reflection DDoS',
    'CharGen': 'UDP-based Reflection DDoS',
    'DrDoS_NTP': 'UDP-based Reflection DDoS',
    'DrDoS_TFTP': 'UDP-based Reflection DDoS',
    'DDoS_SYN': 'TCP-based Exploitation DDoS',
    'DDoS_Web': 'TCP-based Exploitation DDoS',
    'DDoS_UDP_Lag': 'UDP-based Exploitation DDoS',
    'DrDoS_UDP': 'UDP-based Reflection DDoS',
    'DDoS_UDP': 'UDP-based Exploitation DDoS'
}

# Define protocol mapping
PROTOCOL_MAP = {
    'TCP': 6,
    'UDP': 17
}

# Map attack types to protocols
ATTACK_PROTOCOLS = {
    'Benign': 'TCP',
    'DrDoS_MSSQL': 'TCP',
    'DrDoS_DNS': 'UDP',
    'DrDoS_LDAP': 'TCP',
    'DrDoS_NetBIOS': 'UDP',
    'DrDoS_SNMP': 'UDP',
    'DrDoS_Portmap': 'UDP',
    'CharGen': 'UDP',
    'DrDoS_NTP': 'UDP',
    'DrDoS_TFTP': 'UDP',
    'DDoS_SYN': 'TCP',
    'DDoS_Web': 'TCP',
    'DDoS_UDP_Lag': 'UDP',
    'DrDoS_UDP': 'UDP',
    'DDoS_UDP': 'UDP'
}
ATTACK_DESCRIPTIONS = {
    # TCP-based Reflection DDoS
    'DrDoS_MSSQL': 'This is a TCP-based reflection DDoS attack that leverages exposed MSSQL servers to reflect and amplify traffic toward the victim. Restrict MSSQL access to trusted IPs, use firewalls, and apply rate-limiting on port 1433.',

    # TCP/UDP-based Reflection DDoS
    'DrDoS_DNS': 'This is a TCP/UDP-based reflection DDoS attack using misconfigured or open services (like DNS, LDAP, NetBIOS, SNMP, Portmap) to amplify traffic. Secure the services, restrict access, apply rate-limiting, and block spoofed traffic.',
    'DrDoS_LDAP': 'This is a TCP/UDP-based reflection DDoS attack using misconfigured or open services (like DNS, LDAP, NetBIOS, SNMP, Portmap) to amplify traffic. Secure the services, restrict access, apply rate-limiting, and block spoofed traffic.',
    'DrDoS_NetBIOS': 'This is a TCP/UDP-based reflection DDoS attack using misconfigured or open services (like DNS, LDAP, NetBIOS, SNMP, Portmap) to amplify traffic. Secure the services, restrict access, apply rate-limiting, and block spoofed traffic.',
    'DrDoS_SNMP': 'This is a TCP/UDP-based reflection DDoS attack using misconfigured or open services (like DNS, LDAP, NetBIOS, SNMP, Portmap) to amplify traffic. Secure the services, restrict access, apply rate-limiting, and block spoofed traffic.',
    'DrDoS_Portmap': 'This is a TCP/UDP-based reflection DDoS attack using misconfigured or open services (like DNS, LDAP, NetBIOS, SNMP, Portmap) to amplify traffic. Secure the services, restrict access, apply rate-limiting, and block spoofed traffic.',

    # UDP-based Reflection DDoS
    'CharGen': 'This is a UDP-based reflection DDoS attack where services like CharGen, NTP, TFTP, and generic UDP reflect large responses to spoofed requests. Disable unused UDP services, restrict access, and implement anti-spoofing measures.',
    'DrDoS_NTP': 'This is a UDP-based reflection DDoS attack where services like CharGen, NTP, TFTP, and generic UDP reflect large responses to spoofed requests. Disable unused UDP services, restrict access, and implement anti-spoofing measures.',
    'DrDoS_TFTP': 'This is a UDP-based reflection DDoS attack where services like CharGen, NTP, TFTP, and generic UDP reflect large responses to spoofed requests. Disable unused UDP services, restrict access, and implement anti-spoofing measures.',
    'DrDoS_UDP': 'This is a UDP-based reflection DDoS attack where services like CharGen, NTP, TFTP, and generic UDP reflect large responses to spoofed requests. Disable unused UDP services, restrict access, and implement anti-spoofing measures.',

    # UDP-based Exploitation DDoS
    'DDoS_UDP': 'This is a UDP-based exploitation DDoS attack where direct UDP floods overwhelm target systems with traffic. Use rate-limiting, deploy DDoS protection services, and implement traffic filtering at the perimeter.',
    'DDoS_UDP_Lag': 'This is a UDP-based exploitation DDoS attack where direct UDP floods overwhelm target systems with traffic. Use rate-limiting, deploy DDoS protection services, and implement traffic filtering at the perimeter.',

    # TCP-based Exploitation DDoS
    'DDoS_SYN': 'This is a TCP-based exploitation DDoS attack exploiting connection-based protocols (e.g., SYN floods, HTTP floods) to exhaust server resources. Enable SYN cookies, use stateful firewalls, and apply rate-limiting.',
    'DDoS_Web': 'This is a TCP-based exploitation DDoS attack exploiting connection-based protocols (e.g., SYN floods, HTTP floods) to exhaust server resources. Enable SYN cookies, use stateful firewalls, and apply rate-limiting.',

    # Benign
    'Benign': 'Normal network traffic exhibiting no signs of malicious behavior.'
}


def remove_columns(df):
    print("Removing specified columns...")
    
    # Get the column names to drop (by index position)
    columns_to_drop = df.columns[[0, 1, 2, 3, 4, 6]]
    print(f"Columns being removed: {columns_to_drop.tolist()}")
    
    # Drop the columns
    df_reduced = df.drop(columns=columns_to_drop)
    
    print(f"Original column count: {df.shape[1]}")
    print(f"New column count: {df_reduced.shape[1]}")
    
    return df_reduced

def preprocess_data(df, scaler, feature_cols):
    """
    Apply preprocessing steps to the input dataframe
    """
    print(f"Original data shape: {df.shape}")
    
    # Keep only required features
    df_features = df[feature_cols].copy()
    
    # Handle missing values
    print(f"Missing values before handling: {df_features.isnull().sum().sum()}")
    df_features = df_features.fillna(0)  # Fill NA with zeros
    
    # Convert all feature columns to numeric
    df_features = df_features.apply(pd.to_numeric, errors='coerce')
    
    # Replace any remaining NA values after conversion
    df_features = df_features.fillna(0)
    
    # Handle infinite values
    inf_mask = np.isinf(df_features.values).any(axis=1)
    print(f"Found {inf_mask.sum()} rows with infinite values")
    
    # Replace inf values with large finite values
    df_features = df_features.replace([np.inf, -np.inf], np.finfo(np.float64).max)
    
    # Apply the same scaling as during training
    df_scaled = pd.DataFrame(
        scaler.transform(df_features),
        columns=feature_cols
    )
    
    print(f"Processed data shape: {df_scaled.shape}")
    return df_scaled

def generate_random_ip():
    """Generate a random internal IP address for demonstration"""
    return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

def generate_random_port():
    """Generate a random port from specified options"""
    return random.choice([80, 12345, 12543])

def write_attack_info(attack_counts, output_dir="data"):
    """Write attack information to a single text file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a unique filename with timestamp
    timestamp = int(time.time())
    # filename = f"{output_dir}/attack_summary_{timestamp}.txt"
    filename = f"{output_dir}/attack_summary.txt"
    
    with open(filename, 'w') as f:
        # Write a header
        # f.write("==== DDoS Attack Detection Summary ====\n\n")
        # f.write(f"Report generated: {time.ctime()}\n\n")
        
        # Write summary for each attack type
        for attack_type, count in attack_counts.items():
            # Determine if this is an anomaly or benign
            is_anomaly = "Benign" if attack_type == "Benign" else "Anomaly"
            
            # Get attack category
            attack_category = ATTACK_CATEGORIES.get(attack_type, "Unknown")
            
            # Determine protocol
            protocol_name = ATTACK_PROTOCOLS.get(attack_type, "TCP")
            protocol_num = PROTOCOL_MAP.get(protocol_name, 6)
            
            # Generate description
            description = ATTACK_DESCRIPTIONS.get(attack_type, "Unknown attack type detected.")
            
            # Generate random components for each attack type
            dst_ip = "192.168.143.3"
            dst_port = generate_random_port()
            
            # Write the attack information
            # f.write(f"=== {attack_type} ===\n")
            f.write(f"Anomaly or Benign: {is_anomaly}\n")
            f.write(f"Type of Attack: {attack_type}\n")
            f.write(f"Attack Count: {count}\n")
            f.write(f"DST IP Address: {dst_ip}\n")
            f.write(f"DST Port: {dst_port}\n")
            f.write(f"Attack Category: {attack_category}\n")
            f.write(f"Protocol: {protocol_num}\n")
            f.write(f"Description: {description}\n\n")
    
    print(f"Attack summary written to {filename}")
    return filename

def detect_and_classify(df, model_dir='.', output_dir="data"):
    """
    Main function to load models and perform DDoS detection and classification
    """
    start_time = time.time()
    
    # Load preprocessing components
    print("Loading preprocessing components...")
    scaler = joblib.load(f'{model_dir}/scaler.joblib')
    label_encoder = joblib.load(f'{model_dir}/label_encoder.joblib')
    feature_cols = joblib.load(f'{model_dir}/feature_cols.joblib')
    threshold = np.load(f'{model_dir}/anomaly_threshold.npy')
    
    # Load models
    print("Loading models...")
    autoencoder = tf.keras.models.load_model(f'{model_dir}/autoencoder_model.keras')
    classifier = tf.keras.models.load_model(f'{model_dir}/classifier_model.keras')
    
    # Preprocess the data
    print("Preprocessing data...")
    X_processed = preprocess_data(df, scaler, feature_cols)
    
    # Convert to numpy and reshape for LSTM
    X = X_processed.values
    X_reshaped = X.reshape(X.shape[0], 1, X.shape[1])
    
    # Step 3: Anomaly detection with autoencoder
    print("Performing anomaly detection...")
    X_pred = autoencoder.predict(X_reshaped)
    reconstruction_errors = np.mean(np.abs(X_reshaped - X_pred), axis=(1, 2))
    
    # Determine anomalies
    is_anomaly = reconstruction_errors > threshold
    
    # Add results to the dataframe
    results = pd.DataFrame({
        'reconstruction_error': reconstruction_errors,
        'threshold': threshold,
        'is_anomaly': is_anomaly,
        'predicted_label': ['Benign'] * len(is_anomaly)  # Default to benign
    })
    
    # Initialize attack count dictionary
    attack_counts = {'Benign': sum(~is_anomaly)}
    
    # Step 4 & 5: Classify anomalies with DNN
    if np.any(is_anomaly):
        print(f"Classifying {np.sum(is_anomaly)} detected anomalies...")
        anomaly_indices = np.where(is_anomaly)[0]
        anomaly_data = X[anomaly_indices]
        
        # Predict attack types
        attack_probs = classifier.predict(anomaly_data)
        attack_types = np.argmax(attack_probs, axis=1)
        
        # Convert numeric predictions to labels
        attack_labels = label_encoder.inverse_transform(attack_types)
        
        # Update results for anomalies
        results.loc[anomaly_indices, 'predicted_label'] = attack_labels
        
        # Count attack types
        for attack_type in attack_labels:
            if attack_type in attack_counts:
                attack_counts[attack_type] += 1
            else:
                attack_counts[attack_type] = 1
    
    # Calculate timing stats
    end_time = time.time()
    total_time = end_time - start_time
    per_sample_time = total_time / len(df) if len(df) > 0 else 0
    
    print(f"Processed {len(df)} samples in {total_time:.2f} seconds")
    print(f"Average processing time: {per_sample_time*1000:.2f} ms per sample")
    
    # Create a summary report
    summary_file = write_attack_info(attack_counts, output_dir)
    
    # print("\nDetection Results:")
    # for attack_type, count in attack_counts.items():
    #     print(f"{attack_type}: {count}")
    
    return results, summary_file

def main():
    parser = argparse.ArgumentParser(description='DDoS Detection and Classification')
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output', type=str, default='detection_results.csv', help='Path to save the results')
    parser.add_argument('--model_dir', type=str, default='.', help='Directory containing model files')
    parser.add_argument('--report_dir', type=str, default='data', help='Directory to store attack reports')
    parser.add_argument('--remove_columns', action='store_true', help='Remove columns 1-5 and 7 from the input CSV')
    parser.add_argument('--save_reduced', type=str, help='Path to save the CSV with removed columns')
    args = parser.parse_args()
    
    print(f"Loading test data from: {args.input}")
    df = pd.read_csv(args.input)
    
    # Apply column removal if requested
    if args.remove_columns:
        df_reduced = remove_columns(df)
        
        # Save the reduced CSV if a path is specified
        if args.save_reduced:
            df_reduced.to_csv(args.save_reduced, index=False)
            print(f"CSV with removed columns saved to: {args.save_reduced}")
        
        # Use the reduced dataframe for detection
        df = df_reduced
    
    results, summary_file = detect_and_classify(df, args.model_dir, args.report_dir)
    
    # Combine original data with results
    output_df = pd.concat([df, results], axis=1)
    output_df.to_csv(args.output, index=False)
    
    print(f"Results saved to: {args.output}")
    
    # Display summary
    benign_count = sum(results['predicted_label'] == 'Benign')
    attack_count = sum(results['predicted_label'] != 'Benign')
    # print(f"\nSummary: {benign_count} benign traffic, {attack_count} attack traffic detected")
    print(f"\nAttack summary report has been saved to: {summary_file}")

if __name__ == "__main__":
    main()