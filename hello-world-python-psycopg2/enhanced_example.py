#!/usr/bin/env python3
"""
Enhanced CockroachDB example with advanced database functionality.
"""

import logging
import os
import random
import time
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras
from psycopg2 import pool


class CockroachDBManager:
    """Enhanced CockroachDB manager with connection pooling and advanced features."""
    
    def __init__(self, dsn: str, min_connections: int = 2, max_connections: int = 10):
        self.dsn = dsn
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            min_connections, max_connections, dsn,
            application_name="enhanced_crdb_example",
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        psycopg2.extras.register_uuid()
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        self.connection_pool.closeall()

    def create_schema(self):
        """Create enhanced database schema with multiple tables."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Accounts table with additional fields
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        account_number STRING UNIQUE NOT NULL,
                        owner_name STRING NOT NULL,
                        account_type STRING NOT NULL CHECK (account_type IN ('checking', 'savings', 'business')),
                        balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE,
                        INDEX idx_account_number (account_number),
                        INDEX idx_owner_name (owner_name),
                        INDEX idx_created_at (created_at)
                    )
                """)
                
                # Transaction history table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        from_account_id UUID REFERENCES accounts(id),
                        to_account_id UUID REFERENCES accounts(id),
                        amount DECIMAL(15,2) NOT NULL,
                        transaction_type STRING NOT NULL CHECK (transaction_type IN ('transfer', 'deposit', 'withdrawal')),
                        description STRING,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        status STRING DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'reversed')),
                        INDEX idx_from_account (from_account_id),
                        INDEX idx_to_account (to_account_id),
                        INDEX idx_created_at (created_at),
                        INDEX idx_status (status)
                    )
                """)
                
                # Account summaries materialized view
                cur.execute("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS account_summaries AS
                    SELECT 
                        a.id,
                        a.account_number,
                        a.owner_name,
                        a.account_type,
                        a.balance,
                        COUNT(t.id) as transaction_count,
                        COALESCE(SUM(CASE WHEN t.from_account_id = a.id THEN -t.amount ELSE t.amount END), 0) as total_transaction_volume
                    FROM accounts a
                    LEFT JOIN transactions t ON (a.id = t.from_account_id OR a.id = t.to_account_id)
                    WHERE a.is_active = TRUE
                    GROUP BY a.id, a.account_number, a.owner_name, a.account_type, a.balance
                """)
                
                # Trigger to update account updated_at timestamp
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_account_timestamp()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                cur.execute("""
                    DROP TRIGGER IF EXISTS account_update_trigger ON accounts;
                    CREATE TRIGGER account_update_trigger
                        BEFORE UPDATE ON accounts
                        FOR EACH ROW
                        EXECUTE FUNCTION update_account_timestamp();
                """)
                
            conn.commit()
            logging.info("✓ Enhanced schema created successfully")

    def cleanup_schema(self):
        """Drop all tables, views, functions, and triggers created by the demo."""
        print("🧹 Cleaning up enhanced schema...")
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Drop in reverse order of dependencies
                    
                    # Drop materialized view first
                    cur.execute("DROP MATERIALIZED VIEW IF EXISTS account_summaries CASCADE")
                    logging.info("✓ Dropped materialized view: account_summaries")
                    
                    # Drop trigger
                    cur.execute("DROP TRIGGER IF EXISTS account_update_trigger ON accounts")
                    logging.info("✓ Dropped trigger: account_update_trigger")
                    
                    # Drop function
                    cur.execute("DROP FUNCTION IF EXISTS update_account_timestamp")
                    logging.info("✓ Dropped function: update_account_timestamp")
                    
                    # Drop transactions table (has foreign key references to accounts)
                    cur.execute("DROP TABLE IF EXISTS transactions CASCADE")
                    logging.info("✓ Dropped table: transactions")
                    
                    # Drop accounts table
                    cur.execute("DROP TABLE IF EXISTS accounts CASCADE")
                    logging.info("✓ Dropped table: accounts")
                    
                conn.commit()
                print("✅ Schema cleanup completed successfully!")
                
        except Exception as e:
            logging.error(f"❌ Error during schema cleanup: {e}")
            raise

    def create_sample_accounts(self, count: int = 5) -> List[uuid.UUID]:
        """Create sample accounts with realistic data."""
        account_types = ['checking', 'savings', 'business']
        names = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown']
        
        account_ids = []
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for i in range(count):
                    account_id = uuid.uuid4()
                    account_number = f"ACC{random.randint(1000000, 9999999)}"
                    owner_name = names[i % len(names)]
                    account_type = random.choice(account_types)
                    initial_balance = Decimal(str(random.uniform(500.0, 5000.0))).quantize(Decimal('0.01'))
                    
                    cur.execute("""
                        INSERT INTO accounts (id, account_number, owner_name, account_type, balance)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (account_number) DO NOTHING
                    """, (account_id, account_number, owner_name, account_type, initial_balance))
                    
                    account_ids.append(account_id)
                
            conn.commit()
            logging.info(f"✓ Created {count} sample accounts")
        
        return account_ids

    def enhanced_transfer_funds(self, from_account_id: uuid.UUID, to_account_id: uuid.UUID, 
                               amount: Decimal, description: str = None):
        """Enhanced fund transfer with transaction logging and validation."""
        def transfer_operation(conn):
            with conn.cursor() as cur:
                # Lock accounts in consistent order to prevent deadlocks
                account_order = sorted([from_account_id, to_account_id])
                cur.execute("""
                    SELECT id, balance, is_active FROM accounts 
                    WHERE id IN %s ORDER BY id FOR UPDATE
                """, (tuple(account_order),))
                
                accounts = {row['id']: row for row in cur.fetchall()}
                
                if from_account_id not in accounts or to_account_id not in accounts:
                    raise ValueError("One or both accounts not found")
                
                if not accounts[from_account_id]['is_active'] or not accounts[to_account_id]['is_active']:
                    raise ValueError("One or both accounts are inactive")
                
                from_balance = accounts[from_account_id]['balance']
                if from_balance < amount:
                    raise ValueError(f"Insufficient funds: have {from_balance}, need {amount}")
                
                # Perform the transfer
                cur.execute("""
                    UPDATE accounts SET balance = balance - %s 
                    WHERE id = %s
                """, (amount, from_account_id))
                
                cur.execute("""
                    UPDATE accounts SET balance = balance + %s 
                    WHERE id = %s
                """, (amount, to_account_id))
                
                # Log the transaction
                cur.execute("""
                    INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description)
                    VALUES (%s, %s, %s, 'transfer', %s)
                """, (from_account_id, to_account_id, amount, description or f"Transfer of ${amount}"))
        
        with self.get_connection() as conn:
            self.run_transaction(conn, transfer_operation)

    def bulk_deposit(self, account_amounts: Dict[uuid.UUID, Decimal]):
        """Perform bulk deposits using batch operations."""
        def bulk_operation(conn):
            with conn.cursor() as cur:
                # Batch update balances
                for account_id, amount in account_amounts.items():
                    cur.execute("""
                        UPDATE accounts SET balance = balance + %s 
                        WHERE id = %s AND is_active = TRUE
                    """, (amount, account_id))
                    
                    # Log deposit transaction
                    cur.execute("""
                        INSERT INTO transactions (to_account_id, amount, transaction_type, description)
                        VALUES (%s, %s, 'deposit', %s)
                    """, (account_id, amount, f"Bulk deposit of ${amount}"))
        
        with self.get_connection() as conn:
            self.run_transaction(conn, bulk_operation)
        
        logging.info(f"✓ Bulk deposit completed for {len(account_amounts)} accounts")

    def get_account_analytics(self) -> Dict:
        """Get comprehensive account analytics using window functions and aggregations."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Overall statistics
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_accounts,
                        SUM(balance) as total_balance,
                        AVG(balance) as avg_balance,
                        MIN(balance) as min_balance,
                        MAX(balance) as max_balance,
                        PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY balance) as median_balance
                    FROM accounts 
                    WHERE is_active = TRUE
                """)
                overall_stats = cur.fetchone()
                
                # Account distribution by type
                cur.execute("""
                    SELECT 
                        account_type,
                        COUNT(*) as count,
                        SUM(balance) as total_balance,
                        AVG(balance) as avg_balance
                    FROM accounts 
                    WHERE is_active = TRUE
                    GROUP BY account_type
                    ORDER BY count DESC
                """)
                type_distribution = cur.fetchall()
                
                # Recent transaction activity
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('day', created_at) as date,
                        transaction_type,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM transactions 
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE_TRUNC('day', created_at), transaction_type
                    ORDER BY date DESC, transaction_type
                """)
                recent_activity = cur.fetchall()
                
                # Top accounts by balance
                cur.execute("""
                    SELECT 
                        account_number,
                        owner_name,
                        account_type,
                        balance,
                        ROW_NUMBER() OVER (ORDER BY balance DESC) as rank
                    FROM accounts 
                    WHERE is_active = TRUE
                    ORDER BY balance DESC
                    LIMIT 10
                """)
                top_accounts = cur.fetchall()
        
        return {
            'overall_stats': dict(overall_stats),
            'type_distribution': [dict(row) for row in type_distribution],
            'recent_activity': [dict(row) for row in recent_activity],
            'top_accounts': [dict(row) for row in top_accounts]
        }

    def get_transaction_history(self, account_id: uuid.UUID, limit: int = 50) -> List[Dict]:
        """Get detailed transaction history for an account."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        t.id,
                        t.transaction_type,
                        t.amount,
                        t.description,
                        t.created_at,
                        t.status,
                        CASE 
                            WHEN t.from_account_id = %s THEN 'outgoing'
                            WHEN t.to_account_id = %s THEN 'incoming'
                            ELSE 'other'
                        END as direction,
                        from_acc.account_number as from_account,
                        from_acc.owner_name as from_owner,
                        to_acc.account_number as to_account,
                        to_acc.owner_name as to_owner
                    FROM transactions t
                    LEFT JOIN accounts from_acc ON t.from_account_id = from_acc.id
                    LEFT JOIN accounts to_acc ON t.to_account_id = to_acc.id
                    WHERE t.from_account_id = %s OR t.to_account_id = %s
                    ORDER BY t.created_at DESC
                    LIMIT %s
                """, (account_id, account_id, account_id, account_id, limit))
                
                return [dict(row) for row in cur.fetchall()]

    def run_transaction(self, conn, operation, max_retries: int = 3):
        """Enhanced transaction runner with exponential backoff."""
        for retry in range(1, max_retries + 1):
            try:
                with conn:
                    operation(conn)
                return
            except SerializationFailure as e:
                if retry == max_retries:
                    raise
                sleep_time = (2 ** retry) * 0.1 * (random.random() + 0.5)
                logging.debug(f"Serialization failure, retrying in {sleep_time:.2f}s")
                time.sleep(sleep_time)
            except psycopg2.Error as e:
                logging.error(f"Database error: {e}")
                raise

def  demonstrate_advanced_features():
    """Demonstrate the enhanced database functionality."""
    dsn = os.environ.get("DATABASE_URL", "postgresql://root@localhost:26257/defaultdb?sslmode=disable")
    
    print("🚀 Enhanced CockroachDB Example")
    print("=" * 50)
    
    # Initialize the enhanced manager
    db_manager = CockroachDBManager(dsn)
    
    try:
        # Create enhanced schema
        db_manager.create_schema()
        
        # Create sample accounts
        account_ids = db_manager.create_sample_accounts(5)
        
        # Demonstrate bulk operations
        bulk_deposits = {acc_id: Decimal(str(random.uniform(100, 500))) for acc_id in account_ids[:3]}
        db_manager.bulk_deposit(bulk_deposits)
        
        # Demonstrate transfers
        if len(account_ids) >= 2:
            db_manager.enhanced_transfer_funds(
                account_ids[0], account_ids[1], 
                Decimal('250.00'), "Demo transfer"
            )
        
        # Show analytics
        print("\n📊 Account Analytics:")
        analytics = db_manager.get_account_analytics()
        
        stats = analytics['overall_stats']
        print(f"Total Accounts: {stats['total_accounts']}")
        print(f"Total Balance: ${stats['total_balance']:,.2f}")
        print(f"Average Balance: ${stats['avg_balance']:,.2f}")
        
        # Show transaction history
        if account_ids:
            print(f"\n📋 Recent Transactions for Account {account_ids[0]}:")
            history = db_manager.get_transaction_history(account_ids[0], 5)
            for txn in history[:3]:
                print(f"  {txn['direction'].title()}: ${txn['amount']} - {txn['description']}")
        
        print("\n✅ All enhanced features demonstrated successfully!")
        
    except Exception as e:
        logging.error(f"Error during demonstration: {e}")
        raise
    finally:
        db_manager.close_all_connections()


def cleanup_enhanced_schema():
    """Cleanup function to drop all enhanced schema objects."""
    dsn = os.environ.get("DATABASE_URL", "postgresql://root@localhost:26257/defaultdb?sslmode=disable")
    
    print("🧹 Enhanced CockroachDB Schema Cleanup")
    print("=" * 50)
    print("⚠️  This will permanently delete the following objects:")
    print("   • accounts table (and all data)")
    print("   • transactions table (and all data)")
    print("   • account_summaries materialized view")
    print("   • update_account_timestamp function")
    print("   • account_update_trigger trigger")
    print()
    
    # Safety confirmation
    try:
        confirmation = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
        if confirmation not in ['yes', 'y']:
            print("❌ Cleanup cancelled by user")
            return
    except KeyboardInterrupt:
        print("\n❌ Cleanup cancelled by user")
        return
    
    # Initialize the enhanced manager
    db_manager = CockroachDBManager(dsn)
    
    try:
        # Perform cleanup
        db_manager.cleanup_schema()
        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")
        raise
    finally:
        db_manager.close_all_connections()


def main():
    """Main function with enhanced argument parsing."""
    parser = ArgumentParser(
        description=__doc__ + """

Usage Examples:
  # Run advanced features demonstration
  python enhanced_example.py --demo

  # Run with verbose logging
  python enhanced_example.py --verbose --demo

  # Cleanup all demo tables and views
  python enhanced_example.py --cleanup

  # Connect to specific database
  python enhanced_example.py --demo "postgresql://root@host:26257/mydb?sslmode=disable"
        """, 
        formatter_class=RawTextHelpFormatter
    )
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--demo", action="store_true", help="Run advanced features demonstration")
    parser.add_argument("--cleanup", action="store_true", help="Drop all tables and views created by --demo")
    parser.add_argument("dsn", nargs="?", default=os.environ.get("DATABASE_URL"),
                       help="Database connection string")
    
    args = parser.parse_args()
    
    if not args.dsn:
        parser.error("Database connection string not provided")
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if args.cleanup:
        # Run cleanup to drop all enhanced schema objects
        cleanup_enhanced_schema()
    elif args.demo:
        # Run the demonstration of enhanced CockroachDB features
        demonstrate_advanced_features()
    else:
        # Run original simple example
        print("Run with --demo flag to see enhanced features")
        print("Run with --cleanup flag to remove all demo tables and views")


if __name__ == "__main__":
    main()
