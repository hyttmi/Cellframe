import subprocess
import re
import sqlite3
import inspect

def fire_and_split_command(command, split=True):
    command = command.split()
    try:
        command_run = subprocess.run(command, check=True, stdout=subprocess.PIPE)
        if split:
            command_run = str(command_run.stdout, encoding="utf-8").splitlines()
        else:
            command_run = str(command_run.stdout, encoding="utf-8")
    except Exception as e:
        print(f"Didn't work, got error: {e}")
        exit()

    return command_run

def wallets_to_db():
    print("Running: " + inspect.stack()[0][3])
    connection = sqlite3.connect("cellframe_data.db")
    with connection:        
        connection.execute("DROP TABLE IF EXISTS wallet_data")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS wallet_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT,
                token TEXT,
                balance TEXT
            )
        """)
    command = fire_and_split_command("cellframe-node-cli ledger list balance -net Backbone", True)
    for line in command:
        if "null" in line or not "CELL" in line:
            continue
        command_regex = re.compile(r"Ledger balance key: (\w+).+token_ticker:(\w+).+balance:(\d+)")
        match = re.search(command_regex, line)
        if match:
            addr = match.group(1)
            token = match.group(2)
            balance = match.group(3)
            with connection:
                try:
                    connection.execute("INSERT INTO wallet_data (address, token, balance) VALUES (?, ?, ?)",
                                       (addr, token, balance))
                except sqlite3.IntegrityError:
                    pass

wallets_to_db()