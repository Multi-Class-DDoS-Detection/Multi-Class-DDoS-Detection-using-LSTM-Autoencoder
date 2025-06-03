# from flask import Flask, render_template
# import os

# app = Flask(__name__)

# # Hardcoded file path
# TEXT_FILE_PATH = "data/sample.txt"

# # Function to read and parse the text file into records
# def parse_file():
#     records = []
#     attack_stats = {"yes": 0, "no": 0}
#     ddos_types = {}
#     ip_addresses = set()

#     if os.path.exists(TEXT_FILE_PATH):
#         with open(TEXT_FILE_PATH, "r") as file:
#             lines = file.readlines()

#         record = {}
#         for line in lines:
#             if line.strip():
#                 key, value = line.split(":")
#                 record[key.strip()] = value.strip()

#                 # If all keys are collected, add to records and reset
#                 if len(record) == 3:
#                     records.append(record)

#                     # Process stats
#                     attack = record.get("Attack")
#                     attack_stats[attack] += 1

#                     ddos_type = record.get("Type of DDOS")
#                     ddos_types[ddos_type] = ddos_types.get(ddos_type, 0) + 1

#                     ip_address = record.get("IP address")
#                     ip_addresses.add(ip_address)

#                     record = {}

#     return records, attack_stats, ddos_types, ip_addresses

# @app.route("/")
# def index():
#     records, attack_stats, ddos_types, ip_addresses = parse_file()
#     return render_template("index.html", records=records, attack_stats=attack_stats, ddos_types=ddos_types, ip_addresses=ip_addresses)

# if __name__ == "__main__":
#     app.run(debug=True)











# from flask import Flask, render_template, jsonify
# import os

# app = Flask(__name__)

# TEXT_FILE_PATH = "data/sample.txt"

# def parse_file():
#     records = []
#     attack_type_counter = {}
#     anomaly_counter = {"Anomaly": 0, "Benign": 0}

#     if os.path.exists(TEXT_FILE_PATH):
#         with open(TEXT_FILE_PATH, "r", encoding="utf-8") as file:
#             content = file.read().strip()
#             entries = content.split("\n\n")  # split records by blank lines

#             for entry in entries:
#                 lines = entry.strip().split("\n")
#                 record = {}
#                 for line in lines:
#                     if ":" in line:
#                         key, value = line.split(":", 1)
#                         record[key.strip()] = value.strip()

#                 if record:
#                     records.append(record)

#                     attack_type = record.get("Type of Attack", "Unknown")
#                     attack_type_counter[attack_type] = attack_type_counter.get(attack_type, 0) + 1

#                     anomaly_status = record.get("Anomaly or Beningn", "Unknown")
#                     if "anomaly" in anomaly_status.lower():
#                         anomaly_counter["Anomaly"] += 1
#                     else:
#                         anomaly_counter["Benign"] += 1

#     return records, attack_type_counter, anomaly_counter

# @app.route('/')
# def index():
#     records, attack_type_counter, anomaly_counter = parse_file()
#     return render_template('index.html',
#                            records=records,
#                            attack_type_counter=attack_type_counter,
#                            anomaly_counter=anomaly_counter)

# @app.route('/get-data')
# def get_data():
#     records, attack_type_counter, anomaly_counter = parse_file()
#     return jsonify({
#         "records": records,
#         "attack_type_counter": attack_type_counter,
#         "anomaly_counter": anomaly_counter
#     })

# if __name__ == "__main__":
#     app.run(debug=True)





















from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

TEXT_FILE_PATH = "data/sample.txt"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-data")
def get_data():
    data = []
    if os.path.exists(TEXT_FILE_PATH):
        with open(TEXT_FILE_PATH, "r") as file:
            lines = file.readlines()
            record = {}
            for line in lines:
                line = line.strip()
                if not line:  # skip empty lines
                    continue
                if line.startswith("Anomaly or Benign:"):
                    if record:
                        data.append(record)
                        record = {}
                    record["Anomaly or Benign"] = line.split(":", 1)[1].strip()
                elif line.startswith("Type of Attack:"):
                    record["Type of Attack"] = line.split(":", 1)[1].strip()
                elif line.startswith("Attack Count:"):
                    record["Attack Count"] = int(line.split(":", 1)[1].strip())
                elif line.startswith("DST IP Address:"):
                    record["DST IP Address"] = line.split(":", 1)[1].strip()
                elif line.startswith("DST Port:"):
                    record["DST Port"] = line.split(":", 1)[1].strip()
                elif line.startswith("Attack Category:"):
                    record["Attack Category"] = line.split(":", 1)[1].strip()
                elif line.startswith("Protocol:"):
                    record["Protocol"] = line.split(":", 1)[1].strip()
                elif line.startswith("Description:"):
                    record["Description"] = line.split(":", 1)[1].strip()

            if record:
                data.append(record)

    return jsonify(data)

# @app.route("/get-data")
# def get_data():
#     data = []
#     if os.path.exists(TEXT_FILE_PATH):
#         with open(TEXT_FILE_PATH, "r") as file:
#             lines = file.readlines()
#             record = {}
#             for line in lines:
#                 line = line.strip()
#                 if not line:  # skip empty lines
#                     continue
#                 if line.startswith("Anomaly or Benign:"):
#                     if record:
#                         data.append(record)
#                         record = {}
#                     record["Anomaly or Benign"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("Type of Attack:"):
#                     record["Type of Attack"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("Attack Count:"):
#                     record["Attack Count"] = int(line.split(":", 1)[1].strip())
#                 elif line.startswith("DST IP Address:"):
#                     record["DST IP Address"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("DST Port:"):
#                     record["DST Port"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("Attack Category:"):
#                     record["Attack Category"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("Protocol:"):
#                     record["Protocol"] = line.split(":", 1)[1].strip()
#                 elif line.startswith("Description:"):
#                     record["Description"] = line.split(":", 1)[1].strip()

#             if record:
#                 data.append(record)

#     return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
