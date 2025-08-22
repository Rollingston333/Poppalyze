#!/usr/bin/env python3
"""
System Monitor for Stress Testing
=================================
Monitors system resources during load testing
"""

import psutil
import time
import json
from datetime import datetime

class SystemMonitor:
    def __init__(self, interval=1):
        self.interval = interval
        self.monitoring = False
        self.data = []
    
    def start_monitoring(self, duration_minutes=10):
        """Start monitoring system resources"""
        print("🔍 Starting system monitoring...")
        print(f"📊 Monitoring for {duration_minutes} minutes")
        print("=" * 50)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        self.monitoring = True
        
        # Print header
        print(f"{'Time':<12} {'CPU%':<8} {'RAM%':<8} {'RAM(GB)':<10} {'Network In':<12} {'Network Out':<12} {'Connections':<12}")
        print("-" * 80)
        
        while time.time() < end_time and self.monitoring:
            stats = self.get_system_stats()
            self.data.append(stats)
            
            # Print real-time stats
            print(f"{stats['time']:<12} {stats['cpu_percent']:<8.1f} {stats['memory_percent']:<8.1f} "
                  f"{stats['memory_gb']:<10.1f} {stats['network_in_mb']:<12.1f} {stats['network_out_mb']:<12.1f} "
                  f"{stats['connections']:<12}")
            
            time.sleep(self.interval)
        
        self.save_results()
        self.print_summary()
    
    def get_system_stats(self):
        """Get current system statistics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_gb = memory.used / (1024**3)
        
        # Network
        net_io = psutil.net_io_counters()
        network_in_mb = net_io.bytes_recv / (1024**2)
        network_out_mb = net_io.bytes_sent / (1024**2)
        
        # Network connections
        connections = len(psutil.net_connections())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'time': datetime.now().strftime('%H:%M:%S'),
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_gb': memory_gb,
            'network_in_mb': network_in_mb,
            'network_out_mb': network_out_mb,
            'connections': connections
        }
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        print("\n🛑 Monitoring stopped")
    
    def save_results(self):
        """Save monitoring results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"system_monitor_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.data:
            return
        
        cpu_values = [d['cpu_percent'] for d in self.data]
        memory_values = [d['memory_percent'] for d in self.data]
        connections_values = [d['connections'] for d in self.data]
        
        print("\n" + "=" * 50)
        print("📈 SYSTEM PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"⏱️  Duration: {len(self.data)} seconds")
        print(f"🔥 CPU Usage:")
        print(f"   Average: {sum(cpu_values)/len(cpu_values):.1f}%")
        print(f"   Peak: {max(cpu_values):.1f}%")
        print(f"   Min: {min(cpu_values):.1f}%")
        print(f"💾 Memory Usage:")
        print(f"   Average: {sum(memory_values)/len(memory_values):.1f}%")
        print(f"   Peak: {max(memory_values):.1f}%")
        print(f"🌐 Network Connections:")
        print(f"   Average: {sum(connections_values)/len(connections_values):.0f}")
        print(f"   Peak: {max(connections_values)}")

if __name__ == "__main__":
    import sys
    
    duration = 5  # Default 5 minutes
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    
    monitor = SystemMonitor()
    try:
        monitor.start_monitoring(duration)
    except KeyboardInterrupt:
        monitor.stop_monitoring() 