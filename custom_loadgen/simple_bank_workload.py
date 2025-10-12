#!/usr/bin/env python3
"""
Simple Bank Workload Generator for CockroachDB
A Python alternative to 'cockroach workload' command for generating bank-like load.
"""

import psycopg2
import argparse
import time
import threading
import random
import sys
from datetime import datetime
from collections import defaultdict

class BankWorkloadStats:
    """Track workload statistics"""
    def __init__(self):
        self.lock = threading.Lock()
        self.operations = defaultdict(int)
        self.errors = defaultdict(int)
        self.start_time = time.time()
    
    def record_operation(self, op_type, success=True):
        with self.lock:
            if success:
                self.operations[op_type] += 1
            else:
                self.errors[op_type] += 1
    
    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            total_ops = sum(self.operations.values())
            total_errors = sum(self.errors.values())
            
            return {
                'elapsed_time': elapsed,
                'total_operations': total_ops,
                'total_errors': total_errors,
                'ops_per_second': total_ops / elapsed if elapsed > 0 else 0,
                'operations_breakdown': dict(self.operations),
                'errors_breakdown': dict(self.errors)
            }

class SimpleBankWorkload:
    """Simple bank workload generator"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.stats = BankWorkloadStats()
    
    def init_schema(self):
        """Initialize the bank schema (equivalent to 'cockroach workload init bank')"""
        print("🏦 Initializing Bank schema...")
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cur = conn.cursor()
            
            # Create bank database schema
            cur.execute("""
                CREATE DATABASE IF NOT EXISTS bank
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            # Connect to bank database
            bank_conn_string = self.connection_string.replace('/defaultdb', '/bank').replace('/postgres', '/bank')
            conn = psycopg2.connect(bank_conn_string)
            cur = conn.cursor()
            
            # Drop accounts table if exists
            cur.execute("DROP TABLE IF EXISTS accounts CASCADE")

            # Create accounts table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INT PRIMARY KEY,
                    balance INT NOT NULL
                )
            """)
            
            # Create initial accounts (0-999)
            print("📊 Creating initial accounts...")
            cur.execute("SELECT COUNT(*) FROM accounts")
            existing_count = cur.fetchone()[0]
            
            if existing_count == 0:
                # Insert accounts in batches for better performance
                batch_size = 100
                for i in range(0, 1000, batch_size):
                    values = []
                    for account_id in range(i, min(i + batch_size, 1000)):
                        initial_balance = 1000
                        values.append(f"({account_id}, {initial_balance})")
                    
                    if values:
                        cur.execute(f"""
                            INSERT INTO accounts (id, balance) VALUES {','.join(values)}
                        """)
                
                conn.commit()
                print(f"✓ Created 1000 accounts with initial balance of $1000 each")
            else:
                print(f"✓ Schema already exists with {existing_count} accounts")
            
            cur.close()
            conn.close()
            
            print("✅ Bank schema initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Schema initialization failed: {e}")
            return False
    
    def transfer_funds(self, conn):
        """Perform a random funds transfer between accounts"""
        try:
            cur = conn.cursor()
            
            # Pick two random accounts
            from_account = random.randint(0, 999)
            to_account = random.randint(0, 999)
            
            # Ensure different accounts
            while to_account == from_account:
                to_account = random.randint(0, 999)
            
            # Random transfer amount (1-100)
            amount = random.randint(1, 100)
            
            # Check source account balance
            cur.execute("SELECT balance FROM accounts WHERE id = %s", (from_account,))
            result = cur.fetchone()
            
            if result is None or result[0] < amount:
                # Insufficient funds or account not found
                conn.rollback()
                self.stats.record_operation('transfer', False)
                return
            
            # Perform transfer
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, from_account))
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, to_account))
            
            conn.commit()
            self.stats.record_operation('transfer', True)
            
        except Exception as e:
            conn.rollback()
            self.stats.record_operation('transfer', False)
            # Reconnection logic could be added here
    
    def read_balance(self, conn):
        """Read a random account balance"""
        try:
            cur = conn.cursor()
            account_id = random.randint(0, 999)
            
            cur.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
            result = cur.fetchone()
            
            if result:
                self.stats.record_operation('read', True)
            else:
                self.stats.record_operation('read', False)
                
        except Exception as e:
            self.stats.record_operation('read', False)
    
    def worker_thread(self, worker_id, duration):
        """Worker thread that generates load"""
        bank_conn_string = self.connection_string.replace('/defaultdb', '/bank').replace('/postgres', '/bank')
        
        try:
            conn = psycopg2.connect(bank_conn_string)
            conn.autocommit = False
            print(f"Worker {worker_id} connected")
        except Exception as e:
            print(f"Worker {worker_id} failed to connect: {e}")
            return
        
        end_time = time.time() + duration
        operations_count = 0
        
        try:
            while time.time() < end_time:
                # 80% transfers, 20% reads (similar to cockroach workload bank)
                if random.random() < 0.8:
                    self.transfer_funds(conn)
                else:
                    self.read_balance(conn)
                
                operations_count += 1
                
                # Small delay to prevent overwhelming
                time.sleep(0.01)  # 10ms between operations
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
        finally:
            print(f"Worker {worker_id} completed {operations_count} operations")
            try:
                conn.close()
            except:
                pass
    
    def run_workload(self, duration=60, workers=5):
        """Run the bank workload (equivalent to 'cockroach workload run bank')"""
        print(f"🚀 Starting Bank workload...")
        print(f"Duration: {duration}s, Workers: {workers}")
        print("="*50)
        
        # Test connection first
        try:
            bank_conn_string = self.connection_string.replace('/defaultdb', '/bank').replace('/postgres', '/bank')
            test_conn = psycopg2.connect(bank_conn_string)
            test_conn.close()
        except Exception as e:
            print(f"❌ Cannot connect to bank database: {e}")
            print("💡 Did you run the init command first?")
            return False
        
        # Start worker threads
        threads = []
        for i in range(workers):
            thread = threading.Thread(
                target=self.worker_thread,
                args=(i+1, duration),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(0.1)  # Stagger starts
        
        # Monitor progress
        last_print = time.time()
        
        try:
            while any(t.is_alive() for t in threads):
                time.sleep(1)
                
                # Print progress every 10 seconds
                if time.time() - last_print >= 10:
                    stats = self.stats.get_stats()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Ops: {stats['total_operations']:,} | "
                          f"Rate: {stats['ops_per_second']:.1f} ops/sec | "
                          f"Errors: {stats['total_errors']:,}")
                    last_print = time.time()
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping workload...")
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=2)
        
        # Print final results
        final_stats = self.stats.get_stats()
        print("\n" + "="*50)
        print("🏁 WORKLOAD COMPLETE")
        print("="*50)
        print(f"Total Runtime:     {final_stats['elapsed_time']:.2f}s")
        print(f"Total Operations:  {final_stats['total_operations']:,}")
        print(f"Total Errors:      {final_stats['total_errors']:,}")
        print(f"Average Rate:      {final_stats['ops_per_second']:.2f} ops/sec")
        
        if final_stats['operations_breakdown']:
            print("\nOperations Breakdown:")
            for op_type, count in final_stats['operations_breakdown'].items():
                print(f"  {op_type.capitalize()}: {count:,}")
        
        print("="*50)
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Simple Bank Workload Generator (Alternative to cockroach workload)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize bank schema
  python simple_bank_workload.py init "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
  
  # Run workload for 5 minutes with 10 workers
  python simple_bank_workload.py run --duration 300 --workers 10 \\
    "postgresql://root@localhost:26257/defaultdb?sslmode=disable"
        """)
    
    parser.add_argument('command', choices=['init', 'run'], 
                       help='Command to execute (init=setup schema, run=generate load)')
    parser.add_argument('connection_string', 
                       help='PostgreSQL connection string')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in seconds (for run command)')
    parser.add_argument('--workers', type=int, default=5,
                       help='Number of worker threads (for run command)')
    
    args = parser.parse_args()
    
    workload = SimpleBankWorkload(args.connection_string)
    
    if args.command == 'init':
        success = workload.init_schema()
        sys.exit(0 if success else 1)
    
    elif args.command == 'run':
        success = workload.run_workload(args.duration, args.workers)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
