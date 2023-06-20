from flask import Flask,redirect,url_for,request,render_template,flash,session
import mysql.connector
from key import secret_key,salt
from itsdangerous import URLSafeTimedSerializer
from stoken import token
from cmail import sendmail
import os

app = Flask(__name__)
app.secret_key=secret_key
app.config['SESSION_TYPE']='filesystem'
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')

with mysql.connector.connect(host=host,user=user,password=password,port=port,db=db) as conn:
    cursor=conn.cursor(buffered=True)
    cursor.execute("create table if not exists users(username varchar(20) primary key, email varchar(60) unique not null, password varchar(30))")
    cursor.execute("create table if not exists usercalcount(cid int primary key auto_increment, weight int, height int, age int, gender varchar(10), bmr float, food_cal float, final_result float, username varchar(20), cal_date timestamp default current_timestamp, foreign key(username) references users(username))")
    cursor.close()

mydb=mysql.connector.connect(host=host,user=user,password=password,db=db)

@app.route('/')
def index():
    return render_template('title.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from users where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==1:
            session['user']=username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/registration',methods=['GET','POST'])
def registration():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from users where username=%s',[username])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from users where email=%s',[email])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('Username is already in use')
            return render_template('registration.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('registration.html')
        data={'username':username,'password':password,'email':email}
        subject='Email Confirmation'
        body=f"Welcome to our Calorie Counter Application {username}!!!\n\nThanks for registering on our application....\nClick on this link to confirm your registration - {url_for('confirm',token=token(data),_external=True)}\n\n\n\nWith Regards,\nCalorie Counter Team"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('registration'))
    return render_template('registration.html')

@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception:
        flash('Link expired register again')
        return redirect(url_for('registration'))
    else:
        cursor=mydb.cursor(buffered=True)
        username=data['username']
        cursor.execute('select count(*) from users where username=%s',[username])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('login'))
        else:
            cursor.execute('insert into users values(%s,%s,%s)',[data['username'],data['email'],data['password']])
            mydb.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('login'))
        
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        flash('You are successfully logged out')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    if session.get('user'):
        return render_template('about.html')
    else:
        return redirect(url_for('login'))
    

