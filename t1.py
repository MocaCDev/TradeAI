from TradeAI_webpage_backend.webpage import webpage

from flask import (
    Flask, request, jsonify, render_template, 
    redirect, url_for, make_response, send_file
)
from robin_stocks.robinhood import (
    login, get_top_100, get_all_stock_orders, get_all_open_stock_orders, get_quotes, get_stock_order_info, find_stock_orders, get_latest_price, get_ratings, get_earnings,
    get_historical_portfolio, build_holdings, order_buy_market, order, order_sell_market, order_buy_fractional_by_price,
    get_option_order_info, get_stock_quote_by_id, get_stock_quote_by_symbol, get_symbol_by_url,
    get_name_by_url, helper, find_stock_orders,logout, get_total_dividends, get_notifications,
    get_linked_bank_accounts
)
import os
import pandas as pd
import json
import plotly
import plotly.express as px
import sys

a = webpage()
a.launch(use_host=True)
app = Flask(__name__)

all_posts = []
all_data = []
old_length = 0
platform_being_used = None
data = None
error_data = None
greeting = 'Howdy'
has_logged_out = False

def auto_login(username, password, MFA_code):
    data = {'logged_into': username, 'password_used': password, 'MFA Code': MFA_code}
    log = None
    try:
        if MFA_code != None:
            log = login(username, password, mfa_code = MFA_code)
        else:
            log = login(username, password)
    except Exception as e:
        print(f'failed: {e}')
        return render_template('login.html', err_msg=False)
    div = get_linked_bank_accounts()
    data['owner_info'] = {'account_owner': div[0]['bank_account_holder_name']}
    data['withdrawal_limit'] = {'limit': div[0]['withdrawal_limit']}
    data['type'] = {'banking_type': div[0]['bank_account_type']}
    routing = list(div[0]['bank_routing_number'])
    acct_number = str(div[0]['bank_account_number'])
    for i in range(len(routing)-4):
        routing[i] = '*'
    routing = ''.join(routing)
    data['bank_info'] = {'routing_number': routing, 'account_number': acct_number}
    #logout()

    return data

# If the "forced" login attempt(using cookie) is a success then we will redirect to `/account`
def attempt_forced_login():
    global platform_being_used
    global greeting

    try:
        data = auto_login(request.cookies.get('username'), request.cookies.get('password'), None)
        platform = request.cookies.get('for')
        if platform != platform_being_used:
            return render_template('login.html', err_msg=True, err=f'You have already logged in with the platform {platform}.', err_msg2 = True, err2 = f'Logging into {platform_being_used} will erase stored data for {platform}.', platform = platform_being_used)
        
        greeting = 'Welcome Back'
        del data['password_used']
        return redirect(url_for('account'))
    except:
        pass
    
    return render_template('login.html', err_msg=False, platform = platform_being_used)

@app.route('/', methods=['GET', 'POST'])
def home():
    #try:
    #    data = auto_login(request.cookies.get('username'), request.cookies.get('password'), None)
    #    platform_being_used = request.cookies.get('for')
    #    greeting = 'Welcome Back'
    #    return redirect(url_for('account'))
    #except:pass
    
    return render_template('home.html', login_data = False, data = all_posts if len(all_posts) > 0 else {'Data': 'None'})

@app.route('/testing', methods = ['POST', 'GET'])
def testing():
    df = pd.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 
      'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
    })
    fig = px.line(df, x='Fruit', y='Amount', color='City')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('notdash.html', graphJSON=graphJSON)

@app.route('/td')
def td():
    path = f'{os.getcwd()}/m.txt'
    return send_file(path, as_attachment=True)

@app.route('/login_robinhood')
def login_robinhood():
    global platform_being_used
    global greeting
    global has_logged_out
    platform_being_used = 'Robinhood'

    error_data = None

    if has_logged_out:
        return render_template('login.html', err_msg=False, platform = platform_being_used)
    
    return attempt_forced_login()
    #try:
    #    data = auto_login(request.cookies.get('username'), request.cookies.get('password'), None)
    #    #platform_being_used = request.cookies.get('for')
    #    greeting = 'Welcome Back'
    #    del data['password_used']
    #    return redirect(url_for('account'))
    #except:
    #    return render_template('login.html', err_msg=False, platform = platform_being_used)

