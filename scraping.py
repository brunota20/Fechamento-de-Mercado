from typing import Literal, Text
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from bcb import sgs



URL_highlow = "https://www.infomoney.com.br/wp-json/infomoney/v1/highlow"
URL_ibov = "https://www.infomoney.com.br/wp-json/infomoney/v1/graph/IBOVESPA"
URL_usdbtc = "https://www.infomoney.com.br/wp-json/infomoney/v1/usdbtc"


r_highlow = requests.get(URL_highlow).json()
r_ibov = requests.get(URL_ibov).json()
r_usdbtc = requests.get(URL_usdbtc).json()


def email():
    try:
        fromaddr = "brunot.anjos@hotmail.com"
        toaddr = 'vinicius@phidiasinvestimentos.com.br'
        msg = MIMEMultipart()

        msg['From'] = fromaddr 
        msg['To'] = toaddr
        msg['Subject'] = "Fechamento de Mercado" + " ({})".format(date.today())

        body = f"""
            Boa noite! Tudo bem?

            Segue o Fechamento de Mercado do dia {date.today()} anexado ao e-mail.

            Abraços.
            """

        msg.attach(MIMEText(body, 'plain'))

        imagem = 'Fechamento de Mercado.png'
        attachment = open(imagem,'rb')


        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % imagem)

        msg.attach(part)

        attachment.close()

        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login(fromaddr, "anjos4")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print('\nEmail enviado com sucesso!')
    except Exception as e:
        print("\nErro ao enviar email")
        print(e)



def yfinance():
    ibov = yf.download("^BVSP", start = date.today())
    fechamento = ibov.iloc[0].at["Close"]
    abertura = ibov.iloc[0].at["Open"]
    porcentagem = round((((fechamento - abertura)*100)/abertura),2)
    if str(porcentagem).startswith("+") or str(porcentagem).startswith("-"):
        pass
    else:
        if porcentagem > 0:
            porcentagem = "+"+"{:.2f}".format(porcentagem)
        else:
            porcentagem = "-"+"{:.2f}".format(porcentagem)
    return '{0:,}'.format(int(fechamento)).replace(',','.'), str(porcentagem)


def dados_selic():
    selic = sgs.get(('selic', 432), start = '2010-01-01')
    return str(selic.iloc[-1].at["selic"]).replace(".",",")


def anbima_CDI():
    cdi = sgs.get(('Selic', 1178), last=1)

    cdi_string =  str(cdi.Selic.iloc[0]).replace(".",",")
    
    return cdi_string

anbima_CDI()


def data():
    meses = {"1":"Janeiro", "2":"Fevereiro", "3":"Março", "4":"Abril", "5":"Maio", "6":"Junho", "7":"Julho", "8":"Agosto", "9":"Setembro","10":"Outubro","11":"Novembro","12":"Dezembro"}
    data_atual = date.today()
    for mes in meses:
        if mes == str(data_atual.month):
            mes_texto = meses[mes]
    data_atual_texto = "{} de {} de {}".format(data_atual.day, mes_texto, data_atual.year)

    return data_atual_texto

def SeparacaoHighLow(highlow):
    high = highlow["high"]
    low = highlow["low"]
    return high,low

def SeparacaoUSDBTC(tabela):
    if tabela[0]['Name'] == "D\u00d3LAR":
        usd = tabela[0]
    if tabela[1]['Name'] == "BITCOIN":
        btc = tabela[1]
    return [usd],[btc]

def CriaTabela(tabelacrua):
    tabela = pd.DataFrame(tabelacrua)
    return tabela


def dados():
    high, low = SeparacaoHighLow(r_highlow)
    usd,btc = SeparacaoUSDBTC(r_usdbtc)
    #lista_btc = [btc]
    tabela_high = CriaTabela(high)
    tabela_low = CriaTabela(low)
    tabela_ibov = CriaTabela(r_ibov)
    tabela_usd = CriaTabela(list(usd))
    tabela_btc = CriaTabela(list(btc))
    return tabela_high, tabela_low, tabela_usd, tabela_btc, tabela_ibov


def dadosIbov(tabela):
    last_row = tabela.iloc[-1]
    first_row = tabela.iloc[0]
    preco_fechamento = last_row[1]
    preco_abertura = first_row[1]
    porcentagem = round((((preco_fechamento - preco_abertura)*100)/preco_abertura),2)
    if str(porcentagem).startswith("+") or str(porcentagem).startswith("-"):
        pass
    else:
        if porcentagem > 0:
            porcentagem = "+"+"{:.2f}".format(porcentagem)
        else:
            porcentagem = "-"+"{:.2f}".format(porcentagem)
    #porcentagem = "{:.2f}".format(porcentagem)
    preco_fechamento = "{:,}".format(round(preco_fechamento))
    preco_fechamento = str(preco_fechamento).replace(",",".")
    return preco_fechamento, porcentagem
    
def dadosUsdBtc(tabela):
    preco = tabela.iloc[0,2]
    porcentagem = str(tabela.iloc[0,4]).replace("<sub>","").replace("</sub>","").replace("<sup>%</sup>","").replace(",",".")
    return preco, porcentagem


def dadosHighLow(tabela):
    tickers = []
    value = []
    rent = []
    for i in tabela.index:
        stockcode = str(tabela["StockCode"][i])
        valor = "R$ " + str("{:.2f}".format(tabela["VALOR"][i])).replace(".",",")
        oscilacao = str("{:.2f}".format(tabela["OSCILACAO"][i]))
        tickers.append(stockcode)
        value.append(valor)
        rent.append(oscilacao)
    return tickers, value, rent

