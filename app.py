from flask import Flask, render_template, request, redirect, url_for
from models import db, Transaction
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server-side chart rendering
import matplotlib.pyplot as plt
import os
import webbrowser
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Chart generation function
def generate_category_chart(transactions):
    if not transactions:
        return

    # Ensure static folder exists
    os.makedirs("static", exist_ok=True)

    # Aggregate spending by category
    category_totals = {}
    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    # Create pie chart
    labels = category_totals.keys()
    sizes = category_totals.values()
    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title("Spending by Category")
    plt.tight_layout()

    # Save chart to static folder
    chart_path = os.path.join("static", "category_chart.png")
    plt.savefig(chart_path)
    plt.close()

@app.route("/")
def index():
    transactions = Transaction.query.all()
    generate_category_chart(transactions)

    # Calculate summary totals
    total = sum(t.amount for t in transactions)
    return render_template("index.html", transactions=transactions, total=total)

@app.route("/add", methods=["POST"])
def add_transaction():
    amount = float(request.form["amount"])
    category = request.form["category"]
    description = request.form["description"]
    new_t = Transaction(amount=amount, category=category, description=description)
    db.session.add(new_t)
    db.session.commit()
    return redirect(url_for("index"))

# Auto-open browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)