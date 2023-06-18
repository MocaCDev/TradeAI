from flask import (
    Flask, request, jsonify, render_template, 
    redirect, url_for, make_response, send_file
)
from robin_stocks.robinhood import (
    login, get_top_100, get_all_stock_orders, get_all_open_stock_orders, get_quotes, get_stock_order_info, find_stock_orders, get_latest_price, get_ratings, get_earnings,
    get_historical_portfolio, build_holdings, order_buy_market, order, order_sell_market, order_buy_fractional_by_price,
    get_option_order_info, get_stock_quote_by_id, get_stock_quote_by_symbol, get_symbol_by_url,
    get_name_by_url, helper, find_stock_orders,logout, get_total_dividends, get_notifications,
    get_linked_bank_accounts, get_bank_account_info, deposit_funds_to_robinhood_account
)
import json, os
import yfinance as yf
from datetime import datetime, timezone

class webpage_ideals:
    flask_app = Flask(__name__)

    # Types of accounts for Robinhood
    robinhood_accounts = ['traditional', 'roth ira', 'normal ira']

    roth_ira_stocks = []
    norm_ira_stocks = []
    trad_stocks = []

    # Todays date
    date = str(datetime.now().date()).split('-')
    year = date[0]
    date = [int(i) for i in date]
    date[2] += 3
    date = [str(i) for i in date]
    date = '-'.join(date)

    # Manual user stock data
    # This data can either be manually submitted through the website itself, or through the command line
    # This data is registered, and stored, via a "POST" request to `/create`
    # `manual_user_stock_data_length` will (should) always be 1 less than the actual size of `manual_user_stock_data`
    # The reason for this is, when there is new "manual" data, we need to know so if the length is 1 short than the actual length
    # the website will know there is new data
    manual_user_stock_data = []
    manual_user_stock_data_length = 0

    # Records of all possible (external) "POST" request sent to TradeAI wherever a (external) "POST" request is able to be sent
    all_post_requests = []
    add_new_data_button_clicked = False

    # User data, such as account username/password, platform used etc
    user_data = {}
    
    # Robinhood based account
    robinhood_account = None

    # TODO: add variables for alpaca/TD Ameritrade based platforms
    #       These platforms use keys/secret keys to access data instead of just loggin in(I believe)

    # Error data
    error_data = None

    # Indirect error data(this will show on the login forms)
    indirect_error_data = None

    # Greeting(`howdy` upon first login, `Welcome Back` when coming back)
    greeting = 'Howdy'

    # Platform being used(Robinhood, Alpaca or TD Ameritrade; TODO: make it to where all 3 can be used)
    platform_being_used = None

    # Login status
    has_logged_in = False
    has_logged_out = False
    keep_logged_in = False

    # Account buttons
    add_cash_submit_button_clicked = False
    takeout_cash_button_clicked = False
    has_just_added_cash = False

    # Buy information
    stock_colors = [] # This is a color depending on how well the stock is doing compared to what the users gain recommendations are
    stock_symbols = [] # This will be '✗' if the stock does not match >= gains, or '✓' if it does
    price_colors = [] # This will be the color of the prices of the stock. If they are down, it will be red; if they are up, they will be green
    stock_stats = []  # What are the gains (+) or losses (-) for the stock?
    users_personal_share_info = [] # Data over the gains (+) or losses (-) for the user in the given stock, if they own it
    stock_prices = []

    # Information over depositing cash
    cash_amount_to_deposit = 0
    stocks_cash_will_be_used_on = None

    # Last page that the user was on, by default it is home
    last_page = 'home'

    # Information kept while running
    server_running_data = {
        'User Data': None,
        'Logged In': None,
        'Logged Out': None,
        'Keep Logged In': None,
        'Last Page': None,
        'Error Data': None,
        'Greeting': None,
        'Platform Used': None,
        'Indirect Error Data': None,
        'All Post Reqs': None,
        'User Data': None,
        'Manual User Stock Data': None,
        'Roth IRA Stocks': None,
        'Trad IRA Stocks': None,
        'Trad Stocks': None,
        'Cash Deposited': 0,
        'Created Data': []
    }

    all_submitted_data = {'Entries': []}
    has_entries = False

    #
    # update_server_running_data: update all the data and write it to a json file
    #
    def update_server_running_data():
        webpage_ideals.server_running_data['Roth IRA Stocks'] = webpage_ideals.roth_ira_stocks
        webpage_ideals.server_running_data['Trad IRA Stocks'] = webpage_ideals.norm_ira_stocks
        webpage_ideals.server_running_data['Trad Stocks'] = webpage_ideals.trad_stocks
        webpage_ideals.server_running_data['User Data'] = webpage_ideals.user_data
        webpage_ideals.server_running_data['Error Data'] = webpage_ideals.error_data
        webpage_ideals.server_running_data['Indirect Error Data'] = webpage_ideals.indirect_error_data
        webpage_ideals.server_running_data['Logged In'] = webpage_ideals.has_logged_in
        webpage_ideals.server_running_data['Logged Out'] = webpage_ideals.has_logged_out
        webpage_ideals.server_running_data['Keep Logged In'] = webpage_ideals.keep_logged_in
        webpage_ideals.server_running_data['Last Page'] = webpage_ideals.last_page
        webpage_ideals.server_running_data['Greeting'] = webpage_ideals.greeting
        webpage_ideals.server_running_data['Platform Used'] = webpage_ideals.platform_being_used
        webpage_ideals.server_running_data['All Post Reqs'] = webpage_ideals.all_post_requests
        webpage_ideals.server_running_data['Manual User Stock Data'] = webpage_ideals.manual_user_stock_data

        with open('server_run_data.json', 'w') as file:
            file.write(json.dumps(webpage_ideals.server_running_data, indent=2))
            file.flush()
            file.close()
        
        if webpage_ideals.all_submitted_data['Entries'] != []:
            with open('submitted_new_data.json', 'w') as file:
                file.write(json.dumps(webpage_ideals.all_submitted_data, indent = 2))
                file.flush()
                file.close()
    
    #
    # adapt_last_server_run_data: assign all appropriate variables according to the data
    #
    def adapt_last_server_run_data():

        webpage_ideals.server_running_data = json.loads(open('server_run_data.json', 'r').read())
        webpage_ideals.server_running_data['Created Data'] = []

        if os.path.isfile('submitted_new_data.json'):
            webpage_ideals.all_submitted_data = json.loads(open('submitted_new_data.json', 'r').read())
            webpage_ideals.server_running_data['Created Data'] = webpage_ideals.all_submitted_data
            webpage_ideals.has_entries = True

        webpage_ideals.roth_ira_stocks = webpage_ideals.server_running_data['Roth IRA Stocks']
        webpage_ideals.norm_ira_stocks = webpage_ideals.server_running_data['Trad IRA Stocks']
        webpage_ideals.trad_stocks = webpage_ideals.server_running_data['Trad Stocks']
        webpage_ideals.user_data = webpage_ideals.server_running_data['User Data']
        webpage_ideals.error_data = webpage_ideals.server_running_data['Error Data']
        webpage_ideals.indirect_error_data = webpage_ideals.server_running_data['Indirect Error Data']
        webpage_ideals.has_logged_in = webpage_ideals.server_running_data['Logged In']
        webpage_ideals.has_logged_out = webpage_ideals.server_running_data['Logged Out']
        webpage_ideals.keep_logged_in = webpage_ideals.server_running_data['Keep Logged In']
        webpage_ideals.last_page = webpage_ideals.server_running_data['Last Page']
        webpage_ideals.greeting = webpage_ideals.server_running_data['Greeting']
        webpage_ideals.platform_being_used = webpage_ideals.server_running_data['Platform Used']
        webpage_ideals.all_post_requests = webpage_ideals.server_running_data['All Post Reqs']
        webpage_ideals.manual_user_stock_data = webpage_ideals.server_running_data['Manual User Stock Data']
        webpage_ideals.manual_user_stock_data_length = len(webpage_ideals.manual_user_stock_data) - 1

    #
    # robinhood_login: login to the platform `robinhood`.
    #   username: account username used to login to `robinhood`
    #   password: account password used to login to `robinhood`
    #   MFA_code: Robinhood will, at random intervals it seems like, ask you for an AUTH code.
    #             (users can enter this manually via the login screen)
    #   Returns: a dictionary with some data. This data will grow as the user continues to go through
    #            TradeAI as there main platform.
    #
    def robinhood_login(username, password, MFA_code = None):
        webpage_ideals.user_data = {'logged_into': username, 'password_used': password, 'MFA Code': MFA_code}

        try:
            webpage_ideals.robinhood_account = login(username, password, mfa_code = MFA_code)
        except Exception as e:
            return render_template('login.html', err_msg = True, err = 'Username or password was incorrect.')
        
        # lba - linked bank account
        lba_info = get_linked_bank_accounts()

        webpage_ideals.user_data['owner_info'] = {'account_owner': lba_info[0]['bank_account_holder_name']}
        webpage_ideals.user_data['withdrawal_limit'] = {'limit': lba_info[0]['withdrawal_limit']}
        webpage_ideals.user_data['type'] = {'banking_type': lba_info[0]['bank_account_type']}
        webpage_ideals.user_data['User Stock Holdings'] = dict(build_holdings())

        # Change routing number to an array and make the account number a string
        routing = list(lba_info[0]['bank_routing_number'])
        acct_number = str(lba_info[0]['bank_account_number'])

        # Hide first 5 digits of routing, then make it a string
        for i in range(len(routing)-4):
            routing[i] = '*'
        routing = ''.join(routing)
    
        webpage_ideals.user_data['bank_info'] = {'routing_number': routing, 'account_number': acct_number}
        return webpage_ideals.user_data

    #
    # attempt_forced_login: attempt to login with saved cookies, if there are any
    #   Error: redirects to `login.html`, success redirects to the account
    #
    def attempt_forced_login(platform, msg = None, msg_2 = None):

        try:
            data = auto_login(request.cookies.get('username'), request.cookies.get('password'), None)
            
            platform = request.cookies.get('for')
            if platform != platform_being_used:
                return render_template('login.html', err_msg=True, err=f'You have already logged in with the platform {platform}.', err_msg2 = True, err2 = f'Logging into {webpage_ideals.platform_being_used} will erase stored data for {platform}.', platform = webpage_ideals.platform_being_used)
            
            webpage_ideals.greeting = 'Welcome Back'

            del webpage_ideals.user_data['password_used']
            return redirect(url_for('account'))
        except:
            pass
    
        return render_template('login.html', err_msg=False, platform = webpage_ideals.platform_being_used)
    
    #
    # attempt_log_back_in: attempt to log back into the account previously used, if possible
    #   Error: redirects to `login.html`
    #
    def attempt_log_back_in(suspected_platform):
        if webpage_ideals.has_logged_out == False:
            webpage_ideals.platform_being_used = request.cookies.get('for')

            if webpage_ideals.platform_being_used is not None:
                if webpage_ideals.platform_being_used != suspected_platform:
                    return render_template('login.html', err_msg=True, err=f'You have already logged in with the platform {webpage_ideals.platform_being_used}.', err_msg2 = True, err2 = f'Logging into {suspected_platform} will erase stored data for {webpage_ideals.platform_being_used}.', platform = suspected_platform)

                if suspected_platform == 'Robinhood':
                    webpage_ideals.user_data = webpage_ideals.robinhood_login(request.cookies.get('username'), request.cookies.get('password'))
                    webpage_ideals.greeting = 'Welcome Back'
                    return redirect(url_for('account'))

                if suspected_platform == 'Alpaca':
                    # TODO: Get a login going for alpaca
                    # TODO: I don't think alpaca has an API function that logs the user into there account, rather they use keys/secret keys
                    #       so this is where TradeAI will host users to create an account for the website
                    pass
                return None
            return None
        return None
    
    def attempt_login(platform):

        if webpage_ideals.attempt_log_back_in(platform) is None: return False

        return True