@app.route('/home')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/calorie', methods=["GET","POST"])
def calorie():
    if session.get('user'):
        if request.method == 'POST':
            try:
                weight = int(request.form['weight'])
                height = int(request.form['height'])
                age = int(request.form['age'])
                gender = request.form['gender']
                if gender == 'male':    
                    bmr = (10*weight)+(6.25*height)-(5*age)+5
                else:
                    bmr = (10*weight)+(6.25*height)-(5*age)-161
                item = []
                quantity = []
                item.append(request.form['item1'])
                item.append(request.form['item2'])
                item.append(request.form['item3'])
                item.append(request.form['item4'])
                item.append(request.form['item5'])
                item.append(request.form['item6'])
                item.append(request.form['item7'])
                item.append(request.form['item8'])
                quantity.append(float(request.form['quantity1']))
                quantity.append(float(request.form['quantity2']))
                quantity.append(float(request.form['quantity3']))
                quantity.append(float(request.form['quantity4']))
                quantity.append(float(request.form['quantity5']))
                quantity.append(float(request.form['quantity6']))
                quantity.append(float(request.form['quantity7']))
                quantity.append(float(request.form['quantity8']))
                cursor=mydb.cursor(buffered=True)
                username=session.get('user')
                calories = {'absinthe': 3.48, 'acai': 0.7, 'acai juice': 0.58, 'ace drink': 0.44, 'acerola': 0.32, 'acorn': 3.87, 'activia': 0.74, 'activia lemon': 1.0, 'activia strawberry': 0.97, 'advocaat': 2.83, 'after eight': 4.52, 'agar-agar': 0.26, 'agave syrup': 3.1, 'airheads': 3.75, 'ajvar': 0.18, 'ale': 0.35, 'alfalfa sprouts': 0.23, 'all purpose flour': 3.64, 'all-blue potatoes': 0.61, 'alligator': 2.32, 'alligator meat': 2.32, 'almond butter': 6.14, 'almond extract': 2.58, 'almond milk': 0.17, 'almond oil': 8.82, 'almond roca': 5.71, 'almonds': 5.75, 'aloe vera': 0.44, 'aloe vera yogurt': 0.85, 'alphabet soup': 0.25, 'altbier': 0.43, 'amaranth': 3.71, 'amaretto': 3.1, 'american cheese': 1.48, 'anchovy': 1.31, 'andouille': 2.32, 'angel delight': 4.51, 'angel food cake': 2.58, 'animal crackers': 4.46, 'anise': 3.37, 'anise seed': 3.37, 'antelope meat': 1.5, 'apple': 0.52, 'apple butter': 1.73, 'apple cake': 2.52, 'apple cobbler': 1.98, 'apple crisp': 1.56, 'apple crumble': 1.56, 'apple juice': 0.46, 'apple pie': 2.37, 'apple pie filling': 1.0, 'apple spritzer': 0.24, 'apple strudel': 2.74, 'apple turnover': 3.48, 'applejack': 2.33, 'applesauce': 0.62, 'applesauce cake': 3.58, 'applewood': 4.1, 'apricot': 0.48, 'apricot jam': 2.5, 'apricot kernel oil': 8.89, 'apricot nectar': 0.56, 'arbyâ€™s grand turkey club': 2.1, 'arbyâ€™s reuben': 2.08, 'arbyâ€™s roast beef classic': 2.34, 'arbyâ€™s roast beef max': 2.34, 'argan oil': 8.96, 'arrabiata sauce': 0.36, 'arrowroot': 0.65, 'artichoke': 0.47, 'arugula': 0.25, 'asiago cheese': 3.92, 'asian pear': 0.42, 'asparagus': 0.2, 'asti': 1.38, 'aubergine': 0.25, 'avocado': 1.6, 'avocado oil': 8.57, 'ayran': 0.42, 'azuki bean': 1.24, 'babassu oil': 8.84, 'baby back ribs': 2.59, 'baby ruth': 4.69, 'babybel': 3.33, 'bacon': 4.07, 'bacon and eggs': 2.52, 'bagel': 2.57, 'baguette': 2.74, 'baileyâ€™s irish cream': 3.27, 'baileys': 3.27, 'baked alaska': 2.47, 'baked beans': 0.94, 'baked chicken': 1.64, 'baked ham': 3.43, 'baked potato': 0.93, 'bakewell tart': 4.3, 'baking powder': 0.53, 'baking soda': 0.0, 'balsamic vinaigrette dressing': 2.9, 'balsamic vinegar': 0.88, 'bamboo shoots': 0.27, 'banana': 0.89, 'banana bread': 3.26, 'banana juice': 0.5, 'banana nut bread': 3.26, 'banoffee pie': 3.95, 'barbecue sauce': 1.5, 'barley': 3.54, 'barley groats': 1.0, 'barqâ€™s': 0.46, 'basil': 2.33, 'baskin-robbins': 2.39, 'bass': 0.45, 'bbq chicken pizza': 2.34, 'bbq pizza': 2.24, 'bbq rib': 2.12, 'bbq ribs': 2.55, 'bean burrito': 2.0, 'bean curd': 0.76, 'bean sprouts': 0.3, 'bean stew': 1.33, 'bear meat': 2.59, 'beaver meat': 2.12, 'bechamel sauce': 2.25, 'beckâ€™s': 0.39, 'beechnut': 5.76, 'beef': 1.71, 'beef bouillon': 0.03, 'beef brain': 1.96, 'beef brisket': 1.37, 'beef fillet': 1.89, 'beef goulash': 1.23, 'beef heart': 1.65, 'beef jerky': 4.1, 'beef kidney': 1.58, 'beef liver': 1.91, 'beef lung': 1.2, 'beef melt': 2.71, 'beef minute steak': 1.33, 'beef neck': 2.13, 'beef noodle soup': 0.34, 'beef pancreas': 2.71, 'beef patty': 2.47, 'beef pizza': 3.04, 'beef prime rib': 4.04, 'beef ribs': 1.96, 'beef salami': 3.75, 'beef sirloin': 1.82, 'beef soup': 0.33, 'beef stew': 0.95, 'beef suet': 8.54, 'beef tallow': 9.02, 'beef tenderloin': 2.18, 'beef thymus': 3.19, 'beef tongue': 2.84, 'beef tripe': 0.94, 'beer': 0.43, 'beer bread': 2.27, 'beetroot': 0.43, 'bell pepper': 0.2, 'ben and jerryâ€™s': 2.28, 'bengal gram': 3.64, 'bergkã¤se': 4.18, 'bernaise sauce': 4.14, 'bianca pizza': 2.46, 'big nâ€™ tasty': 2.23, 'bircher muesli yogurt': 1.09, 'birthday cake': 4.65, 'biryani': 1.76, 'biscuit': 2.69, 'bison': 1.71, 'bison meat': 1.71, 'bison sirloin': 1.71, 'bitter lemon': 0.34, 'black and white cookie': 3.81, 'black beans': 3.41, 'black bread': 2.5, 'black chickpeas': 3.64, 'black forest cake': 2.64, 'black gram': 3.41, 'black olives': 1.15, 'black pepper': 2.51, 'black pudding': 3.79, 'black rice': 3.23, 'black sesame seeds': 5.73, 'blackberries': 0.43, 'blackberry jam': 2.5, 'blackberry juice': 0.48, 'blackcurrant jam': 2.5, 'blood oranges': 0.5, 'blood sausage': 3.79, 'blt': 2.47, 'blue cheese': 3.53, 'blue cheese dressing': 5.33, 'blue curacao': 2.43, 'blue moon': 0.48, 'blueberries': 0.57, 'blueberry cobbler': 2.34, 'blueberry jam': 2.5, 'blueberry muffin': 3.77, 'blueberry pie': 2.32, 'blueberry yogurt': 1.05, 'bluefish': 1.59, 'bock beer': 0.5, 'bockwurst': 3.01, 'boiled ham': 1.26, 'boiled potatoes': 0.87, 'bologna': 2.47, 'bolognese': 1.06, 'boudin': 1.94, 'bouillon': 0.16, 'bourbon': 2.33, 'boysenberry juice': 0.54, 'bran flakes': 3.56, 'bran muffins': 2.7, 'brandy': 2.13, 'bratwurst': 3.33, 'brawn': 3.09, 'brazil nuts': 6.56, 'bread flour': 3.61, 'bread pudding': 1.53, 'breadfruit': 1.03, 'breadsticks': 4.0, 'breakfast sausage links': 3.39, 'bream': 1.35, 'bresaola': 1.78, 'brie': 3.34, 'brioche': 3.46, 'brittle': 5.92, 'broccoli': 0.34, 'broccoli cheese soup': 0.87, 'broccoli soup': 0.87, 'broth': 1.0, 'brown bread': 2.46, 'brown lentil': 3.53, 'brown rice': 3.88, 'brown sugar': 3.95, 'brownies': 4.05, 'brussels sprouts': 0.43, 'buckler (n.a.)': 0.21, 'buckwheat': 3.43, 'buckwheat groats': 3.46, 'bud ice': 0.35, 'bud light': 0.29, 'bud light chelada': 0.43, 'bud light lime': 0.34, 'bud select': 0.28, 'bud select 55': 0.15, 'budweiser': 0.41, 'budweiser chelada': 0.52, 'buffalo': 1.31, 'buffalo chicken pizza': 2.52, 'buffalo meat': 1.31, 'bun': 3.16, 'bundt cake': 3.7, 'burger king angry whopper': 2.55, 'burger king double whopper': 2.39, 'burger king double whopper with cheese': 2.49, 'burger king original chicken sandwich': 3.01, 'burger king premium alaskan fish sandwich': 2.59, 'burger king triple whopper': 2.69, 'burger king whopper': 2.31, 'burger king whopper jr.': 2.34, 'burger king whopper with cheese': 2.41, 'burrito': 1.63, 'busch': 0.37, 'busch light': 0.27, 'busch n.a.': 0.17, 'butter': 7.2, 'butter cheese': 3.88, 'butter chicken': 1.4, 'butter pecan ice cream': 2.48, 'butterfinger': 4.5, 'butterfish': 1.87, 'buttermilk': 0.62, 'buttermilk pancakes': 2.38, 'buttermilk pie': 3.8, 'buttermilk ranch dressing': 5.33, 'butternut': 6.12, 'butterscotch chips': 5.39, 'cabbage': 0.25, 'cabbage soup': 0.28, 'cabernet sauvignon': 0.77, 'caesar dressing': 4.29, 'cake flour': 3.62, 'abrese pizza': 2.35, 'amari': 1.75, 'f brain': 1.36, 'f liver': 1.92, 'f lung': 1.04, 'f melt': 2.56, 'ifornia roll': 0.93, 'zone': 2.31, 'camembert': 3.0, 'canada dry ginger ale': 0.41, 'canadian whiskey': 2.16, 'canadian-style bacon': 1.07, 'candied orange peel': 0.97, 'candy apple': 1.52, 'candy cane': 4.23, 'candy canes': 4.23, 'candy corn': 3.6, 'candy floss': 4.0, 'cane sugar': 3.87, 'canned apricots': 0.48, 'canned blackberries': 0.92, 'canned blueberries': 0.88, 'canned cherries': 0.54, 'canned cranberries': 1.78, 'canned crushed pineapple': 0.53, 'canned figs': 1.07, 'canned fruit cocktail': 0.81, 'canned fruit salad': 0.5, 'canned gooseberries': 0.73, 'canned grapefruit': 0.37, 'canned grapes': 0.76, 'canned mandarin oranges': 0.71, 'canned mango': 0.65, 'canned mangosteen': 0.73, 'canned mixed fruit': 0.71, 'canned morello cherries': 0.81, 'canned oranges': 0.62, 'canned peaches': 0.54, 'canned pears': 0.35, 'canned pineapple': 0.6, 'canned plums': 0.58, 'canned raspberries': 0.91, 'canned sliced pineapple': 0.53, 'canned sour cherries': 1.14, 'canned strawberries': 0.92, 'canned tangerines': 0.61, 'cannelloni': 1.46, 'cannoli': 2.54, 'canola oil': 8.84, 'cantaloupe': 0.34, 'cantaloupe melon': 0.34, 'capâ€™n crunch': 4.04, 'capellini': 3.53, 'capers': 0.23, 'capicola': 1.1, 'capon': 2.29, 'cappelletti': 1.64, 'capricciosa pizza': 2.6, 'capri-sun': 0.41, 'capsicum': 0.27, 'caramel cake': 4.75, 'caramel popcorn': 3.76, 'caramel squares': 3.67, 'caraway seeds': 3.33, 'cardamom': 3.11, 'caribou': 1.59, 'carlsberg': 0.32, 'carp': 1.62, 'carrot': 0.41, 'carrot cake': 4.08, 'carrot ginger soup': 0.25, 'carrot juice': 0.4, 'carrot soup': 0.25, 'carvel': 2.12, 'casaba melon': 0.28, 'cashew': 5.53, 'cassava': 1.6, 'catalina dressing': 2.82, 'cauliflower': 0.25, 'cava': 0.76, 'caviar': 2.64, 'cayenne pepper': 3.18, 'celebrations': 4.9, 'celery': 0.16, 'cellophane noodles': 3.51, 'chai': 0.0, 'chai tea': 0.0, 'challah': 2.83, 'chambord': 3.48, 'chamomile tea': 0.0, 'champagne': 0.75, 'chapati': 2.4, 'chard': 0.19, 'chardonnay': 0.85, 'chasseur sauce': 0.45, 'cheddar': 4.03, 'cheerios': 3.47, 'cheese fondue': 2.28, 'cheese pastry': 3.74, 'cheese pizza': 2.67, 'cheese platter': 3.57, 'cheese slices': 3.56, 'cheese spread': 2.9, 'cheese tortellini': 2.91, 'cheese whiz': 2.76, 'cheeseburger': 2.63, 'cheesecake': 3.21, 'cheez-itâ€™s': 5.33, 'chenin blanc': 0.8, 'cherimoya': 0.75, 'cherries': 0.5, 'cherry coke': 0.44, 'cherry jam': 2.5, 'cherry juice': 0.45, 'cherry pie': 2.6, 'cherry tomato': 1.0, 'cherry yogurt': 0.97, 'chess pie': 4.11, 'chester': 3.87, 'chestnut': 2.13, 'chex': 3.87, 'chia seeds': 4.86, 'chicken': 2.19, 'chicken bouillon': 0.04, 'chicken breast': 1.63, 'chicken breast fillet': 0.79, 'chicken broth': 0.16, 'chicken caesar salad': 1.27, 'chicken drumstick': 1.85, 'chicken drumsticks': 1.85, 'chicken fajita': 1.47, 'chicken fat': 8.98, 'chicken fried steak': 1.51, 'chicken giblets': 1.58, 'chicken gizzards': 1.46, 'chicken gumbo soup': 0.23, 'chicken heart': 1.85, 'chicken leg': 1.74, 'chicken legs': 1.74, 'chicken liver': 1.67, 'chicken marsala': 0.96, 'chicken mcnuggets': 3.02, 'chicken meat': 1.72, 'chicken noodle soup': 0.25, 'chicken nuggets': 2.96, 'chicken parmesan': 1.1, 'chicken pizza': 2.34, 'chicken pizziola': 1.41, 'chicken pot pie': 2.23, 'chicken salad': 0.81, 'chicken sandwich': 2.41, 'chicken stock': 0.16, 'chicken stomach': 1.48, 'chicken teriyaki sandwich': 1.38, 'chicken thigh': 2.29, 'chicken thighs': 2.29, 'chicken tikka masala': 0.81, 'chicken vegetable soup': 0.31, 'chicken wing': 2.66, 'chicken wings': 3.24, 'chicken with rice soup': 0.24, 'chickpeas': 3.64, 'chicory': 0.72, 'chicory greens': 0.23, 'chicory roots': 0.72, 'chili': 2.82, 'chili bean': 0.97, 'chili con carne': 1.05, 'chili powder': 2.82, 'chili sauce': 1.12, 'chimichanga': 2.32, 'chinese cabbage': 0.16, 'chitterlings': 2.33, 'chive cream cheese': 3.42, 'chives': 0.3, 'chocolate': 5.29, 'chocolate bar': 5.33, 'chocolate cake': 3.89, 'chocolate cheerios': 3.67, 'chocolate chip ice cream': 2.15, 'chocolate chips': 4.93, 'chocolate cream pie': 3.04, 'chocolate ice cream': 2.16, 'chocolate milk': 0.89, 'chocolate milkshake': 1.25, 'chocolate mousse': 2.25, 'chocolate mousse cake': 2.6, 'chocolate mousse pie': 2.6, 'chocolate muffin': 4.2, 'chocolate philadelphia': 2.87, 'chocolate spread': 5.41, 'chocolate sprinkles': 5.0, 'chocolate wine': 2.56, 'chocolate yogurt': 1.28, 'chocos': 3.8, 'chop suey': 1.72, 'chopped ham': 1.8, 'chorizo': 4.55, 'chuck roast': 1.41, 'chuck steak': 1.37, 'ciabatta': 2.71, 'ciao bella': 1.09, 'cider': 0.49, 'cider vinegar': 0.21, 'cilantro': 0.23, 'cinnamon': 2.47, 'cinnamon bun': 4.36, 'cinnamon toast crunch': 4.33, 'clam': 1.48, 'clamato': 0.6, 'clausthaler (n.a.)': 0.26, 'clementine': 0.47, 'cloves': 2.74, 'club mate': 0.3, 'cobb salad': 1.18, 'coca cola': 0.42, 'coco pops': 3.76, 'cocoa krispies': 3.86, 'cocoa pebbles': 3.67, 'cocoa powder': 2.28, 'cocoa puffs': 4.0, 'coconut': 3.54, 'coconut cake': 3.56, 'coconut flakes': 4.56, 'coconut milk': 2.3, 'coconut oil': 8.57, 'coconut water': 0.19, 'cod': 1.05, 'cod liver oil': 10.0, 'coffee': 0.01, 'coffee cake': 3.31, 'coffee creamer': 1.95, 'coffee ice cream': 2.36, 'cognac': 2.35, 'cointreau': 3.2, 'coke': 0.42, 'coke zero': 0.01, 'cola': 0.42, 'colby cheese': 3.94, 'colby-jack cheese': 3.94, 'cold pack cheese': 2.46, 'cold stone creamery': 2.32, 'collard greens': 0.32, 'colt 45': 0.44, 'conchas/mexican sweet bread': 3.53, 'concord grape': 0.71, 'condensed milk': 3.21, 'cooked ham': 1.33, 'cookie crisp': 4.0, 'cookie dough ice cream': 2.0, 'cookies': 4.88, 'coors': 0.42, 'coors light': 0.29, 'coors n.a.': 0.18, 'coriander': 0.23, 'corn': 3.65, 'corn dog': 2.5, 'corn flakes': 3.57, 'corn flour': 3.61, 'corn oil': 8.0, 'corn pops': 3.77, 'corn syrup': 2.81, 'corn waffles': 2.74, 'cornbread': 1.79, 'corned beef': 2.51, 'corned beef hash': 1.64, 'cornish hens': 2.59, 'cornmeal': 3.62, 'cornstarch': 3.81, 'corona': 0.42, 'cottage cheese': 0.98, 'cottage pie': 1.39, 'cotton candy': 6.43, 'cotton seeds': 5.06, 'cottonseed oil': 8.82, 'count chocula': 4.07, 'courgette': 0.17, 'couscous': 3.76, 'couverture': 6.0, 'cracker': 5.02, 'cracklin oat bran': 4.02, 'cranberries': 0.46, 'cranberry apple juice': 0.67, 'cranberry grape juice': 0.71, 'cranberry juice': 0.46, 'crawfish': 0.82, 'crayfish': 0.87, 'cream': 2.42, 'cream cheese': 3.42, 'cream cheese with herbs': 3.42, 'cream of asparagus soup': 0.35, 'cream of broccoli soup': 0.45, 'cream of celery soup': 0.37, 'cream of chicken soup': 0.48, 'cream of mushroom soup': 0.39, 'cream of onion soup': 0.44, 'cream of potato soup': 0.3, 'cream of tartar': 2.58, 'cream of wheat': 3.64, 'cream puff': 3.34, 'cream sauce': 1.8, 'cream yogurt': 1.24, 'creamed spinach': 0.74, 'creamy chicken noodle soup': 0.23, 'creamy yogurt': 0.9, 'creme fraiche': 3.93, 'crepes': 2.24, 'cress': 0.32, 'croissant': 4.06, 'croquettes': 1.27, 'crumb cake': 4.41, 'crumpet': 1.78, 'crunchie mcflurry': 1.74, 'crunchy nut': 6.0, 'crunchy nut cornflakes': 6.0, 'crystal light': 2.63, 'crystallized ginger': 3.35, 'cubed steak': 1.99, 'cucumber': 0.16, 'cucumber juice': 0.1, 'cumberland sausage': 2.5, 'cumin': 3.75, 'cumin seed': 3.75, 'cupcake': 3.05, 'cupcakes': 3.05, 'curd': 0.98, 'curly fries': 3.11, 'currant juice': 0.48, 'currants': 0.56, 'curry': 3.25, 'curry ketchup': 1.24, 'curry sauce': 0.26, 'custard': 1.22, 'custard apple': 1.01, 'custard powder': 3.37, 'dairy milk mcflurry': 1.86, 'dal': 3.3, 'dampfnudel': 2.74, 'dandelion': 0.45, 'danish pastry': 3.74, 'dark beer': 0.46, 'dark rum': 2.16, 'dates': 2.82, 'deep dish pizza': 2.65, 'deep-fried tofu': 2.71, 'deviled eggs': 2.01, 'dextrose': 3.75, 'diet cherry coke': 0.01, 'diet coke': 0.01, 'diet dr. pepper': 0.0, 'diet pepsi': 0.0, 'diet sunkist': 0.0, 'diet yogurt': 0.54, 'dill': 0.43, 'dill weed': 0.43, 'dim sum': 1.93, 'dippin dots': 2.24, 'dominos philly cheese steak pizza': 2.24, 'donut': 4.03, 'donut/doughnut': 4.21, 'dosa': 0.66, 'double cheeseburger': 2.67, 'double rainbow': 2.57, 'doughnut': 4.03, 'dove': 2.13, 'dr. brownâ€™s': 0.53, 'dr. pepper': 0.27, 'dragon fruit': 0.6, 'drambuie': 3.58, 'dried apricots': 2.41, 'dried cranberries': 3.08, 'dried figs': 2.49, 'dried fruit': 2.43, 'dried prunes': 1.07, 'drumsticks': 2.55, 'dry red wine': 0.85, 'duck': 3.37, 'duck breast': 2.01, 'duck egg': 1.85, 'duck liver': 1.36, 'dumpling dough': 1.24, 'dumplings': 1.24, 'durian': 1.47, 'durum wheat semolina': 3.97, 'dutch cheese': 3.93, 'dutch loaf': 2.68, 'edam': 3.57, 'edam cheese': 3.57, 'eel': 2.36, 'egg': 0.97, 'egg cream': 0.94, 'egg nog': 0.88, 'egg noodles': 3.84, 'egg roll': 2.5, 'egg white': 0.13, 'egg yolk': 3.22, 'eggplant': 0.25, 'eggy bread': 1.96, 'elderflower cordial': 0.29, 'emmental': 3.57, 'emmentaler': 3.57, 'empanada': 3.35, 'emu': 1.52, 'enchiladas': 1.68, 'endive': 0.17, 'energy-drink': 0.87, 'english muffin': 2.27, 'esrom (cheese)': 3.22, 'evaporated milk': 1.35, 'evian': 0.0, 'extra-firm tofu': 0.91, 'fairy cakes': 4.4, 'fajita': 1.17, 'falafel': 3.35, 'fanta': 0.39, 'fanta zero': 0.0, 'farfalle': 3.58, 'feijoa': 0.55, 'fennel': 0.31, 'fennel seed': 3.45, 'fenugreek': 3.23, 'ferrero rocher': 5.76, 'feta': 2.64, 'feta cream cheese': 3.42, 'fettuccine': 3.53, 'fiber one': 2.67, 'figs': 0.74, 'filet mignon': 2.07, 'filet-o-fish': 2.82, 'firm tofu': 0.7, 'fish and chips': 1.95, 'fish fingers': 2.9, 'fish sandwich': 2.73, 'fish sticks': 2.9, 'five alive': 0.35, 'flageolet': 0.85, 'flan': 1.45, 'flank steak': 1.94, 'flapjack': 4.86, 'flat iron steak': 1.37, 'flatbread': 3.11, 'flaxseed': 5.34, 'flaxseed oil': 8.84, 'flounder': 0.86, 'flour': 3.64, 'flourless chocolate cake': 5.09, 'focaccia': 2.49, 'fol epi': 3.88, 'fontina': 3.89, 'fortune cookies': 2.14, 'four cheese pizza': 2.21, 'frangelico': 2.38, 'frankfurters': 3.05, 'freekeh': 5.2, 'french cruller': 4.12, 'french dressing': 0.6, 'french fingerling potatoes': 0.82, 'french fries': 3.12, 'french onion soup': 0.23, 'french vanilla ice cream': 2.01, 'fresca': 0.0, 'fresh mozzarella': 2.8, 'fried bean curd': 2.71, 'fried potatoes': 3.12, 'fried rice': 1.86, 'fried shrimp': 2.77, 'friendlyâ€™s': 2.12, 'froot loops': 3.79, 'frosted cheerios': 3.93, 'frosted flakes': 3.67, 'frosted mini-wheats': 3.53, 'frosties': 3.67, 'fructose': 3.68, 'fruit cake': 3.24, 'fruit salad': 0.5, 'fruit yogurt': 0.97, 'fruitopia': 1.1, 'fruity pebbles': 4.0, 'full throttle': 1.1, 'funnel cake': 3.07, 'fusilli': 3.52, 'fuze': 0.2, 'fuze tea': 0.25, 'galia melon': 0.23, 'gamay': 0.78, 'garlic': 1.49, 'garlic bread': 3.5, 'garlic cream cheese': 3.42, 'garlic powder': 3.31, 'garlic salt': 0.0, 'garlic sausage': 1.69, 'gatorade': 0.23, 'gelatin': 3.35, 'genesee cream ale': 0.46, 'german chocolate cake': 3.7, 'ghee': 1.2, 'gherkin': 0.14, 'gin': 2.63, 'ginger': 0.8, 'ginger ale': 0.35, 'ginger beer': 0.42, 'ginger tea': 0.0, 'gingerbread': 3.56, 'ginkgo nuts': 1.82, 'gjetost': 4.66, 'glass noodles': 1.92, 'glenfiddich': 2.3, 'glucose': 2.86, 'glucose syrup': 3.87, 'gluten': 3.7, 'gnocchi': 1.33, 'goa bean': 4.09, 'goat cheese': 3.64, 'goat cheese pizza': 2.19, 'goat milk': 0.69, 'golden grahams': 4.0, 'golden mushroom soup': 0.65, 'goose': 3.05, 'goose fat': 8.98, 'goose liver': 1.33, 'goose meat': 2.38, 'gorgonzola': 3.5, 'gouda': 3.56, 'gouda cheese': 3.56, 'goulash': 10.09, 'gourd': 0.14, 'grand marnier': 2.53, 'granola bars': 4.52, 'granulated sugar': 3.87, 'grape jelly': 2.55, 'grape juice': 0.6, 'grape leaves': 0.93, 'grape seed oil': 8.84, 'grapefruit': 0.42, 'grapefruit juice': 0.46, 'grape-nuts': 3.62, 'grapes': 0.69, 'grated parmesan': 4.31, 'gravy': 0.53, 'greek dressing': 4.67, 'greek yogurt': 0.53, 'green beans': 0.31, 'green gram': 3.47, 'green lentil': 2.57, 'green olives': 1.15, 'green onion': 0.32, 'greengage': 0.41, 'grilled cheese': 3.5, 'grilled cheese sandwich': 2.88, 'grilled chicken salad': 0.88, 'grilled pizza': 2.26, 'grissini': 4.08, 'ground beef': 2.41, 'ground chuck': 2.5, 'ground cinnamon': 2.47, 'ground ginger': 3.35, 'ground pork': 2.63, 'ground round': 2.12, 'grouper': 1.18, 'gruyere': 4.13, 'guava': 0.68, 'guinea-fowl': 1.58, 'guinness': 0.35, 'gumdrops': 3.21, 'gummi bears': 3.16, 'haddock': 0.9, 'hake': 0.71, 'halibut': 1.11, 'halloumi': 3.21, 'ham': 1.45, 'ham and cheese sandwich': 2.41, 'ham sandwich': 2.41, 'ham sausage': 1.64, 'hamburger': 2.54, 'hamburger sauce': 3.83, 'hanuta': 5.41, 'harissa': 0.52, 'havarti': 3.71, 'hawaiian pizza': 1.15, 'hawaiian punch': 0.31, 'hazelnut': 6.28, 'hazelnut oil': 8.89, 'hazelnuts': 6.28, 'head cheese': 1.57, 'healthy choice': 1.25, 'heavy cream': 3.45, 'heineken': 0.35, 'hemp oil': 8.07, 'herring': 2.03, 'herring oil': 9.02, 'hershey kisses': 4.71, 'hi-c': 0.49, 'hickory ham': 1.88, 'hickory nuts': 6.57, 'hog maws': 1.57, 'hoki': 1.21, 'hollandaise sauce': 5.35, 'honey': 3.04, 'honey brown': 0.42, 'honey ham': 1.22, 'honey mustard dressing': 4.64, 'honey nut cheerios': 3.93, 'honey smacks': 3.7, 'honeycomb': 3.97, 'honeydew': 0.36, 'horchata': 0.54, 'horseradish': 0.48, 'hot chocolate': 0.89, 'hot dog': 2.69, 'hot dog buns': 2.79, 'hot dogs': 2.78, 'hot fudge sundae': 1.86, 'hot pepper': 3.18, 'hot sausage': 2.59, 'hummus': 1.77, 'hurricane high gravity': 0.39, 'i can\\â€™t believe it\\â€™s not butter': 3.57, 'ice cream cake': 2.0, 'ice cream sandwich': 2.37, 'ice cream sundae': 1.42, 'ice milk': 1.59, 'ice tea': 0.27, 'iced tea': 0.27, 'instant ramen': 4.36, 'iodized salt': 0.0, 'ipa': 0.51, 'irish whiskey': 2.33, 'italian bmt': 1.83, 'italian bread': 2.71, 'italian cheese': 3.97, 'italian dressing': 2.93, 'italian sausage': 1.49, 'jack danielâ€™s': 1.46, 'jackfruit': 0.95, 'jagermeister': 2.5, 'jaggery': 3.83, 'jalapeno': 0.13, 'jambalaya': 1.0, 'japanese sweet potatoes': 0.87, 'jarlsberg': 3.52, 'jelly': 2.78, 'jelly beans': 3.54, 'jelly belly': 3.54, 'jerky': 4.1, 'jif peanut butter': 5.8, 'jim beam': 2.22, 'jolly ranchers': 3.85, 'jolt cola': 0.44, 'jordan almonds': 4.29, 'jujube': 0.79, 'juniper': 0.45, 'just right': 3.91, 'kahlua': 1.8, 'kale': 0.49, 'kamut': 3.37, 'karamalz': 0.37, 'kashi': 3.77, 'kebab': 2.15, 'kefir': 0.55, 'kelloggs corn flakes': 3.57, 'ketchup': 1.0, 'key lime pie': 3.59, 'keystone ice': 0.4, 'keystone light': 0.29, 'kidney beans': 3.37, 'kielbasa': 3.09, 'king cake': 3.77, 'kipper': 2.17, 'kit kat': 5.21, 'kiwi': 0.61, 'kix': 3.67, 'knackwurst': 3.07, 'koelsch': 0.43, 'kohlrabi': 0.27, 'kombucha': 0.13, 'kool-aid': 0.26, 'krave': 3.72, 'kumara': 0.86, 'kumquat': 0.71, 'labatt': 0.43, 'lactose-free milk': 0.52, 'lacy swiss cheese': 3.21, 'laffy taffy': 3.72, 'lager beer': 0.43, 'lamb': 2.02, 'lamb meat': 2.02, 'land shark': 0.42, 'landjaeger': 3.52, 'lard': 8.98, 'lasagna': 1.32, 'lasagne': 1.32, 'lasagne sheets': 2.71, 'lassi': 0.75, 'latkes': 1.89, 'latte macchiato': 0.57, 'layer cake': 4.02, 'leek': 0.61, 'leerdammer': 2.84, 'leerdammer cheese': 2.84, 'lemon': 0.29, 'lemon cake': 3.52, 'lemon grass': 0.99, 'lemon juice': 0.21, 'lemon meringue pie': 2.68, 'lemon pie filling': 1.43, 'lemonade': 0.5, 'lentil soup': 0.56, 'lentils': 3.53, 'lettuce': 0.15, 'licorice': 3.75, 'life cereal': 3.75, 'lifesavers': 5.0, 'light beer': 0.29, 'lima beans': 0.71, 'lime': 0.3, 'lime juice': 0.21, 'limeade': 1.28, 'lindt chocolate': 5.48, 'ling': 1.09, 'linguica': 2.82, 'linguine': 3.57, 'linseed oil': 8.37, 'liqueur': 2.5, 'liquor': 2.5, 'liquorice': 3.75, 'liver pate': 3.19, 'liverwurst': 3.26, 'lobster': 0.89, 'lobster bisque soup': 1.0, 'lollipop': 3.92, 'lotus seed': 0.89, 'low carb pasta': 2.82, 'lowenbrau': 0.45, 'low-fat yogurt': 0.63, 'lucky charms': 4.06, 'luncheon meat': 1.17, 'lychee': 0.66, 'lychees': 0.66, 'm&mâ€™s': 4.79, 'maasdam cheese': 3.44, 'mac and cheese': 3.7, 'macadamia nuts': 7.18, 'macadamia oil': 8.19, 'macaroni': 3.7, 'macaroni and cheese': 3.7, 'mackerel': 2.62, 'madeira cake': 3.94, 'maggi': 1.04, 'magnolia': 2.3, 'magnum': 3.0, 'magnum almond': 3.15, 'magnum double caramel': 3.55, 'magnum double chocolate': 3.8, 'magnum gold': 3.41, 'magnum white': 2.97, 'malbec': 0.82, 'malbec wine': 0.82, 'mallard duck meat': 2.11, 'mallard meat': 2.11, 'malt beer': 0.37, 'malt powder': 3.61, 'malted milk': 4.05, 'maltesers': 4.98, 'maltitol': 2.1, 'maltodextrin': 3.75, 'malt-o-meal': 0.51, 'maltose': 3.44, 'manchego cheese': 3.2, 'mandarin oranges': 0.53, 'mango': 0.6, 'mango lassi': 0.66, 'mangosteen': 0.73, 'manicotti': 3.57, 'maple syrup': 2.7, 'maracuya': 0.97, 'maraschino cherries': 1.65, 'marble cake': 3.39, 'margarine': 7.17, 'margherita pizza': 2.75, 'marjoram': 2.71, 'marmite': 2.25, 'marron': 2.1, 'marrow dumplings': 4.24, 'mars bar': 4.48, 'marsala wine': 1.0, 'marshmallow fluff': 6.66, 'marshmallows': 3.18, 'marzipan': 4.11, 'mascarpone': 4.5, 'mashed potatoes': 0.89, 'matzo bread': 3.51, 'mayonnaise': 6.92, 'mcdonaldâ€™s big mac': 2.56, 'mcdonaldâ€™s cheeseburger': 2.63, 'mcdonaldâ€™s chicken nuggets': 2.97, 'mcdonaldâ€™s double cheeseburger': 2.82, 'mcdonaldâ€™s filet-o-fish': 2.75, 'mcdonaldâ€™s mcchicken': 2.51, 'mcdonaldâ€™s mcdouble': 2.52, 'mcdonaldâ€™s mcmuffi egg': 2.25, 'mcdonaldâ€™s mcrib': 2.65, 'mcdonaldâ€™s mighty wings': 3.08, 'mcflurry': 1.53, 'mcflurry oreo': 1.86, 'mcrib': 2.65, 'meat pie': 2.42, 'meatball sandwich': 1.61, 'meatball soup': 0.49, 'meatloaf': 0.89, 'mello yello': 0.49, 'menhaden oil': 9.11, 'meringue': 2.85, 'merlot': 0.83, 'merlot wine': 0.83, 'mettwurst': 3.1, 'michelob amber bock': 0.47, 'michelob lager': 0.44, 'michelob light': 0.32, 'michelob ultra': 0.27, 'michelob ultra amber': 0.26, 'michelob ultra lime cactus': 0.27, 'midori': 2.67, 'mike and ike': 3.6, 'milk': 0.61, 'milk duds': 4.22, 'milkfish': 1.9, 'milkshake (dry)': 3.29, 'milky way': 4.49, 'miller chill': 0.31, 'miller genuine draft': 0.4, 'miller high life': 0.4, 'miller high life light': 0.31, 'miller lite': 0.27, 'millet': 3.78, 'millet flour': 3.72, 'millet gruel': 0.46, 'milo': 4.09, 'milwaukeeâ€™s best': 0.36, 'milwaukeeâ€™s best light': 0.28, 'minced onion': 0.4, 'minced veal': 1.43, 'minestrone': 0.34, 'mini milk': 1.2, 'mini-wheats': 3.53, 'minneola': 0.64, 'mint': 0.7, 'mint chocolate chip ice cream': 2.39, 'minute maid': 0.46, 'minute maid light': 0.02, 'miso': 1.99, 'mocca yogurt': 1.0, 'molasses': 2.9, 'molson': 0.42, 'monkey bread': 2.9, 'monkfish': 0.97, 'monterey': 3.73, 'monterey jack cheese': 3.73, 'moose': 1.34, 'moose meat': 1.34, 'mortadella': 3.11, 'moscato wine': 0.76, 'mostaccioli': 1.84, 'mozzarella': 2.8, 'mozzarella pizza': 2.49, 'muenster cheese': 3.68, 'muesli': 3.36, 'muffin': 2.96, 'mug root beer': 0.42, 'mulberries': 0.43, 'mulled wine': 1.96, 'mullet': 1.5, 'multi-grain bread': 2.65, 'multigrain cheerios': 3.8, 'mung beans': 0.12, 'mushroom pizza': 2.12, 'mushroom soup': 0.35, 'mushrooms': 0.22, 'muskmelon': 0.34, 'mussel': 1.72, 'mustard': 0.6, 'mustard greens': 0.27, 'mustard oil': 8.84, 'mustard sauce': 6.45, 'mustard seed': 5.08, 'mutton': 2.34, 'mutton meat': 2.34, 'naan': 3.1, 'nachos with cheese': 3.06, 'napoli pizza': 2.02, 'natto': 2.12, 'natural ice': 0.44, 'natural light': 0.27, 'navy bean': 3.37, 'nectar': 0.53, 'nectarine': 0.44, 'nestea': 0.21, 'neufchatel': 2.53, 'new york strip steak': 1.99, 'new york style pizza': 1.69, 'newcastle': 0.39, 'non-alcoholic beer': 0.37, 'noni': 0.53, 'nonpareils': 4.75, 'noodle soup': 0.34, 'nori': 0.35, 'norland red potatoes': 0.89, 'nutella': 5.44, 'nutmeg': 5.25, 'nutri-grain': 3.51, 'oâ€™doulâ€™s (n.a.)': 0.19, 'oat bran': 2.46, 'oat oil': 8.84, 'oatibix': 4.21, 'oatmeal': 3.75, 'oatmeal cookies': 4.5, 'oatmeal raisin cookies': 4.35, 'obatzda': 3.03, 'octopus': 1.64, 'okara': 0.77, 'okra': 0.33, 'old milwaukee': 0.41, 'old milwaukee n.a.': 0.16, 'olde english': 0.45, 'olive cream cheese': 3.42, 'olive loaf': 2.32, 'olive oil': 8.84, 'olive spread': 5.5, 'olives': 1.15, 'omelette': 1.54, 'onion': 0.4, 'onion powder': 3.41, 'onion rings': 4.11, 'onion soup': 0.23, 'opera cake': 3.2, 'orange': 0.47, 'orange chicken': 2.59, 'orange juice': 0.46, 'orange peel': 0.97, 'orange sauce': 1.79, 'orange soda': 0.48, 'orecchiette': 3.7, 'oregano': 2.65, 'organic yogurt': 0.75, 'orzo': 3.57, 'ostrich': 1.45, 'ostrich meat': 1.45, 'oven-roasted turkey breast': 1.04, 'oxtail soup': 0.28, 'pabst blue ribbon': 0.41, 'paczki': 3.36, 'pad thai': 1.5, 'paella': 1.56, 'pale ale': 0.42, 'palm kernel oil': 8.82, 'palm oil': 8.82, 'pan de sal': 2.93, 'pancake': 2.27, 'pandesal': 2.93, 'panettone': 3.6, 'papaya': 0.43, 'papaya juice': 0.58, 'paprika': 2.82, 'paratha': 3.25, 'parma ham': 3.45, 'parmesan': 4.31, 'parsley': 0.36, 'parsnip': 0.75, 'parsnips': 0.75, 'passion fruit': 0.97, 'passion fruit juice': 0.48, 'pastrami': 1.33, 'pavlova': 2.94, 'payday': 4.62, 'pea soup': 0.75, 'peach': 0.39, 'peach cobbler': 0.65, 'peach juice': 0.54, 'peach nectar': 0.54, 'peach pie': 2.23, 'peach yogurt': 0.97, 'peanut bar': 5.33, 'peanut brittle': 1.83, 'peanut butter': 5.89, 'peanut butter bars': 3.79, 'peanut butter cookies': 4.75, 'peanut butter sandwich': 4.08, 'peanut butter toast crunch': 4.31, 'peanut oil': 8.57, 'peanuts': 5.67, 'pear': 0.57, 'pear juice': 0.6, 'pear nectar': 0.6, 'pearl barley': 3.52, 'peas': 0.81, 'pecan': 6.91, 'pecan nuts': 6.91, 'pecan pie': 4.07, 'pecans': 6.91, 'pecorino': 3.87, 'peking duck': 2.25, 'penne': 3.51, 'penne rigate': 3.7, 'pepper': 0.27, 'pepper cheese': 1.0, 'peppermint bark': 5.0, 'peppermint extract': 0.0, 'pepperoni': 4.94, 'pepperoni pizza': 2.55, 'pepsi': 0.44, 'persimmon': 1.27, 'pesto': 4.58, 'pesto cream cheese': 3.42, 'peter pan peanut butter': 6.09, 'pez': 4.27, 'pheasant': 2.39, 'pheasant breast': 1.33, 'pheasant leg': 2.39, 'pheasant meat': 2.39, 'philadelphia cream cheese': 3.42, 'philly cheese steak': 2.5, 'physalis': 0.49, 'pibb xtra': 0.4, 'pickerel': 1.11, 'pickled herring': 2.62, 'pide': 2.68, 'pie': 2.37, 'pierogi': 2.0, 'pig brain': 1.38, 'pig ear': 1.66, 'pig fat': 6.38, 'pig heart': 1.48, 'pig kidney': 1.51, 'pig lung': 0.99, 'pigâ€™s tail': 3.96, 'pigâ€™s trotter': 2.43, 'pigeon': 1.42, 'pike': 1.13, 'pili nuts': 7.19, 'pilsner': 0.43, 'pimento loaf': 2.65, 'pine nuts': 6.73, 'pineapple': 0.5, 'pineapple cream cheese': 3.42, 'pineapple juice': 0.53, 'pineapple orange juice': 0.5, 'pineapple upside-down cake': 3.19, 'pink grapefruit': 0.42, 'pinot gris': 0.83, 'pinot noir': 0.75, 'pinto beans': 3.47, 'pistachios': 5.62, 'pita bread': 2.75, 'pizza': 2.67, 'pizza dough': 2.28, 'pizza hut stuffed crust pizza': 2.55, 'pizza hut supreme pizza': 2.48, 'pizza rolls': 2.47, 'plaice': 0.91, 'plain yogurt': 0.61, 'plantain': 1.22, 'plantains': 1.22, 'plum': 0.46, 'plum cake': 1.09, 'plum jam': 2.5, 'plum juice': 0.71, 'plum wine': 1.63, 'polenta': 3.66, 'polish sausage': 3.01, 'pollack': 1.11, 'pomegranate': 0.83, 'pomegranate juice': 0.66, 'pomelo': 0.38, 'pop rocks': 3.58, 'popcorn': 5.82, 'poppy seed': 5.25, 'poppy seed oil': 8.84, 'poppy seeds': 5.25, 'poppy-seed cake': 3.94, 'pork': 1.96, 'pork baby back ribs': 2.12, 'pork bacon': 4.07, 'pork belly': 5.18, 'pork blade steak': 2.32, 'pork chop': 1.23, 'pork chops': 1.96, 'pork country-style ribs': 2.47, 'pork crown roast': 2.12, 'pork cutlet': 1.31, 'pork cutlets': 1.31, 'pork leg': 2.01, 'pork liver': 1.65, 'pork loin': 2.04, 'pork meatloaf': 2.43, 'pork melt': 2.19, 'pork ragout': 0.73, 'pork rib roast': 1.59, 'pork ribs': 2.92, 'pork roast': 2.47, 'pork roll': 3.02, 'pork sausage': 3.39, 'pork shank': 1.72, 'pork shoulder': 2.69, 'pork shoulder blade': 2.32, 'pork steaks': 1.96, 'pork stomach': 2.5, 'pork tongue': 2.71, 'port wine': 1.6, 'porter': 0.54, 'porterhouse steak': 2.47, 'post raisin bran': 3.22, 'post shredded wheat': 3.47, 'potato': 0.77, 'potato bread': 2.66, 'potato dumpling': 1.24, 'potato fritter': 1.85, 'potato gratin': 1.32, 'potato pancakes': 2.68, 'potato salad': 1.43, 'potato soup': 0.8, 'potato starch': 3.31, 'potato sticks': 5.22, 'potato waffles': 1.67, 'potato wedges': 1.23, 'potatoes au gratin': 1.32, 'poularde': 2.0, 'poultry seasoning': 3.07, 'pound cake': 3.9, 'poutine': 2.27, 'powdered milk': 4.96, 'powdered sugar': 3.89, 'powerade': 0.16, 'prawn crackers': 5.27, 'pretzel': 3.38, 'pretzel roll': 3.38, 'pretzel sticks': 3.8, 'prickly pear': 0.41, 'probiotic yogurt': 0.8, 'profiterole': 3.34, 'prosciutto': 1.95, 'prosecco': 0.66, 'protein powder': 4.11, 'provolone': 3.51, 'puff': 3.67, 'puff pastry': 5.58, 'puffed rice': 3.83, 'puffed wheat': 3.67, 'pulled pork sandwich': 2.11, 'pumpernickel': 2.5, 'pumpkin': 0.26, 'pumpkin bread': 2.98, 'pumpkin cheesecake': 3.4, 'pumpkin pie': 2.43, 'pumpkin pie spice': 3.42, 'pumpkin seed oil': 8.8, 'pumpkin seeds': 5.6, 'pumpkin soup': 0.29, 'punch': 0.62, 'purple majesty potatoes': 0.72, 'puy lentils': 3.45, 'quail': 2.27, 'quail breast': 1.23, 'quaker grits': 3.44, 'quaker oatmeal': 3.75, 'quaker oatmeal squares': 4.0, 'quark': 1.45, 'quattro formaggi pizza': 2.48, 'quince': 0.57, 'quinoa': 3.68, 'rã¶sti': 1.38, 'rabbit': 1.97, 'rack of pork': 2.41, 'raclette cheese': 3.57, 'racoon': 2.55, 'racoon meat': 2.55, 'radish seeds': 0.43, 'radishes': 0.16, 'raisin bran': 3.22, 'raisin bran crunch': 3.55, 'raisin bread': 2.74, 'raisin nut bran': 3.67, 'raisins': 2.99, 'rajma': 1.4, 'rambutan': 0.82, 'ramen': 4.47, 'ranch dressing': 5.1, 'raspberries': 0.52, 'raspberry pie': 2.4, 'ravioli': 0.77, 'ready brek': 3.59, 'real butter': 7.2, 'red beans': 1.24, 'red cabbage': 0.31, 'red gold potatoes': 0.89, 'red kidney bean': 3.37, 'red lentils': 3.29, 'red pepper': 2.51, 'red pepper pizza': 1.92, 'red potatoes': 0.89, 'red snapper': 1.28, 'red velvet cake': 3.67, 'red wine': 0.85, 'red wine vinegar': 0.19, 'red wines': 0.85, 'redbridge (gluten-free)': 0.45, 'redfish': 0.94, 'reeses peanut butter cups': 5.36, 'refried beans': 0.91, 'reindeer': 2.0, 'reindeer meat': 2.0, 'remoulade sauce': 6.35, 'reuben sandwich': 2.08, 'rhea': 1.6, 'rhubarb': 0.21, 'rhubarb pie': 2.45, 'rib eye steak': 2.17, 'rice bran oil': 8.89, 'rice chex': 3.87, 'rice krispies': 3.94, 'rice milk': 0.49, 'rice pudding': 1.18, 'ricotta': 1.74, 'riesling': 0.8, 'riesling wine': 0.8, 'rigatoni': 3.53, 'ring bologna': 2.86, 'roast beef': 1.87, 'roast dinner': 1.98, 'roast potatoes': 1.49, 'roasted almonds': 4.52, 'roasted soybeans': 4.71, 'rock sugar': 6.25, 'rocky road ice cream': 2.57, 'roll': 3.16, 'rolled oats': 3.84, 'rolling rock': 0.37, 'rolling rock light': 0.3, 'rollmops': 1.71, 'rolo': 4.74, 'romano': 3.87, 'root beer': 0.41, 'roquefort': 3.69, 'rose wine': 0.71, 'rosemary': 1.31, 'rosemary potatoes': 0.93, 'roti': 2.64, 'rotini': 3.53, 'round steak': 1.82, 'rum': 2.31, 'rum cake': 3.51, 'rump steak': 1.71, 'rusk': 4.1, 'russet potatoes': 0.97, 'russian banana potatoes': 0.67, 'russian dressing': 4.0, 'rutabaga': 0.38, 'rye bran': 2.81, 'rye bread': 2.59, 'sâ€™mores': 5.0, 'sacher torte': 3.52, 'safflower oil': 8.57, 'safflower seeds': 5.17, 'saffron': 3.1, 'sage': 3.15, 'sago': 3.54, 'salad dressing': 4.49, 'salami': 3.36, 'salami pizza': 2.55, 'salmon': 2.06, 'salmon cream cheese': 3.42, 'salmon oil': 9.11, 'salt': 0.0, 'salt meat': 2.86, 'salt pork': 2.86, 'salted butter': 7.17, 'sambal oelek': 0.21, 'sambuca': 3.33, 'samosa': 2.14, 'samuel adams': 0.45, 'sandwich': 3.04, 'sandwich bread': 2.51, 'sandwich cheese': 1.48, 'sangria': 0.96, 'sapodilla': 0.83, 'sardine oil': 9.02, 'sardines': 2.08, 'sauerkraut juice': 0.14, 'sausage': 2.3, 'sausage pizza': 2.46, 'sausage roll': 3.5, 'sausage rolls': 2.97, 'sauvignon blanc': 0.81, 'savory': 2.72, 'savoury biscuits': 3.47, 'slops': 1.11, 'scampi': 0.84, 'schnitzel': 1.56, 'schwanâ€™s': 2.46, 'schweppes ginger ale': 0.38, 'scone': 3.62, 'scooters': 3.67, 'scotch': 2.22, 'scotch broth': 0.33, 'sea bass': 1.24, 'sea salt': 0.0, 'seafood pizza': 2.45, 'semi-skimmed milk': 0.5, 'semolina': 3.4, 'semolina flour': 3.5, 'semolina pudding': 0.67, 'serrano ham': 3.0, 'serrano pepper': 0.32, 'sesame ginger dressing': 4.64, 'sesame oil': 8.84, 'sesame paste': 5.95, 'sesame seeds': 5.73, 'shad': 2.52, 'shallots': 0.72, 'shark': 1.3, 'shea oil': 8.84, 'sheep cheese': 3.64, 'shells': 3.53, 'shepherds pie': 0.7, 'sherry': 1.16, 'shirataki noodles': 0.18, 'shiraz': 0.71, 'shock top': 0.47, 'shock top raspberry wheat': 0.5, 'shortbread': 5.02, 'shortcrust pastry': 5.44, 'shredded coconut': 5.01, 'shredded wheat': 3.4, 'shreddies': 3.51, 'shrimp cocktail': 4.64, 'shrimp pizza': 2.09, 'sicilian pizza': 2.41, 'sierra nevada strong': 0.62, 'silken tofu': 0.55, 'skim milk': 0.35, 'skim milk yogurt': 0.56, 'skippy peanut butter': 5.94, 'skirt steak': 2.05, 'skittles': 4.05, 'sloe gin': 3.32, 'sloppy joe': 0.71, 'sloppy joes': 1.54, 'slurpee': 0.04, 'slush puppie': 0.5, 'smart start': 3.71, 'smarties': 3.57, 'smarties mcflurry': 1.98, 'smelt': 1.24, 'smoked almonds': 5.75, 'smoked cheese': 4.1, 'smoked ham': 1.07, 'smoked salmon': 1.58, 'smoked sausage': 3.01, 'smoked turkey breast': 1.04, 'smoothie': 0.37, 'smores': 5.0, 'smuckers strawberry jam': 2.5, 'snickers': 4.84, 'snickers ice cream': 3.6, 'soda': 0.53, 'soda bread': 2.9, 'soft cheese': 2.68, 'soft serve': 2.22, 'soft tofu': 0.61, 'sole': 0.86, 'solero': 1.0, 'sorbitol': 3.75, 'soufflã©': 2.04, 'sour cream': 1.81, 'sour cream sauce': 0.6, 'sour patch kids': 3.63, 'sourdough bread': 2.89, 'soursop fruit': 0.66, 'souse': 1.57, 'southern comfort': 2.47, 'soy beans': 1.47, 'soy cheese': 2.35, 'soy mayonnaise': 3.22, 'soy milk': 0.45, 'soy noodles': 2.16, 'soy nut butter': 5.62, 'soy nuts': 4.71, 'soy oil': 8.82, 'soy protein powder': 3.38, 'soy sauce': 0.67, 'soy yogurt': 0.66, 'soya cheese': 2.35, 'soybean oil': 8.89, 'soybeans': 1.47, 'soynut butter': 5.62, 'spaetzle': 3.68, 'spaghetti': 3.7, 'spaghetti bolognese': 1.32, 'spam': 3.15, 'spanakopita': 2.46, 'spare ribs': 2.38, 'spareribs': 2.38, 'sparkling wine': 1.9, 'sparks': 0.74, 'special k': 3.77, 'special k chocolatey delight': 3.88, 'special k protein plus': 3.75, 'special k red berries': 3.45, 'speculoos': 4.69, 'spelt': 3.38, 'spelt bran': 1.77, 'spelt semolina': 3.6, 'spice cake': 3.32, 'spicy italian': 2.19, 'spinach': 0.23, 'spinach feta pizza': 2.42, 'spinach pizza': 2.34, 'spinach tortellini': 3.14, 'spirelli': 3.67, 'sponge cake': 2.89, 'spring roll': 2.5, 'spring rolls': 2.5, 'sprinkles': 5.0, 'sprite': 0.37, 'sprite zero': 0.0, 'spritz cookies': 5.0, 'squash': 0.45, 'squid': 0.92, 'squirrel': 1.73, 'squirrel meat': 1.73, 'squirt': 0.44, 'st. pauli girl': 0.42, 'standing rib roast': 3.33, 'star fruit': 0.31, 'starch': 3.81, 'starfruit': 0.31, 'steel reserve': 0.63, 'stevia': 0.0, 'stew beef': 1.91, 'stilton cheese': 3.93, 'stout': 0.51, 'stout beer': 0.51, 'stracciatella yogurt': 1.39, 'strawberries': 0.32, 'strawberry cheesecake': 3.27, 'strawberry ice cream': 2.36, 'strawberry jam': 2.5, 'strawberry jelly': 2.5, 'strawberry milkshake': 1.13, 'strawberry pie': 2.3, 'strawberry preserves': 2.78, 'strawberry rhubarb pie': 2.81, 'strawberry sundae': 1.58, 'strawberry yogurt': 1.0, 'string cheese': 2.5, 'strip steak': 1.17, 'strong beer': 0.55, 'stuffed crust pizza': 2.55, 'sturgeon': 1.35, 'subway club sandwich': 1.31, 'succotash': 1.15, 'sucrose': 3.87, 'sugar': 4.05, 'sugar peas': 0.42, 'sugar puffs': 3.79, 'summer sausage': 2.98, 'sunbutter': 6.17, 'sundae': 2.15, 'sunflower butter': 6.17, 'sunflower oil': 8.84, 'sunflower seeds': 5.84, 'sunkist': 0.25, 'surge': 0.48, 'sushi': 1.5, 'sweet and sour sauce': 1.79, 'sweet chestnut': 1.94, 'sweet peas': 0.48, 'sweet potato': 0.92, 'sweet potato pie': 2.6, 'sweet red wine': 0.81, 'sweet rolls': 3.33, 'sweet white wine': 0.82, 'sweet wines': 0.83, 'sweetened condensed milk': 3.21, 'sweetener': 3.6, 'swiss cheese': 3.8, 'swiss roll': 4.39, 'swordfish': 1.72, 'tab': 0.0, 'tabasco': 0.7, 'taco': 2.17, 'tagliatelle': 3.7, 'take 5': 4.76, 'tamarind': 2.39, 'tandoori chicken': 1.13, 'tang': 3.81, 'tangerine': 0.53, 'tangerine juice': 0.43, 'tap water': 0.0, 'tapenade': 2.33, 'taro': 1.12, 'tarragon': 2.95, 'tarte flambã©e': 2.53, 'tarte tatin': 2.1, 't-bone steak': 2.02, 't-bone-steak': 2.21, 'tea': 0.01, 'tempeh': 1.93, 'tequila': 1.1, 'teriyaki sauce': 0.89, 'textured soy protein': 5.71, 'textured vegetable protein': 3.33, 'thai curry paste': 1.55, 'thai soup': 0.6, 'thin crust pizza': 2.61, 'thyme': 2.76, 'tilsit': 3.4, 'tilt': 0.64, 'tiramisu': 2.83, 'tiramisu cake': 2.91, 'toast': 2.61, 'toasties': 3.61, 'toblerone': 5.25, 'tofu': 0.76, 'tomato': 0.18, 'tomato juice': 0.17, 'tomato paste': 0.82, 'tomato puree': 0.38, 'tomato rice soup': 0.47, 'tomato sauce': 0.24, 'tomato seed oil': 8.84, 'tomato soup': 0.3, 'tongue': 2.84, 'tonic water': 0.35, 'tortellini': 2.91, 'tortilla': 2.37, 'tortilla bread': 2.65, 'tortilla chips': 4.99, 'tortilla wrap': 2.71, 'treacle tart': 3.69, 'tres leches cake': 2.46, 'trifle': 1.8, 'triggerfish': 0.93, 'triple sec': 1.53, 'trix': 4.0, 'trout': 1.9, 'tuna': 0.86, 'tuna pizza': 2.54, 'tuna salad': 1.87, 'turbot': 1.22, 'turkey': 1.04, 'turkey breast': 1.04, 'turkey cutlet': 1.89, 'turkey drumsticks': 2.08, 'turkey giblets': 1.73, 'turkey ham': 1.26, 'turkey heart': 1.74, 'turkey hill': 2.71, 'turkey legs': 2.08, 'turkey liver': 1.89, 'turkey salami': 1.52, 'turkey steak': 1.89, 'turkey stomach': 1.48, 'turkey wings': 2.21, 'turmeric': 3.54, 'turnip greens': 0.2, 'turnips': 0.28, 'twix': 4.95, 'tzatziki': 1.17, 'unsalted butter': 7.17, 'vanilla bean': 2.5, 'vanilla coke': 0.45, 'vanilla cone': 1.62, 'vanilla extract': 2.88, 'vanilla ice cream': 2.01, 'vanilla milkshake': 1.49, 'vanilla sugar': 3.57, 'vanilla yogurt': 1.01, 'veal': 2.82, 'veal breast': 2.82, 'veal heart': 1.86, 'veal kidney': 1.63, 'veal leg': 2.11, 'veal roast beef': 1.75, 'veal shank': 1.77, 'veal shoulder': 1.83, 'veal sirloin': 2.04, 'veal tenderloin': 2.17, 'veal tongue': 2.02, 'vegemite': 1.8, 'vegetable beef soup': 0.31, 'vegetable broth': 0.05, 'vegetable cream cheese': 3.42, 'vegetable juice': 0.21, 'vegetable oil': 8.0, 'vegetable pizza': 2.56, 'vegetable shortening': 8.84, 'vegetable soup': 0.28, 'vegetable stock': 0.05, 'vegetarian pizza': 2.56, 'veggie burger': 1.81, 'veggie delight': 1.38, 'veggie patty': 3.9, 'veggie pizza': 2.31, 'venison': 1.64, 'venison sirloin': 1.58, 'vermicelli': 3.68, 'vermouth': 1.3, 'victoria sponge cake': 2.57, 'vinaigrette': 1.2, 'vinegar': 0.18, 'vodka': 2.31, 'volvic': 0.0, 'waffles': 3.12, 'wahoo': 1.67, 'walnut cream cheese': 3.42, 'walnut oil': 8.89, 'walnuts': 6.54, 'wasabi': 1.09, 'water': 0.0, 'watermelon': 0.3, 'wedding cake': 3.81, 'wedding soup': 0.53, 'weetabix': 3.58, 'weet-bix': 3.53, 'weetos': 3.78, 'weisswurst': 3.13, 'wendyâ€™s baconator': 3.04, 'wendyâ€™s jr. bacon cheeseburger': 2.61, 'wendyâ€™s jr. cheeseburger': 2.25, 'wendyâ€™s son of baconator': 3.21, 'wheat beer': 0.45, 'wheat bran': 2.16, 'wheat germ': 3.82, 'wheat germ oil': 9.29, 'wheat gluten': 3.25, 'wheat semolina': 3.6, 'wheat starch': 3.51, 'wheaties': 3.67, 'whipped cream': 2.57, 'whisky': 2.5, 'white american': 1.48, 'white beans': 3.36, 'white bread': 2.38, 'white cheddar': 4.03, 'white grape juice': 0.75, 'white pepper': 2.96, 'white pizza': 2.46, 'white potatoes': 0.94, 'white wine': 0.82, 'white zinfandel': 0.88, 'whitefish': 1.72, 'whiting': 1.16, 'whole grain noodles': 3.47, 'whole grain spaghetti': 3.51, 'whole grain wheat': 3.39, 'whole milk': 0.61, 'whole wheat bread': 2.47, 'whole wheat flour': 3.4, 'wholegrain oat': 3.75, 'whoopie pie': 4.0, 'whopper': 2.31, 'wild boar': 1.6, 'wild boar meat': 1.6, 'wild duck': 2.11, 'wild honey': 2.86, 'wine': 0.83, 'winter squash': 0.34, 'wisconsin cheese': 3.89, 'worcestershire sauce': 0.78, 'xylitol': 2.4, 'yam': 1.18, 'yam bean': 0.38, 'yams': 1.16, 'yeast (dry)': 3.25, 'yellow lentils': 3.04, 'yellow tail wine': 0.71, 'yerba mate': 0.62, 'yogurt': 0.61, 'yogurt corner': 1.19, 'yogurt dressing': 0.45, 'yoplait boston cream pie': 0.9, 'yoplait french vanilla': 1.0, 'yoplait greek blueberry': 1.0, 'yoplait greek coconut': 1.0, 'yoplait greek strawberry': 1.0, 'yoplait greek vanilla': 1.0, 'yoplait harvest peach': 1.0, 'yoplait key lime pie': 1.0, 'yoplait mango': 1.0, 'yoplait mixed berry': 1.0, 'yoplait pina colada': 1.0, 'yoplait strawberry': 1.0, 'yoplait strawberry banana': 1.0, 'yoplait strawberry cheesecake': 1.0, 'yorkshire pudding': 5.53, 'young gouda': 3.56, 'yuba': 1.76, 'yukon gold potatoes': 0.82, 'zander': 0.84, 'zesty italian dressing': 2.67, 'zinfandel': 0.88, 'zinger': 2.56, 'zinger burger': 2.56, 'ziti': 3.52, 'zucchini': 0.17, 'None': 0.0, 'none': 0.0}
                cal = 0.0
                try:
                    for i in range(0,8):  
                        cal += (quantity[i]*((calories[item[i].lower()]))
                except:
                    flash('Enter the enter details correctly.')
                    return redirect(url_for('calorie'))
                diff = cal-bmr
                cursor.execute('insert into userCalCount(weight, height, age, gender, bmr, final_result, food_cal, username) values(%s,%s,%s,%s,%s,%s,%s,%s)',[weight, height, age, gender, bmr, diff, cal, username])
                mydb.commit()
                diff = abs(diff)
                data = [weight, height, age, gender, bmr, diff, cal, username]
                print(data)
                if bmr > cal:
                    flash(f'You need to take {diff} more calories')
                    return render_template('result.html',data=data)
                else:
                    flash(f'You are taking {diff} more calories than required')
                    return render_template('result.html',data=data)
            except:
                return redirect('calorie.html')
        return render_template('calorie.html')
    else:
        return redirect(url_for('login'))

@app.route('/result')
def result():
    if session.get('user'):
        return render_template('result.html')
    else:
        return redirect(url_for('login'))

@app.route('/history')
def history():
    if session.get('user'):
        username=session.get('user')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from usercalcount where username = %s order by cal_date desc',[username])
        data=cursor.fetchall()
        cursor.close()
        return render_template('history.html',data=data)
    else:
        return redirect(url_for('login'))
    
@app.route('/delete/<nid>')
def delete(nid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('delete from userCalCount where cid=%s',[nid])
        mydb.commit()
        cursor.close()
        flash('Record Deleted.')
        return redirect(url_for('history'))
    else:
        return redirect(url_for('login'))
    
@app.route('/view/<nid>')
def view(nid):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select weight, height, age, gender, bmr, final_result, food_cal, username from userCalCount where cid=%s',[nid])
        data = cursor.fetchone()
        cursor.close()
        diff = data[5]
        if diff < 0:
            flash(f'You need to take {diff} more calories')
            return render_template('result.html',data=data)
        else:
            flash(f'You are taking {diff} more calories than required')
            return render_template('result.html',data=data)
    else:
        return redirect(url_for('login'))
    
@app.route('/forgotpassword', methods=["GET","POST"])
def forgotpassword():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        confirmPassword = request.form['password1']
        if password != confirmPassword:
            flash('Both passwords are not same')
            return redirect(url_for('forgotpassword'))
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select email from users where username=%s',[username])
        email = cursor.fetchone()[0]
        cursor.close()
        data={'username':username,'password':password, 'email':email}
        subject='Forgot Password Confirmation'
        body=f"Welcome to our Calorie Counter Application {username}!!!\n\nThis is your account's password reset confirmation email....\nClick on this link to confirm your reset password - {url_for('reset',token=token(data),_external=True)}\n\n\n\nWith Regards,\nCalorie Counter Team"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('forgotpassword'))
    return render_template('forgotpassword.html')

@app.route('/reset/<token>')
def reset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception:
        flash('Link expired reset your password again')
        return redirect(url_for('forgotpassword'))
    else:
        cursor=mydb.cursor(buffered=True)
        username=data['username']
        password = data['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('update users set password = %s where username = %s',[password, username])
        mydb.commit()
        cursor.close()
        flash('Password Reset Successful!')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(use_reloader = True, debug= True)