@app.route('/login_alpaca')
def login_alpaca():
    global platform_being_used
    global greeting
    global has_logged_out
    platform_being_used = 'Alpaca'

    error_data = None

    if has_logged_out:
        return render_template('login.html', err_msg=False, platform = platform_being_used)

    return attempt_forced_login()


#
# TODO: Add `login_alpaca` and `login_tdAmeritrade` below
#

@app.route('/login', methods = ['POST', 'GET'])
def deal_with_login():
    global platform_being_used
    global data
    global error_data
    global has_logged_out

    # Make sure there is no error data
    error_data = None

    if request.method == 'POST':

        print(request.form.get('keepLoggedIn'), '!')
            
        username_gotten = request.form['username']
        password_gotten = request.form['passw']
        MFA_code = request.form['MFACode'] if request.form['MFACode'] != '' else None
        
        if password_gotten == '' and username_gotten == '':
            return render_template('login_robinhood.html', err_msg=True, err="Both username and password left blank")
        if username_gotten == '':
            return render_template('login_robinhood.html', err_msg=True, err="Username was left empty")
        if password_gotten == '':
            return render_template('login_robinhood.html', err_msg=True, err='Password was left empty')
        
        data = auto_login(username_gotten, password_gotten, MFA_code)

        if platform_being_used is None:
            try:
                # Lets see if the cookie saved
                platform_being_used = request.cookies.get('for')

                if platform_being_used is None:
                    raise Exception('Cannot detect the platform being used')
            except:
                return render_template('login_robinhood.html', err_msg=True, err='Something went wrong, please try again')
        
        has_logged_out = False
        return redirect(url_for('account'))
    else:
        try:
            # Attempt to use the cookies to log the user back in
            data = auto_login(request.cookies.get('username'), request.cookies.get('password'), None)
            platform_being_used = request.cookies.get('for')
            greeting = 'Welcome Back'
            del data['password_used']
            has_logged_out = False
            return redirect(url_for('account'))
        except:
            error_data = {'Error': 'An unknown error occurred. Try again later.'}
            return redirect(url_for('error'))

@app.route('/account', methods = ['POST', 'GET'])
def account():
    global platform_being_used
    global data
    global error_data
    global greeting

    error_data = None

    if request.method == 'POST':
        pass

    #if request.form['sub']

    if data is None:
        try:
            return redirect(url_for('deal_with_login'))
        except:
            error_data = {'Error': 'An unknown error occurred. Try again later.'}
            return redirect(url_for('error'))

    if 'password_used' in data:
        res = make_response(render_template('account.html', greeting = greeting, user = data['owner_info']['account_owner'], platform = platform_being_used, login_data = True, data = data))
        res.set_cookie('username', value = data['logged_into'])
        res.set_cookie('password', value = data['password_used'])

        # We don't want to keep the password in `data`
        del data['password_used']

        res.set_cookie('for', value = platform_being_used)
        if data['MFA Code'] is None:
            res.set_cookie('mfa_code', value='x', max_age = 0)
        else:
            res.set_cookie('mfa_code', value = data['MFA Code'])

        return res
    
    return render_template('account.html', greeting = greeting, user = data['owner_info']['account_owner'], platform = platform_being_used, login_data = True, data = data)

@app.route('/logout')
def logout_account():
    global greeting
    global data
    global has_logged_out

    has_logged_out = True

    res = make_response(redirect(url_for('home')))#render_template('home.html', login_data = False, data = all_posts if len(all_posts) > 0 else {'Data': 'None'}))
    data['account_info'] = {
        'username': request.cookies.get('username'),
        'password': request.cookies.get('password'),
        'platform': request.cookies.get('for')
    }
    with open('data.json', 'w') as file:
        file.write(json.dumps(data, indent=2))
        file.flush()
        file.close()
    res.set_cookie('username', '', max_age=0)
    res.set_cookie('password', '', max_age=0)
    res.set_cookie('for', '', max_age=0)
    return res

@app.route('/error')
def error():
    global error_data

    if error_data is None:
        if has_logged_out:
            return redirect(url_for('home'))
        return redirect(url_for('account'))
    return render_template('error.html', error = error_data)

@app.route("/create", methods=["POST"])
def creat_user():
    data = request.get_json()
    old_length = len(all_data)
    all_data.append(data)
    all_posts.append(data)

    return jsonify(data), 200

app.run(debug = True, host='0.0.0.0')