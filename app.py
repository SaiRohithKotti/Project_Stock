import requests
from openai import OpenAI
from flask import Flask, request, render_template_string, redirect, url_for, flash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flashing messages

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = "Q1G2DLMT5THOX3OD"

# OpenAI API key
OPENAI_API_KEY = "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"

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Function to fetch stock price
def get_stock_price(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Check if the response contains the expected data
    if "Time Series (5min)" not in data:
        return None  # Handle invalid symbol or API error
    
    latest_time = list(data["Time Series (5min)"].keys())[0]
    latest_price = data["Time Series (5min)"][latest_time]["1. open"]
    return latest_price

# Function to get GPT-4 advice
def get_gpt4_advice(stock_symbol, stock_price):
    prompt = f"The current price of {stock_symbol} is {stock_price}. Should I invest in this stock? Provide a brief explanation."
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Flask route for home page
@app.route("/")
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stock Investment Advisor</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                }
                .container {
                    margin-top: 50px;
                }
                .form-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                .btn-primary {
                    background-color: #007bff;
                    border-color: #007bff;
                }
                .btn-primary:hover {
                    background-color: #0056b3;
                    border-color: #0056b3;
                }
                .advice-container {
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6 form-container">
                        <h1 class="text-center">Stock Investment Advisor</h1>
                        <form action="/advice" method="post">
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Enter Stock Symbol:</label>
                                <input type="text" class="form-control" id="symbol" name="symbol" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Get Advice</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """)

# Flask route to handle advice request
@app.route("/advice", methods=["POST"])
def advice():
    symbol = request.form["symbol"].upper()
    price = get_stock_price(symbol)
    
    if price is None:
        flash("Invalid stock symbol or API error. Please try again.", "error")
        return redirect(url_for("home"))
    
    advice = get_gpt4_advice(symbol, price)
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Advice for {{ symbol }}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                }
                .container {
                    margin-top: 50px;
                }
                .advice-container {
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                .btn-primary {
                    background-color: #007bff;
                    border-color: #007bff;
                }
                .btn-primary:hover {
                    background-color: #0056b3;
                    border-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6 advice-container">
                        <h1 class="text-center">Advice for {{ symbol }}</h1>
                        <p><strong>Current Price:</strong> {{ price }}</p>
                        <p><strong>Advice:</strong> {{ advice }}</p>
                        <a href="/" class="btn btn-primary w-100">Back</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """, symbol=symbol, price=price, advice=advice)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)