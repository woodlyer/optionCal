# app.py (保持不变)
from flask import Flask, render_template, request, jsonify
from scipy.stats import norm
import numpy as np
import datetime

app = Flask(__name__)

# --- Black-Scholes 期权定价模型 ---
def black_scholes(S, K, T, r, sigma, option_type):
    """
    S: 标的资产价格 (Spot price)
    K: 行权价 (Strike price)
    T: 距离到期日的时间 (以年为单位) (Time to expiration in years)
    r: 无风险利率 (Risk-free rate)
    sigma: 波动率 (Volatility)
    option_type: 'call' 或 'put'
    """
    if T <= 0:
        if option_type == 'call':
            return max(0, S - K)
        else: # put
            return max(0, K - S)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else: # put
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return price

# --- 生成 GLD 价格范围用于 X 轴 ---
def generate_gld_price_range(min_price, max_price, step=1):
    """
    生成一个从 min_price 到 max_price 的 GLD 价格数组。
    """
    return np.arange(min_price, max_price + step, step).tolist()

# --- Flask 认证路由 ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('index')) # 已经登录，重定向到主页

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误。', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('您已退出登录。', 'info')
    return redirect(url_for('login'))

# --- Flask 应用路由 ---
@app.route('/btc')
@login_required
def btc():
    """渲染主 HTML 页面"""
    return render_template('btc.html')

@app.route('/')
@login_required
def index():
    """渲染主 HTML 页面"""
    return render_template('index.html')

@app.route('/calculate_option_prices', methods=['POST'])
@login_required
def calculate_option_prices():
    """
    接收前端发送的期权参数和利率，计算价格并返回。
    """
    data = request.json
    options_data = data.get('options', [])
    
    risk_free_rate_input = data.get('riskFreeRate', 0.042197)
    risk_free_rate = float(risk_free_rate_input) 

    gld_min_price = 250 # X轴起点
    gld_max_price = 650 # X轴终点
    gld_price_points = generate_gld_price_range(gld_min_price, gld_max_price, step=1)

    datasets = []
    
    for i, option in enumerate(options_data):
        try:
            expiry_date_str = option['expiryDate']
            strike_price = float(option['strikePrice'])
            volatility_pct = float(option['volatility'])
            calculation_date_str = option['calculationDate']
            option_type = option['optionType']

            volatility = volatility_pct / 100 

            option_prices_for_curve = []
            
            calc_date_obj = datetime.datetime.strptime(calculation_date_str, '%Y-%m-%d')
            expiry_date_obj = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d')
            
            if calc_date_obj >= expiry_date_obj:
                time_to_expiry_years = 0 
            else:
                time_to_expiry_days = (expiry_date_obj - calc_date_obj).days
                time_to_expiry_years = time_to_expiry_days / 365.25 

            for spot_price in gld_price_points:
                option_price = black_scholes(spot_price, strike_price, time_to_expiry_years, risk_free_rate, volatility, option_type)
                option_prices_for_curve.append([round(spot_price, 2), round(option_price, 2)])

            datasets.append({
                'label': f'期权{i+1} (到期: {expiry_date_str}, 行权: {strike_price}, 类型: {option_type}, 波动率: {volatility_pct}%)',
                'data': option_prices_for_curve,
                'type': 'line',
                'name': f'期权{i+1}', 
                'smooth': True, 
                'lineStyle': {
                    'width': 2
                }
            })
        except Exception as e:
            print(f"计算期权价格时出错: {e}")

    return jsonify({
        'gldMinPrice': gld_min_price, # 仍然返回这些，但前端不强制使用
        'gldMaxPrice': gld_max_price,
        'datasets': datasets
    })







@app.route('/calculate_btc_option_prices', methods=['POST'])
@login_required
def calculate_btc_option_prices():
    """
    接收前端发送的期权参数和利率，计算价格并返回。
    """
    data = request.json
    options_data = data.get('options', [])
    
    risk_free_rate_input = data.get('riskFreeRate', 0.042197)
    risk_free_rate = float(risk_free_rate_input) 

    gld_min_price = 50000 # X轴起点
    gld_max_price = 160000 # X轴终点
    gld_price_points = generate_gld_price_range(gld_min_price, gld_max_price, step=1000)

    datasets = []
    
    for i, option in enumerate(options_data):
        try:
            expiry_date_str = option['expiryDate']
            strike_price = float(option['strikePrice'])
            volatility_pct = float(option['volatility'])
            calculation_date_str = option['calculationDate']
            option_type = option['optionType']

            volatility = volatility_pct / 100 

            option_prices_for_curve = []
            
            calc_date_obj = datetime.datetime.strptime(calculation_date_str, '%Y-%m-%d')
            expiry_date_obj = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d')
            
            if calc_date_obj >= expiry_date_obj:
                time_to_expiry_years = 0 
            else:
                time_to_expiry_days = (expiry_date_obj - calc_date_obj).days
                time_to_expiry_years = time_to_expiry_days / 365.25 

                current_hour = datetime.datetime.now().hour
                time_to_expiry_days += (16 - current_hour)/24 #// UTC+0 8:00,相当于北京时间16点，减去今天已经过去的小时数
                time_to_expiry_years = time_to_expiry_days / 365.25 
                 

            for spot_price in gld_price_points:
                option_price = black_scholes(spot_price, strike_price, time_to_expiry_years, risk_free_rate, volatility, option_type)
                option_prices_for_curve.append([round(spot_price, 2), round(option_price, 2)])

            datasets.append({
                'label': f'期权{i+1} (到期: {expiry_date_str}, 行权: {strike_price}, 类型: {option_type}, 波动率: {volatility_pct}%)',
                'data': option_prices_for_curve,
                'type': 'line',
                'name': f'期权{i+1}', 
                'smooth': True, 
                'lineStyle': {
                    'width': 2
                }
            })
        except Exception as e:
            print(f"计算期权价格时出错: {e}")

    return jsonify({
        'gldMinPrice': gld_min_price, # 仍然返回这些，但前端不强制使用
        'gldMaxPrice': gld_max_price,
        'datasets': datasets
    })

# 辅助函数：生成随机颜色 (ECharts 会自动分配颜色)
def get_random_color():
    import random
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r}, {g}, {b})'

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    # Flask 默认运行在 5000 端口
    # 现在我们将使用 SSL 证书来启动 HTTPS
    # 把 cert.pem 和 key.pem 放到和 app.py 同一个目录下，或者指定完整路径
    
    # 注意：使用自签名证书会在浏览器中显示安全警告。
    # 生产环境中推荐使用 Let's Encrypt 等免费的或购买的受信任证书，并配合 Nginx/Apache 反向代理。
#    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True, host='0.0.0.0', port=5000)
