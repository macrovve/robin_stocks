import robin_stocks.robinhood as rs
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from tabulate import tabulate
from collections import defaultdict


def login():
    """Login to Robinhood account using credentials from .env file"""
    load_dotenv()
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    
    if not username or not password:
        raise ValueError("Please set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in .env file")
    
    return rs.login(username, password)

def get_option_details(leg):
    """Extract option details from leg information"""
    if not leg:
        return "N/A"
    
    option_type = leg.get('option_type', '').upper()
    strike_price = leg.get('strike_price', 'N/A')
    expiration_date = leg.get('expiration_date', 'N/A')
    
    return f"{option_type} {strike_price} {expiration_date}"

def process_orders(orders):
    """Process orders and create a table of buy/sell transactions"""
    # Group orders by symbol
    symbol_orders = defaultdict(list)
    
    for order in orders:
        symbol = order.get('chain_symbol')
        if symbol:
            # Extract relevant information
            created_at = datetime.fromisoformat(order.get('created_at').replace('Z', '+00:00'))
            side = order.get('legs', [{}])[0].get('side')
            quantity = float(order.get('quantity', 0))
            price = float(order.get('price', 0))
            premium = float(order.get('premium', 0))
            state = order.get('state')
            
            # Get option details from the first leg
            option_details = get_option_details(order.get('legs', [{}])[0])
            
            symbol_orders[symbol].append({
                'time': created_at,
                'side': side,
                'quantity': quantity,
                'price': price,
                'premium': premium,
                'state': state,
                'option_details': option_details
            })
    
    # Create table data
    table_data = []
    for symbol, trades in symbol_orders.items():
        # Sort trades by time
        trades.sort(key=lambda x: x['time'])
        
        # Add header for symbol
        table_data.append([symbol, '', '', '', '', '', ''])
        
        # Add trades
        for trade in trades:
            if trade['state'] == 'filled':  # Only show filled orders
                table_data.append([
                    trade['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    trade['side'].upper(),
                    f"{trade['quantity']:.0f}",
                    f"${trade['price']:.2f}",
                    f"${trade['premium']:.2f}",
                    trade['option_details'],
                    trade['state']
                ])
        
        # Add separator
        table_data.append(['', '', '', '', '', '', ''])
    
    return table_data

def main():
    try:
        # Login to Robinhood
        print("Logging in to Robinhood...")
        login()
        
        # Get all option orders from the last day
        orders = rs.get_all_option_orders(start_date=datetime.now() - timedelta(days=1))
        
        # Process orders and create table
        table_data = process_orders(orders)
        
        # Print table
        headers = ['Time', 'Side', 'Quantity', 'Price', 'Premium', 'Option Details', 'State']
        print("\n=== Option Orders (Last 24 Hours) ===")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Get trades from the last 7 days
        # print("\nFetching your recent trades...")
        # trades_df = get_trades(days_back=7)
        
        # Display trades
        # display_trades(trades_df)

if __name__ == "__main__":
    main() 