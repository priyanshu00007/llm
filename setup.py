"""Setup script for creating sample database."""

import sqlite3
import os


def create_sample_database():
    """Create a sample SQLite database for testing."""
    
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'sample.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            quantity INTEGER,
            date TEXT
        )
    ''')
    
    # Insert sample data
    sample_data = [
        (1, 'Laptop', 'Electronics', 999.99, 50, '2024-01-15'),
        (2, 'Mouse', 'Electronics', 29.99, 200, '2024-01-16'),
        (3, 'Keyboard', 'Electronics', 79.99, 150, '2024-01-17'),
        (4, 'Monitor', 'Electronics', 299.99, 75, '2024-01-18'),
        (5, 'Headphones', 'Electronics', 149.99, 100, '2024-01-19'),
        (6, 'Desk', 'Office', 199.99, 30, '2024-01-20'),
        (7, 'Chair', 'Office', 249.99, 40, '2024-01-21'),
        (8, 'Notebook', 'Stationery', 9.99, 500, '2024-01-22'),
        (9, 'Pen Set', 'Stationery', 14.99, 300, '2024-01-23'),
        (10, 'Stapler', 'Stationery', 12.99, 150, '2024-01-24'),
    ]
    
    cursor.executemany(
        'INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?)',
        sample_data
    )
    
    conn.commit()
    conn.close()
    
    print(f"✓ Sample database created at: {db_path}")
    return db_path


def setup_project():
    """Setup the project (create folders, databases, etc.)."""
    
    print("Setting up ReAct Agent project...")
    print()
    
    # Create directories
    dirs = ['data', 'outputs']
    for d in dirs:
        path = os.path.join(os.path.dirname(__file__), d)
        os.makedirs(path, exist_ok=True)
        print(f"✓ Directory created: {d}/")
    
    # Create sample database
    print()
    create_sample_database()
    
    print()
    print("=" * 50)
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Copy .env.example to .env and add your API keys")
    print("2. Run: python examples/basic_usage.py")
    print("3. Or run interactive CLI: python examples/interactive_cli.py")
    print("=" * 50)


if __name__ == "__main__":
    setup_project()