class webpage:

    def __init__(self):

        self.app = webpage_ideals.flask_app

        # Host for flask web application
        self.host = '0.0.0.0'
    
    def udpate_server_info(self):
        webpage_ideals.update_server_running_data()

    """
        WEBPAGE RELATED FUNCTIONALITY
    """
    @webpage_ideals.flask_app.route('/')
    def home():

        # Before we do anything, we need to see the last set of server data
        # Depending on some values, we will be able to evaluate whether or not the server crashed
        webpage_ideals.server_running_data = json.loads(open('server_run_data.json', 'r').read())
        webpage_ideals.adapt_last_server_run_data()

        all_posts = webpage_ideals.all_post_requests

        webpage_ideals.update_server_running_data()

        if not webpage_ideals.has_logged_out:
            if not webpage_ideals.keep_logged_in:
                webpage_ideals.indirect_error_data = {'Error': 'You have been logged out.', 'Advice': 'Check `Keep Me Logged In` to stay logged in.'}
                
                res = make_response(render_template('home.html', login_data = False, data = all_posts if len(all_posts) > 0 else {'Data': 'None'}))
                
                res.set_cookie('username', '', max_age=0)
                res.set_cookie('password', '', max_age=0)
                res.set_cookie('for', '', max_age=0)
                
                webpage_ideals.has_logged_out = True
                webpage_ideals.update_server_running_data()
                return res

        return render_template('home.html', login_data = False, data = all_posts if len(all_posts) > 0 else {'Data': 'None'})
    
    @webpage_ideals.flask_app.route('/login_robinhood')
    def login_robinhood():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('login_robinhood'))

        webpage_ideals.last_page = 'robinhood_login'
        
        if not webpage_ideals.has_logged_out:
            if webpage_ideals.attempt_log_back_in('Robinhood') != None: 
                return webpage_ideals.attempt_log_back_in('Robinhood')
        else: webpage_ideals.greeting = 'Howdy'

        webpage_ideals.platform_being_used = 'Robinhood'
        
        # Make sure there is no error data
        webpage_ideals.error_data = None

        webpage_ideals.update_server_running_data()

        if webpage_ideals.has_logged_out:
            if webpage_ideals.indirect_error_data is not None:
                return render_template('login.html', err_msg=True, err=webpage_ideals.indirect_error_data['Error'], err_msg2=True if webpage_ideals.indirect_error_data['Advice'] is not None else False, err2 = webpage_ideals.indirect_error_data['Advice'] if webpage_ideals.indirect_error_data['Advice'] is not None else '')
            return render_template('login.html', err_msg=False, platform = webpage_ideals.platform_being_used)
        
        return webpage_ideals.attempt_forced_login('Robinhood')
    
    @webpage_ideals.flask_app.route('/login_alpaca')
    def login_alpaca():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            
        webpage_ideals.last_page = 'alpaca_login'

        if webpage_ideals.attempt_log_back_in('Alpaca') != None: return webpage_ideals.attempt_log_back_in('Alpaca')

        webpage_ideals.platform_being_used = 'Alpaca'

        # Make sure there is no error data
        webpage_ideals.error_data = None

        webpage_ideals.update_server_running_data()

        # TODO: Add support for indirect error data

        if webpage_ideals.has_logged_out:
            return render_template('login.html', err_msg=False, platform = webpage_ideals.platform_being_used)
        
        return webpage_ideals.attempt_forced_login(webpage_ideals.platform_being_used)

    @webpage_ideals.flask_app.route('/login', methods = ['POST', 'GET'])
    def deal_with_login():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('home'))
            
            if webpage_ideals.attempt_log_back_in(webpage_ideals.platform_being_used) != None: 
                return webpage_ideals.attempt_log_back_in(webpage_ideals.platform_being_used)

        webpage_ideals.last_page = 'login_redirect'

        # Make sure there is no error data as well as no indirect error data
        webpage_ideals.error_data = None
        webpage_ideals.indirect_error_data = None

        webpage_ideals.update_server_running_data()

        if request.method == 'POST':

            webpage_ideals.keep_logged_in = request.form.get('keepLoggedIn')
            
            username_gotten = request.form['username']
            password_gotten = request.form['passw']
            MFA_code = request.form['MFACode']

            if password_gotten == '' and username_gotten == '':
                return render_template('login_robinhood.html', err_msg=True, err="Both username and password left blank")
            if username_gotten == '':
                return render_template('login_robinhood.html', err_msg=True, err="Username was left empty")
            if password_gotten == '':
                return render_template('login_robinhood.html', err_msg=True, err='Password was left empty')
            
            if webpage_ideals.platform_being_used is None:
                webpage_ideals.platform_being_used = request.cookies.get('for')

                if webpage_ideals.platform_being_used is None:
                    return render_template('login.html', err_msg=True, err='Something went wrong, please try again')

            if webpage_ideals.platform_being_used == 'Robinhood':
                webpage_ideals.user_data = webpage_ideals.robinhood_login(username_gotten, password_gotten, MFA_code)

                webpage_ideals.has_logged_out = False
                webpage_ideals.has_logged_in = True
                return redirect(url_for('account'))
        else:
            return webpage_ideals.attempt_forced_login()
    
    @webpage_ideals.flask_app.route('/account', methods = ['POST', 'GET'])
    def account():

        if request.cookies.get('date') != None:
            if request.cookies.get('date') != webpage_ideals.date:
                if webpage_ideals.has_logged_in is True:
                    webpage_ideals.has_logged_in = False
                    webpage_ideals.has_logged_out = True
                
                #return redirect(url_for('home'))

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('home'))

            if webpage_ideals.server_running_data['Last Page'] == f'{webpage_ideals.server_running_data["Platform Used"]}_account':
                webpage_ideals.greeting = 'Welcome Back'

        webpage_ideals.last_page = f'{webpage_ideals.platform_being_used}_account'

        print(json.dumps(get_all_stock_orders(), indent=2))

        # Make sure there is no error data as well as no indirect error data
        webpage_ideals.error_data = None
        webpage_ideals.indirect_error_data = None

        # Update server data
        webpage_ideals.update_server_running_data()

        if request.method == 'POST':
            pass
        
        if webpage_ideals.user_data is None:
            try:
                return redirect(url_for('deal_with_login'))
            except:
                webpage_ideals.error_data = {'Error': 'An unknown error occurred. Try again later.'}
                return redirect(url_for('error'))
        
        if webpage_ideals.has_just_added_cash:
            res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, has_just_added_cash = webpage_ideals.has_just_added_cash, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
        else:
            res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, has_just_added_cash = webpage_ideals.has_just_added_cash, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
        res.set_cookie('username', value = webpage_ideals.user_data['logged_into'])
        res.set_cookie('password', value = webpage_ideals.user_data['password_used'])

        res.set_cookie('for', value = webpage_ideals.platform_being_used)
        res.set_cookie('date', value = webpage_ideals.date)
        if webpage_ideals.user_data['MFA Code'] is None:
            res.set_cookie('mfa_code', value='x', max_age = 0)
        else:
            res.set_cookie('mfa_code', value = webpage_ideals.user_data['MFA Code'])
        
        webpage_ideals.update_server_running_data()

        return res
    
    @webpage_ideals.flask_app.route('/account_action_add_cash', methods = ['POST', 'GET'])
    def account_action_add_cash():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('home'))

        #print(deposit_funds_to_robinhood_account('https://connect.auburnstatebank.com/AuburnStateBankOnline', 2))

        #print(json.dumps(get_bank_account_info(), indent=2))

        webpage_ideals.has_just_added_cash = False

        # Make sure there is no already-existing add cash data
        if not webpage_ideals.stock_colors == []:
            webpage_ideals.stock_colors = []
            webpage_ideals.stock_symbols = []
            webpage_ideals.price_colors = []
            webpage_ideals.stock_stats = []
            webpage_ideals.users_personal_share_info = []
            webpage_ideals.stock_prices = []
        
        webpage_ideals.update_server_running_data()

        webpage_ideals.last_page = 'account_action_add_cash'
        
        if request.method == 'POST':
            
            if webpage_ideals.add_cash_submit_button_clicked:

                try:
                    webpage_ideals.cash_amount_to_deposit = int(request.form['cashAmmount'])
                    webpage_ideals.stocks_cash_will_be_used_on = request.form['stocks'].split(',')
                except:
                    webpage_ideals.add_cash_submit_button_clicked = False

                    res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, add_cash_button_clicked = True,  personal=webpage_ideals.users_personal_share_info, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
                    return res

                # TODO: Add a feature that enables the user to specify what they consider a decent gain and a decently bad loss
                #       This way we know what color to highlight the stock depending on its loss/gain

                # Get stock prices
                for i in webpage_ideals.stocks_cash_will_be_used_on:
                    msft = yf.Ticker(i)
                    webpage_ideals.stock_prices.append(msft.info['previousClose'])

                    if i in webpage_ideals.user_data['User Stock Holdings']:
                        webpage_ideals.users_personal_share_info.append(f'{"{:.2f}".format(float(webpage_ideals.user_data["User Stock Holdings"][i]["equity_change"]))}')
                    else:
                        webpage_ideals.users_personal_share_info.append('N/A')

                    if msft.info['previousClose'] < msft.info['open']:
                        if msft.info['open'] - msft.info['previousClose'] < 1:
                            webpage_ideals.stock_colors.append('background-color: yellow;padding-left: 4px; padding-right: 4px')
                        elif msft.info['open'] - msft.info['previousClose'] > 1 and msft.info['open'] - msft.info['previousClose'] < 4:
                            webpage_ideals.stock_colors.append('background-color: #BC544B;padding-left: 4px; padding-right: 4px')
                        else:
                            webpage_ideals.stock_colors.append('background-color: red;padding-left: 4px; padding-right: 4px')
                        webpage_ideals.stock_stats.append(f'- {"{:.2f}".format(msft.info["open"] - msft.info["previousClose"])}')
                        webpage_ideals.stock_symbols.append('✗')
                    if msft.info['previousClose'] > msft.info['open']:
                        if msft.info['previousClose'] - msft.info['open'] >= float(request.form['gains']):
                            webpage_ideals.stock_symbols.append('✓')
                        else:
                            webpage_ideals.stock_symbols.append('✗')
                            
                    if msft.info['previousClose'] - msft.info['open'] < 1:
                        webpage_ideals.stock_colors.append('background-color: orange;padding-left: 4px; padding-right: 4px')
                    elif msft.info['previousClose'] - msft.info['open'] < 2:
                        webpage_ideals.stock_colors.append('background-color: light-green;padding-left: 4px; padding-right: 4px')
                    else:
                        webpage_ideals.stock_colors.append('background-color: green;padding-left: 4px; padding-right: 4px')
                    webpage_ideals.stock_stats.append(f'+ {"{:.2f}".format(msft.info["previousClose"] - msft.info["open"])}')
                    
                format_style = 'font-size: 14px'
                format_style2 = '"font-size: 14px; margin-left: 35px;"'
                class_name = 'show-buy-info-small'
                if len(webpage_ideals.stocks_cash_will_be_used_on) > 6:
                    format_style = 'font-size: 8px'
                    format_style2 = 'font-size: 8px; margin-left: 10px'
                    class_name = 'show-buy-info-medium' if len(webpage_ideals.stocks_cash_will_be_used_on) > 6 and len(webpage_ideals.stocks_cash_will_be_used_on) < 10 else 'show-buy-info-large'

                res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, personal=webpage_ideals.users_personal_share_info, symbol=webpage_ideals.stock_symbols, stats=webpage_ideals.stock_stats, color=webpage_ideals.stock_colors, class_name=class_name, style1=format_style, style2=format_style2, has_just_added_cash = True, cash = webpage_ideals.cash_amount_to_deposit, on_stocks=webpage_ideals.stocks_cash_will_be_used_on, prices=webpage_ideals.stock_prices, amnt_of_stocks=len(webpage_ideals.stocks_cash_will_be_used_on), add_cash_button_clicked = False, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))

                webpage_ideals.add_cash_submit_button_clicked = False
                webpage_ideals.has_just_added_cash = True
                return res
            else:
                webpage_ideals.add_cash_submit_button_clicked = True

                res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, add_cash_button_clicked = True,  personal=webpage_ideals.users_personal_share_info, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
                return res
        else:
            if webpage_ideals.add_cash_submit_button_clicked:
                res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, personal=users_personal_info, symbol=symbol, stats=stats, color=colors, class_name=class_name, style1=format_style, style2=format_style2, confirming = True, cash = webpage_ideals.cash_amount_to_deposit, on_stocks=webpage_ideals.stocks_cash_will_be_used_on, prices=webpage_ideals.stock_prices, amnt_of_stocks=len(webpage_ideals.stocks_cash_will_be_used_on), add_cash_button_clicked = False, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))

                return res

            res = make_response(render_template('account.html', has_entries = webpage_ideals.has_entries, add_cash_button_clicked = True,  personal=webpage_ideals.users_personal_share_info, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
            return res

    @webpage_ideals.flask_app.route('/account_action_takeout_cash', methods = ['POST', 'GET'])
    def account_action_takeout_cash():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('home'))
        
        webpage_ideals.last_page = 'account_action_takeout_cash'

        webpage_ideals.update_server_running_data()

        return redirect(url_for('account'))
    
    @webpage_ideals.flask_app.route('/new_custom_data', methods = ['POST', 'GET'])
    def new_custom_data():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                if not webpage_ideals.has_logged_in:
                    return redirect(url_for('home'))
        
        webpage_ideals.last_page = 'new_custom_data'

        if request.method == 'POST':

            if webpage_ideals.add_new_data_button_clicked is True:
                try:
                    entry_name = request.form['entryName']
                    stocks = request.form['stocks'].split(',')
                    for_accnt = request.form['forAccount'].lower()
                    init_prices = request.form['initPrices'].split(',')
                    TGOL = request.form['TGOL'].split(',')
                    TOT_GOL = request.form['TOTGOL'].split(',')

                    if for_accnt not in webpage_ideals.robinhood_accounts:
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'The account "{for_accnt}" is not supported by Robinhood', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    
                    if len(stocks) < len(init_prices):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'Too many initial prices, only gave {len(stocks)} stocks ({", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    if len(init_prices) < len(stocks):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'There are {len(stocks)-len(init_prices)} more initial prices needed (you gave {len(stocks)} stocks - {", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    if len(stocks) < len(TGOL):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'Too many TGOLs(Todays Gains Or Losses). Only gave {len(stocks)} stocks ({", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    if len(TGOL) < len(stocks):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'There are {len(stocks)-len(TGOL)} more TGOLs needed (you gave {len(stocks)} stocks - {", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    if len(stocks) < len(TOT_GOL):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'Too many TOTGOL(Total Gains Or Losses). Only gave {len(stocks)} stocks ({", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    if len(TOT_GOL) < len(stocks):
                        return render_template('account.html', has_entries = webpage_ideals.has_entries, submit_error = True, sub_err_msg = f'There are {len(stocks)-len(TOT_GOL)} more TOTGOLs needed (you gave {len(stocks)} stocks - {", ".join(stocks)})', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data)
                    
                    # Make sure there are existing stocks
                    for i in stocks:
                        if for_accnt == 'roth ira':
                            if not i in webpage_ideals.roth_ira_stocks: webpage_ideals.roth_ira_stocks.append(i)
                        if for_accnt == 'traditional ira':
                            if not i in webpage_ideals.norm_ira_stocks: webpage_ideals.norm_ira_stocks.append(i)
                        if for_accnt == 'traditional':
                            if not i in webpage_ideals.trad_stocks: webpage_ideals.trad_stocks.append(i)
                    
                    json_ = {
                        'Entry': entry_name,
                        'Date': webpage_ideals.date,
                        'Account': for_accnt,
                        'For Stocks': stocks,
                        'Initial Prices': [float(i) for i in init_prices],
                        'Todays GOL': [float(i) for i in TGOL],
                        'Total GOL': [float(i) for i in TOT_GOL]
                    }
                    webpage_ideals.all_submitted_data['Entries'].append(json_)
                    webpage_ideals.server_running_data['Created Data'].append(json_)
                    webpage_ideals.update_server_running_data()

                    if not webpage_ideals.has_entries:
                        webpage_ideals.has_entries = True
                    
                    webpage_ideals.add_new_data_button_clicked = False
                    #res = make_response(render_template('account.html', has_entries = True if len(webpage_ideals.all_submitted_data['Entries']) > 0 else False, personal=webpage_ideals.users_personal_share_info, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
                    return redirect(url_for('account'))
                except Exception as e:
                    webpage_ideals.add_new_data_button_clicked = True
                    
                    res = make_response(render_template('account.html', is_creating_new_data = True, has_entries=webpage_ideals.has_entries, personal=webpage_ideals.users_personal_share_info, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))
                    return res
            
        
        webpage_ideals.add_new_data_button_clicked = True
        res = make_response(render_template('account.html', is_creating_new_data = True, greeting = webpage_ideals.greeting, user = webpage_ideals.user_data['owner_info']['account_owner'], platform = webpage_ideals.platform_being_used, login_data = True, data = webpage_ideals.user_data))

        return res
    
    @webpage_ideals.flask_app.route('/see_existing_data', methods = ['POST', 'GET'])
    def see_existing_data():

        if os.path.isfile('server_run_data.json') and webpage_ideals.server_running_data['User Data'] is None:
            webpage_ideals.adapt_last_server_run_data()
            if webpage_ideals.attempt_login(webpage_ideals.server_running_data['Platform Used']):
                webpage_ideals.attempt_log_back_in(webpage_ideals.server_running_data['Platform Used'])
            else:
                return redirect(url_for('home'))
        
        webpage_ideals.last_page = 'see_existing_data'

        if request.method == 'POST':
            return render_template('account.html', look_at_entries = True, entries = webpage_ideals.all_submitted_data)
        
        return 'NOT POST'
    
    @webpage_ideals.flask_app.route('/logout', methods = ['GET', 'POST'])
    def logout_account():

        # Make sure there is no error data as well as no indirect error data
        webpage_ideals.error_data = None
        webpage_ideals.indirect_error_data = None

        webpage_ideals.has_logged_out = True

        webpage_ideals.update_server_running_data()

        res = make_response(redirect(url_for('home')))#render_template('home.html', login_data = False, data = all_posts if len(all_posts) > 0 else {'Data': 'None'}))
        webpage_ideals.user_data['account_info'] = {
            'username': request.cookies.get('username'),
            'password': request.cookies.get('password'),
            'platform': request.cookies.get('for')
        }
        with open('data.json', 'w') as file:
            file.write(json.dumps(webpage_ideals.user_data, indent=2))
            file.flush()
            file.close()
        res.set_cookie('username', '', max_age=0)
        res.set_cookie('password', '', max_age=0)
        res.set_cookie('for', '', max_age=0)

        logout()

        # TODO: After "deleting" the cookies, we should store the information the cookies held in a database for possible futuer reference
        #       The only reason this would happen is because the structure, as of right now, is only allowing a user to use a single platform at a time
        # TODO: Make it to where the user can use as many platforms as they want at once

        return res
    
    """
        END WEBPAGE RELATED FUNCTIONALITY
    """
    
    def launch(self, use_host = True):
        if use_host:
            self.app.run(debug=True, host=self.host)
        else:
            self.app.run(debug=True)