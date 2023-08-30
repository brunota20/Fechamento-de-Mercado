# Stock Market Analysis and Email Notification App

This project is a Python application that provides insights into the stock market, analyzes market data, and sends out email notifications with relevant information. The app utilizes various libraries and data sources to deliver a comprehensive overview of market indices, stock returns, and fundamental information.

## Features

- **Market Overview:** Fetches and displays the latest market high and low values, as well as indices like the IBOVESPA.
- **Monthly Returns Analysis:** Provides insights into the monthly returns of selected indices or stocks.
- **Fundamental Information:** Displays fundamental data about selected stocks using the Fundamentus library.
- **Currency Comparison:** Compares the USD and BTC values obtained from Infomoney.
- **Email Notifications:** Sends a daily email with market data and analysis attached as an image.

## Usage

1. Install the required Python libraries by running:
   ```bash
   pip install requests beautifulsoup4 pandas Pillow yfinance smtplib bcb

2. Run the Python script using the following command:

  python scraping.py
   
3. The application will fetch market data, generate an image containing analysis, and send it via email.

## Important Notes

- This application is intended for educational purposes and serves as a demonstration of using libraries for data analysis and email communication.
- Please be aware that the accuracy of stock predictions and financial data can vary due to complex influencing factors.
- Maintain your Python dependencies by using a virtual environment or a requirements file to ensure consistent functionality.

## Acknowledgments

- Libraries used: BeautifulSoup, yfinance, bcb, Pillow, smtplib, Fundamentus.
- The app generates visualizations using the Pillow library.
- Email notifications are sent using the smtplib library.
- Fundamental data is fetched using the Fundamentus library.
- Market data is sourced from Infomoney.
- SELIC and CDI data are provided by Banco Central do Brasil (BCB).

## License
This project is licensed under the MIT License.
