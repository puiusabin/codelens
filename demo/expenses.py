import csv
import json
import os
from pathlib import Path
from datetime import datetime


CATEGORIES = ["food", "transport", "housing", "health", "entertainment", "other"]
LARGE_EXPENSE_THRESHOLD = 500


def load_expenses(filepath):
    expenses = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append({
                "date": row["date"],
                "description": row["description"],
                "amount": float(row["amount"]),
                "category": row["category"].lower(),
            })
    return expenses


def total_by_category(expenses):
    totals = {}
    for expense in expenses:
        cat = expense["category"]
        if cat not in totals:
            totals[cat] = 0
        totals[cat] += expense["amount"]
    return totals


def flag_large_expenses(expenses, threshold=LARGE_EXPENSE_THRESHOLD):
    return [e for e in expenses if e["amount"] > threshold]


def monthly_average(expenses):
    if not expenses:
        return 0
    dates = [datetime.strptime(e["date"], "%Y-%m-%d") for e in expenses]
    months = set((d.year, d.month) for d in dates)
    total = sum(e["amount"] for e in expenses)
    return total / len(months)


def category_breakdown_percent(expenses):
    totals = total_by_category(expenses)
    grand_total = sum(totals.values())
    return {cat: (amount / grand_total) * 100 for cat, amount in totals.items()}


def top_expense(expenses):
    return max(expenses, key=lambda e: e["amount"])


def export_json(expenses, output_path):
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_expenses": len(expenses),
        "grand_total": sum(e["amount"] for e in expenses),
        "by_category": total_by_category(expenses),
        "expenses": expenses,
    }
    with open(output_path, "w") as f:
        json.dump(data, f)
    print(f"Exported to {output_path}")


def export_markdown(expenses, output_path):
    lines = []
    lines.append("# Expense Report\n")
    lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d')}_\n")

    totals = total_by_category(expenses)
    lines.append("## Totals by Category\n")
    lines.append("| Category | Amount |")
    lines.append("|----------|--------|")
    for cat, total in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {cat} | ${total:.2f} |")

    flagged = flag_large_expenses(expenses)
    if flagged:
        lines.append(f"\n## Large Expenses (>${LARGE_EXPENSE_THRESHOLD})\n")
        lines.append("| Date | Description | Amount |")
        lines.append("|------|-------------|--------|")
        for e in flagged:
            lines.append(f"| {e['date']} | {e['description']} | ${e['amount']:.2f} |")

    lines.append(f"\n## Summary\n")
    lines.append(f"- **Total entries:** {len(expenses)}")
    lines.append(f"- **Grand total:** ${sum(e['amount'] for e in expenses):.2f}")
    lines.append(f"- **Monthly average:** ${monthly_average(expenses):.2f}")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Report saved to {output_path}")


def summarize(filepath):
    expenses = load_expenses(filepath)

    print(f"Loaded {len(expenses)} expenses\n")

    totals = total_by_category(expenses)
    print("Totals by category:")
    for cat, total in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<15} ${total:.2f}")

    print(f"\nMonthly average: ${monthly_average(expenses):.2f}")

    flagged = flag_large_expenses(expenses)
    if flagged:
        print(f"\nLarge expenses (>{LARGE_EXPENSE_THRESHOLD}):")
        for e in flagged:
            print(f"  {e['date']}  {e['description']:<30} ${e['amount']:.2f}")

    top = top_expense(expenses)
    print(f"\nBiggest single expense: {top['description']} (${top['amount']:.2f})")

    breakdown = category_breakdown_percent(expenses)
    print("\nCategory breakdown:")
    for cat, pct in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        bar = "#" * int(pct / 2)
        print(f"  {cat:<15} {bar} {pct:.1f}%")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python expenses.py <path-to-csv> [--json <out>] [--md <out>]")
        sys.exit(1)

    filepath = sys.argv[1]
    expenses = load_expenses(filepath)

    args = sys.argv[2:]
    if "--json" in args:
        out = args[args.index("--json") + 1]
        export_json(expenses, out)
    elif "--md" in args:
        out = args[args.index("--md") + 1]
        export_markdown(expenses, out)
    else:
        summarize(filepath)