def corFonte(porcentagem):
    if float(porcentagem) >= 0:
        cor = "green"
    else:
        cor = "red"
    return cor

def comparacao(yf_ibov, infomoney_ibov):
    try:
        if yf_ibov == infomoney_ibov:
            return infomoney_ibov
        else:
            return yf_ibov
    except:
        return infomoney_ibov

def imagem(data, fechamento_ibov, porcentagem_ibov, fechamento_dolar, porcentagem_dolar, 
ticker_high, valor_high, porcentagem_high, ticker_low, valor_low, porcentagem_low, cdi, selic):
    img = Image.open("Fechamento Cru.png")
    cor_data = "grey"
 
    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)

    path = "goldman-sans-cufonfonts"
    
    fonte_data = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=40)
    fonte_preco_ibov_usd = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=55)
    fonte_porcentagem_ibov_usd = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=32)
    fonte_ticker = ImageFont.truetype(font=path+"/GoldmanSansCd_Bd.ttf", size=50)
    fonte_preço = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=40)
    fonte_rentabilidade = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=25)
    fonte_CDI = ImageFont.truetype(font=path+"/GoldmanSans_Rg.ttf", size=56)
 
    # data
    I1.text((340, 528), data, font=fonte_data, fill=cor_data)
    # Preço do Ibov
    if len(fechamento_ibov) > 6:
        I1.text((707, 604), str(fechamento_ibov), font=fonte_preco_ibov_usd, align='right', fill='white')
    else:
        I1.text((737, 604), str(fechamento_ibov), font=fonte_preco_ibov_usd, align='right', fill='white')
    # Porcentagem do Ibov
    cor_porcentagem_ibov = corFonte(porcentagem_ibov)
    I1.text((805, 661), str(porcentagem_ibov)+"%", font=fonte_porcentagem_ibov_usd, align='right', fill=cor_porcentagem_ibov)
    
    # Preço do Dólar
    I1.text((720, 726), str(fechamento_dolar), font=fonte_preco_ibov_usd, align='right', fill='white')
    # Porcentagem do dolar
    cor_porcentagem_dolar = corFonte(porcentagem_dolar)
    I1.text((800, 783), str(porcentagem_dolar)+"%", font=fonte_porcentagem_ibov_usd, align='right', fill=cor_porcentagem_dolar)
    # Porcentagem CDI
    I1.text((723, 864), cdi+"%", font=fonte_CDI, align='right', fill='white')
    # Porcentagem SELIC
    I1.text((723, 984), f"{selic}%", font=fonte_CDI, align='right', fill='white')
    # Tickers altas
    distancia_ticker_high = 10
    for i in range(len(ticker_high)):
        I1.text((166, 1199 + distancia_ticker_high), ticker_high[i], font=fonte_ticker, align='left', fill='white')
        distancia_ticker_high = distancia_ticker_high + 85
    # Preço altas
    distancia_preco_high = 10
    for i in range(len(valor_high)):
        I1.text((360, 1209 + distancia_preco_high), valor_high[i], font=fonte_preço, align='right', fill='white')
        distancia_preco_high = distancia_preco_high + 85   
    # Porcentagem altas
    distancia_rentabilidade_high = 10
    for i in range(len(porcentagem_high)):
        cor_rentabilidade_high = corFonte(porcentagem_high[i])
        I1.text((360, 1247 + distancia_rentabilidade_high), "+"+str(porcentagem_high[i])+"%", font=fonte_rentabilidade, align='right', fill=cor_rentabilidade_high)
        distancia_rentabilidade_high = distancia_rentabilidade_high + 85  


    # Tickers baixas
    distancia_ticker_low = 10
    for i in range(len(ticker_low)):
        I1.text((789, 1199 + distancia_ticker_low), ticker_low[i], font=fonte_ticker, align='right', fill='white')
        distancia_ticker_low = distancia_ticker_low + 85
    # Preço baixas
    distancia_preco_low = 10
    for i in range(len(valor_low)):
        I1.text((570, 1209 + distancia_preco_low), valor_low[i], font=fonte_preço, align='left', fill='white')
        distancia_preco_low = distancia_preco_low + 85 
    # Porcentagem baixas
    distancia_rentabilidade_low = 10
    for i in range(len(porcentagem_low)):
        cor_rentabilidade_low = corFonte(porcentagem_low[i])
        I1.text((570, 1247 + distancia_rentabilidade_low), str(porcentagem_low[i])+"%", font=fonte_rentabilidade, align='left', fill=cor_rentabilidade_low)
        distancia_rentabilidade_low = distancia_rentabilidade_low + 85
    
    # Save the edited image
    img.save("Fechamento de Mercado.png")


def main():
    t_high, t_low, t_usd, t_btc, t_ibov = dados()
    yf_ibov, yf_porcentagem = yfinance()
    data_texto = data()
    fechamento_ibov, porcentagem_ibov = dadosIbov(t_ibov)
    fechamento_dolar, porcentagem_dolar = dadosUsdBtc(t_usd)
    ticker_high, valor_high, porcentagem_high = dadosHighLow(t_high)
    ticker_low, valor_low, porcentagem_low = dadosHighLow(t_low)
    fechamento_comparado = comparacao(yf_ibov,fechamento_ibov)
    porcentagem_comparada = comparacao(yf_porcentagem, porcentagem_ibov)
    selic = dados_selic()
    cdi = anbima_CDI()
    imagem(data_texto, fechamento_comparado, porcentagem_comparada, fechamento_dolar, porcentagem_dolar, ticker_high, valor_high, porcentagem_high, ticker_low, valor_low, porcentagem_low, cdi, selic)
    email()


 
main()
