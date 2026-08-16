import sqlite3
import sys
from decimal import Decimal, InvalidOperation
from rich.console import Console
from rich.table import Table

console = Console()
ALLOWED_TABLES = {"Income", "Expenses"}
TABLE_ALIASES = {"income": "Income", "expense": "Expenses"}


def _check_table(table: str):
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table}")


def _resolve_table(alias: str):
    table = TABLE_ALIASES.get(alias.lower())
    if table is None:
        console.print(f"[bold red]Unknown type: {alias}. Use «income» or «expense».[/bold red]")
        return None
    return table


def setup_db():
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    for table in ALLOWED_TABLES:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Amount TEXT NOT NULL,
                Category TEXT NOT NULL,
                Description TEXT
            )
        """)
    conn.commit()
    conn.close()


def add_record(table: str, amount: Decimal, category: str, description: str = ""):
    check_table(table)
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {table} (Amount, Category, Description)
        VALUES (?, ?, ?)
    """, (str(amount), category, description))
    conn.commit()
    conn.close()


def show_records(table: str):
    check_table(table)
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        console.print(
            f"[bold black]You don't have any entries in {table} yet!"
            "Add one using the «add.»[/bold black]"
        )
        return

    color = "#00e739" if table == "Income" else "#cd0033"

    tbl = Table(title=f"{table}", style=f"bold {color}")
    tbl.add_column("ID", justify="center", style="dim")
    tbl.add_column("Category", style="italic #ff0080")
    tbl.add_column("Amount", justify="right", style="italic #00bfff")
    tbl.add_column("Description", style="italic #e8e8e8")

    total = Decimal("0")
    for row in rows:
        rec_id, amount_str, category, description = row
        amount = Decimal(amount_str)
        tbl.add_row(str(rec_id), category, f"{amount:.2f} ₽", description or "-")
        total += amount

    console.print(tbl)
    console.print(f"[bold black]Total:[/bold black] [bold {color}]{total:.2f} ₽[/bold {color}]\n")


def update_record(table: str, record_id: int, amount: Decimal, category: str, description: str = ""):
    check_table(table)
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute(f"""
    UPDATE {table}
    SET Amount = ?, Category = ?, Description = ?
    WHERE ID = ?
    """, (str(amount), category, description, record_id))
    conn.commit()
    conn.close()


def delete_record(table: str, record_id: int):
    check_table(table)
    conn = sqlite3.connect("finance.db")
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE ID = ?", (record_id,))
    conn.commit()
    conn.close()


def main():
    setup_db()

    if len(sys.argv) < 2:
        console.print("[bold red]Using a command:[/bold red]")
        console.print("[bold red]python finance.py add «amount» «category» «description (if needed)»[/bold red]")
        console.print("[bold red]python finance.py list[/bold red]")
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 5:
            console.print("[bold red]Error: specify the amount and category![/bold red]"
                          "[bold red]Example: python finance.py add 200 Food Tea («Tea» - optional comment)[/bold red]"
                          )
            return

        table = resolve_table(sys.argv[2])
        if table is None:
            return

        try:
            amount = Decimal(sys.argv[3])
        except InvalidOperation:
            console.print("[bold red]Error: the amount must be a number![/bold red]")
            return

        category = sys.argv[4]
        description = sys.argv[5] if len(sys.argv) > 5 else ""

        add_record(table, amount, category, description)
        console.print(f"[bold green]Successfully added: {amount} ₽ — {category}[/bold green]")

    elif command == "list":
        if len(sys.argv) < 3:
            console.print("[bold red]Error: specify type — income or expense.[/bold red]")
            return

        table = resolve_table(sys.argv[2])
        if table is None:
            return

        show_records(table)

    else:
        console.print(f"[bold red]Unknown command: {command}[/bold red]")


if __name__ == "__main__":
    main()
