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
                calories = {'Absinthe': 3.48, 'Acai': 0.7, 'Acai Juice': 0.58, 'ACE Drink': 0.44, 'Acerola': 0.32, 'Acorn': 3.87, 'Activia': 0.74, 'Activia Lemon': 1.0, 'Activia Strawberry': 0.97, 'Advocaat': 2.83, 'After Eight': 4.52, 'Agar-Agar': 0.26, 'Agave Syrup': 3.1, 'Airheads': 3.75, 'Ajvar': 0.18, 'Ale': 0.35, 'Alfalfa Sprouts': 0.23, 'All Purpose Flour': 3.64, 'All-blue Potatoes': 0.61, 'Alligator': 2.32, 'Alligator Meat': 2.32, 'Almond Butter': 6.14, 'Almond Extract': 2.58, 'Almond Milk': 0.17, 'Almond Oil': 8.82, 'Almond Roca': 5.71, 'Almonds': 5.75, 'Aloe Vera': 0.44, 'Aloe Vera Yogurt': 0.85, 'Alphabet Soup': 0.25, 'Altbier': 0.43, 'Amaranth': 3.71, 'Amaretto': 3.1, 'American Cheese': 1.48, 'Anchovy': 1.31, 'Andouille': 2.32, 'Angel Delight': 4.51, 'Angel Food Cake': 2.58, 'Animal Crackers': 4.46, 'Anise': 3.37, 'Anise Seed': 3.37, 'Antelope Meat': 1.5, 'Apple': 0.52, 'Apple Butter': 1.73, 'Apple Cake': 2.52, 'Apple Cobbler': 1.98, 'Apple Crisp': 1.56, 'Apple Crumble': 1.56, 'Apple Juice': 0.46, 'Apple Pie': 2.37, 'Apple Pie Filling': 1.0, 'Apple Spritzer': 0.24, 'Apple Strudel': 2.74, 'Apple Turnover': 3.48, 'Applejack': 2.33, 'Applesauce': 0.62, 'Applesauce Cake': 3.58, 'Applewood': 4.1, 'Apricot': 0.48, 'Apricot Jam': 2.5, 'Apricot Kernel Oil': 8.89, 'Apricot Nectar': 0.56, 'Arbyâ€™s Grand Turkey Club': 2.1, 'Arbyâ€™s Reuben': 2.08, 'Arbyâ€™s Roast Beef Classic': 2.34, 'Arbyâ€™s Roast Beef Max': 2.34, 'Argan Oil': 8.96, 'Arrabiata Sauce': 0.36, 'Arrowroot': 0.65, 'Artichoke': 0.47, 'Arugula': 0.25, 'Asiago Cheese': 3.92, 'Asian Pear': 0.42, 'Asparagus': 0.2, 'Asti': 1.38, 'Aubergine': 0.25, 'Avocado': 1.6, 'Avocado Oil': 8.57, 'Ayran': 0.42, 'Azuki Bean': 1.24, 'Babassu Oil': 8.84, 'Baby Back Ribs': 2.59, 'Baby Ruth': 4.69, 'Babybel': 3.33, 'Bacon': 4.07, 'Bacon and Eggs': 2.52, 'Bagel': 2.57, 'Baguette': 2.74, 'Baileyâ€™s Irish Cream': 3.27, 'Baileys': 3.27, 'Baked Alaska': 2.47, 'Baked Beans': 0.94, 'Baked Chicken': 1.64, 'Baked Ham': 3.43, 'Baked Potato': 0.93, 'Bakewell Tart': 4.3, 'Baking Powder': 0.53, 'Baking Soda': 0.0, 'Balsamic Vinaigrette Dressing': 2.9, 'Balsamic Vinegar': 0.88, 'Bamboo Shoots': 0.27, 'Banana': 0.89, 'Banana Bread': 3.26, 'Banana Juice': 0.5, 'Banana Nut Bread': 3.26, 'Banoffee Pie': 3.95, 'Barbecue Sauce': 1.5, 'Barley': 3.54, 'Barley Groats': 1.0, 'Barqâ€™s': 0.46, 'Basil': 2.33, 'Baskin-Robbins': 2.39, 'Bass': 0.45, 'BBQ Chicken Pizza': 2.34, 'BBQ Pizza': 2.24, 'BBQ Rib': 2.12, 'BBQ Ribs': 2.55, 'Bean Burrito': 2.0, 'Bean Curd': 0.76, 'Bean Sprouts': 0.3, 'Bean Stew': 1.33, 'Bear Meat': 2.59, 'Beaver Meat': 2.12, 'Bechamel Sauce': 2.25, 'Beckâ€™s': 0.39, 'Beechnut': 5.76, 'Beef': 1.71, 'Beef Bouillon': 0.03, 'Beef Brain': 1.96, 'Beef Brisket': 1.37, 'Beef Fillet': 1.89, 'Beef Goulash': 1.23, 'Beef Heart': 1.65, 'Beef Jerky': 4.1, 'Beef Kidney': 1.58, 'Beef Liver': 1.91, 'Beef Lung': 1.2, 'Beef Melt': 2.71, 'Beef Minute Steak': 1.33, 'Beef Neck': 2.13, 'Beef Noodle Soup': 0.34, 'Beef Pancreas': 2.71, 'Beef Patty': 2.47, 'Beef Pizza': 3.04, 'Beef Prime Rib': 4.04, 'Beef Ribs': 1.96, 'Beef Salami': 3.75, 'Beef Sirloin': 1.82, 'Beef Soup': 0.33, 'Beef Stew': 0.95, 'Beef Suet': 8.54, 'Beef Tallow': 9.02, 'Beef Tenderloin': 2.18, 'Beef Thymus': 3.19, 'Beef Tongue': 2.84, 'Beef Tripe': 0.94, 'Beer': 0.43, 'Beer Bread': 2.27, 'Beetroot': 0.43, 'Bell Pepper': 0.2, 'Ben and Jerryâ€™s': 2.28, 'Bengal Gram': 3.64, 'BergkÃ¤se': 4.18, 'Bernaise Sauce': 4.14, 'Bianca Pizza': 2.46, 'Big Nâ€™ Tasty': 2.23, 'Bircher Muesli Yogurt': 1.09, 'Birthday Cake': 4.65, 'Biryani': 1.76, 'Biscuit': 2.69, 'Bison': 1.71, 'Bison Meat': 1.71, 'Bison Sirloin': 1.71, 'Bitter Lemon': 0.34, 'Black and White Cookie': 3.81, 'Black Beans': 3.41, 'Black Bread': 2.5, 'Black Chickpeas': 3.64, 'Black Forest Cake': 2.64, 'Black Gram': 3.41, 'Black Olives': 1.15, 'Black Pepper': 2.51, 'Black Pudding': 3.79, 'Black Rice': 3.23, 'Black Sesame Seeds': 5.73, 'Blackberries': 0.43, 'Blackberry Jam': 2.5, 'Blackberry Juice': 0.48, 'Blackcurrant Jam': 2.5, 'Blood Oranges': 0.5, 'Blood Sausage': 3.79, 'BLT': 2.47, 'Blue Cheese': 3.53, 'Blue Cheese Dressing': 5.33, 'Blue Curacao': 2.43, 'Blue Moon': 0.48, 'Blueberries': 0.57, 'Blueberry Cobbler': 2.34, 'Blueberry Jam': 2.5, 'Blueberry Muffin': 3.77, 'Blueberry Pie': 2.32, 'Blueberry Yogurt': 1.05, 'Bluefish': 1.59, 'Bock Beer': 0.5, 'Bockwurst': 3.01, 'Boiled Ham': 1.26, 'Boiled Potatoes': 0.87, 'Bologna': 2.47, 'Bolognese': 1.06, 'Boudin': 1.94, 'Bouillon': 0.16, 'Bourbon': 2.33, 'Boysenberry Juice': 0.54, 'Bran Flakes': 3.56, 'Bran Muffins': 2.7, 'Brandy': 2.13, 'Bratwurst': 3.33, 'Brawn': 3.09, 'Brazil Nuts': 6.56, 'Bread Flour': 3.61, 'Bread Pudding': 1.53, 'Breadfruit': 1.03, 'Breadsticks': 4.0, 'Breakfast Sausage Links': 3.39, 'Bream': 1.35, 'Bresaola': 1.78, 'Brie': 3.34, 'Brioche': 3.46, 'Brittle': 5.92, 'Broccoli': 0.34, 'Broccoli Cheese Soup': 0.87, 'Broccoli Soup': 0.87, 'Broth': 1.0, 'Brown Bread': 2.46, 'Brown Lentil': 3.53, 'Brown Rice': 3.88, 'Brown Sugar': 3.95, 'Brownies': 4.05, 'Brussels Sprouts': 0.43, 'Buckler (N.A.)': 0.21, 'Buckwheat': 3.43, 'Buckwheat Groats': 3.46, 'Bud Ice': 0.35, 'Bud Light': 0.29, 'Bud Light Chelada': 0.43, 'Bud Light Lime': 0.34, 'Bud Select': 0.28, 'Bud Select 55': 0.15, 'Budweiser': 0.41, 'Budweiser Chelada': 0.52, 'Buffalo': 1.31, 'Buffalo Chicken Pizza': 2.52, 'Buffalo Meat': 1.31, 'Bun': 3.16, 'Bundt Cake': 3.7, 'Burger King Angry Whopper': 2.55, 'Burger King Double Whopper': 2.39, 'Burger King Double Whopper with Cheese': 2.49, 'Burger King Original Chicken Sandwich': 3.01, 'Burger King Premium Alaskan Fish Sandwich': 2.59, 'Burger King Triple Whopper': 2.69, 'Burger King Whopper': 2.31, 'Burger King Whopper Jr.': 2.34, 'Burger King Whopper with Cheese': 2.41, 'Burrito': 1.63, 'Busch': 0.37, 'Busch Light': 0.27, 'Busch N.A.': 0.17, 'Butter': 7.2, 'Butter Cheese': 3.88, 'Butter Chicken': 1.4, 'Butter Pecan Ice Cream': 2.48, 'Butterfinger': 4.5, 'Butterfish': 1.87, 'Buttermilk': 0.62, 'Buttermilk Pancakes': 2.38, 'Buttermilk Pie': 3.8, 'Buttermilk Ranch Dressing': 5.33, 'Butternut': 6.12, 'Butterscotch Chips': 5.39, 'Cabbage': 0.25, 'Cabbage Soup': 0.28, 'Cabernet Sauvignon': 0.77, 'Caesar Dressing': 4.29, 'Cake Flour': 3.62, 'abrese Pizza': 2.35, 'amari': 1.75, 'f Brain': 1.36, 'f Liver': 1.92, 'f Lung': 1.04, 'f Melt': 2.56, 'ifornia Roll': 0.93, 'zone': 2.31, 'Camembert': 3.0, 'Canada Dry Ginger Ale': 0.41, 'Canadian Whiskey': 2.16, 'Canadian-Style Bacon': 1.07, 'Candied Orange Peel': 0.97, 'Candy Apple': 1.52, 'Candy Cane': 4.23, 'Candy canes': 4.23, 'Candy Corn': 3.6, 'Candy Floss': 4.0, 'Cane Sugar': 3.87, 'Canned Apricots': 0.48, 'Canned Blackberries': 0.92, 'Canned Blueberries': 0.88, 'Canned Cherries': 0.54, 'Canned Cranberries': 1.78, 'Canned Crushed Pineapple': 0.53, 'Canned Figs': 1.07, 'Canned Fruit Cocktail': 0.81, 'Canned Fruit Salad': 0.5, 'Canned Gooseberries': 0.73, 'Canned Grapefruit': 0.37, 'Canned Grapes': 0.76, 'Canned Mandarin Oranges': 0.71, 'Canned Mango': 0.65, 'Canned Mangosteen': 0.73, 'Canned Mixed Fruit': 0.71, 'Canned Morello Cherries': 0.81, 'Canned Oranges': 0.62, 'Canned Peaches': 0.54, 'Canned Pears': 0.35, 'Canned Pineapple': 0.6, 'Canned Plums': 0.58, 'Canned Raspberries': 0.91, 'Canned Sliced Pineapple': 0.53, 'Canned Sour Cherries': 1.14, 'Canned Strawberries': 0.92, 'Canned Tangerines': 0.61, 'Cannelloni': 1.46, 'Cannoli': 2.54, 'Canola Oil': 8.84, 'Cantaloupe': 0.34, 'Cantaloupe Melon': 0.34, 'Capâ€™n Crunch': 4.04, 'Capellini': 3.53, 'Capers': 0.23, 'Capicola': 1.1, 'Capon': 2.29, 'Cappelletti': 1.64, 'Capricciosa Pizza': 2.6, 'Capri-Sun': 0.41, 'Capsicum': 0.27, 'Caramel Cake': 4.75, 'Caramel Popcorn': 3.76, 'Caramel squares': 3.67, 'Caraway Seeds': 3.33, 'Cardamom': 3.11, 'Caribou': 1.59, 'Carlsberg': 0.32, 'Carp': 1.62, 'Carrot': 0.41, 'Carrot Cake': 4.08, 'Carrot Ginger Soup': 0.25, 'Carrot Juice': 0.4, 'Carrot Soup': 0.25, 'Carvel': 2.12, 'Casaba Melon': 0.28, 'Cashew': 5.53, 'Cassava': 1.6, 'Catalina Dressing': 2.82, 'Cauliflower': 0.25, 'Cava': 0.76, 'Caviar': 2.64, 'Cayenne Pepper': 3.18, 'Celebrations': 4.9, 'Celery': 0.16, 'Cellophane Noodles': 3.51, 'Chai': 0.0, 'Chai Tea': 0.0, 'Challah': 2.83, 'Chambord': 3.48, 'Chamomile Tea': 0.0, 'Champagne': 0.75, 'Chapati': 2.4, 'Chard': 0.19, 'Chardonnay': 0.85, 'Chasseur Sauce': 0.45, 'Cheddar': 4.03, 'Cheerios': 3.47, 'Cheese Fondue': 2.28, 'Cheese Pastry': 3.74, 'Cheese Pizza': 2.67, 'Cheese Platter': 3.57, 'Cheese Slices': 3.56, 'Cheese Spread': 2.9, 'Cheese Tortellini': 2.91, 'Cheese Whiz': 2.76, 'Cheeseburger': 2.63, 'Cheesecake': 3.21, 'Cheez-Itâ€™s': 5.33, 'Chenin Blanc': 0.8, 'Cherimoya': 0.75, 'Cherries': 0.5, 'Cherry Coke': 0.44, 'Cherry Jam': 2.5, 'Cherry Juice': 0.45, 'Cherry Pie': 2.6, 'Cherry Tomato': 1.0, 'Cherry Yogurt': 0.97, 'Chess Pie': 4.11, 'Chester': 3.87, 'Chestnut': 2.13, 'Chex': 3.87, 'Chia Seeds': 4.86, 'Chicken': 2.19, 'Chicken Bouillon': 0.04, 'Chicken Breast': 1.63, 'Chicken Breast Fillet': 0.79, 'Chicken Broth': 0.16, 'Chicken Caesar Salad': 1.27, 'Chicken Drumstick': 1.85, 'Chicken Drumsticks': 1.85, 'Chicken Fajita': 1.47, 'Chicken Fat': 8.98, 'Chicken Fried Steak': 1.51, 'Chicken Giblets': 1.58, 'Chicken Gizzards': 1.46, 'Chicken Gumbo Soup': 0.23, 'Chicken Heart': 1.85, 'Chicken Leg': 1.74, 'Chicken Legs': 1.74, 'Chicken Liver': 1.67, 'Chicken Marsala': 0.96, 'Chicken McNuggets': 3.02, 'Chicken Meat': 1.72, 'Chicken Noodle Soup': 0.25, 'Chicken Nuggets': 2.96, 'Chicken Parmesan': 1.1, 'Chicken Pizza': 2.34, 'Chicken Pizziola': 1.41, 'Chicken Pot Pie': 2.23, 'Chicken Salad': 0.81, 'Chicken Sandwich': 2.41, 'Chicken Stock': 0.16, 'Chicken Stomach': 1.48, 'Chicken Teriyaki Sandwich': 1.38, 'Chicken Thigh': 2.29, 'Chicken Thighs': 2.29, 'Chicken Tikka Masala': 0.81, 'Chicken Vegetable Soup': 0.31, 'Chicken Wing': 2.66, 'Chicken Wings': 3.24, 'Chicken with Rice Soup': 0.24, 'Chickpeas': 3.64, 'Chicory': 0.72, 'Chicory Greens': 0.23, 'Chicory Roots': 0.72, 'Chili': 2.82, 'Chili Bean': 0.97, 'Chili con Carne': 1.05, 'Chili Powder': 2.82, 'Chili Sauce': 1.12, 'Chimichanga': 2.32, 'Chinese Cabbage': 0.16, 'Chitterlings': 2.33, 'Chive Cream Cheese': 3.42, 'Chives': 0.3, 'Chocolate': 5.29, 'Chocolate Bar': 5.33, 'Chocolate Cake': 3.89, 'Chocolate Cheerios': 3.67, 'Chocolate Chip Ice Cream': 2.15, 'Chocolate Chips': 4.93, 'Chocolate Cream Pie': 3.04, 'Chocolate Ice Cream': 2.16, 'Chocolate Milk': 0.89, 'Chocolate Milkshake': 1.25, 'Chocolate Mousse': 2.25, 'Chocolate Mousse Cake': 2.6, 'Chocolate Mousse Pie': 2.6, 'Chocolate Muffin': 4.2, 'Chocolate Philadelphia': 2.87, 'Chocolate Spread': 5.41, 'Chocolate Sprinkles': 5.0, 'Chocolate Wine': 2.56, 'Chocolate Yogurt': 1.28, 'Chocos': 3.8, 'Chop Suey': 1.72, 'Chopped Ham': 1.8, 'Chorizo': 4.55, 'Chuck Roast': 1.41, 'Chuck Steak': 1.37, 'Ciabatta': 2.71, 'Ciao Bella': 1.09, 'Cider': 0.49, 'Cider Vinegar': 0.21, 'Cilantro': 0.23, 'Cinnamon': 2.47, 'Cinnamon Bun': 4.36, 'Cinnamon Toast Crunch': 4.33, 'Clam': 1.48, 'Clamato': 0.6, 'Clausthaler (N.A.)': 0.26, 'Clementine': 0.47, 'Cloves': 2.74, 'Club Mate': 0.3, 'Cobb Salad': 1.18, 'Coca Cola': 0.42, 'Coco Pops': 3.76, 'Cocoa Krispies': 3.86, 'Cocoa Pebbles': 3.67, 'Cocoa Powder': 2.28, 'Cocoa Puffs': 4.0, 'Coconut': 3.54, 'Coconut Cake': 3.56, 'Coconut Flakes': 4.56, 'Coconut Milk': 2.3, 'Coconut Oil': 8.57, 'Coconut Water': 0.19, 'Cod': 1.05, 'Cod Liver Oil': 10.0, 'Coffee': 0.01, 'Coffee Cake': 3.31, 'Coffee Creamer': 1.95, 'Coffee Ice Cream': 2.36, 'Cognac': 2.35, 'Cointreau': 3.2, 'Coke': 0.42, 'Coke Zero': 0.01, 'Cola': 0.42, 'Colby Cheese': 3.94, 'Colby-Jack Cheese': 3.94, 'Cold Pack Cheese': 2.46, 'Cold Stone Creamery': 2.32, 'Collard Greens': 0.32, 'Colt 45': 0.44, 'Conchas/Mexican Sweet Bread': 3.53, 'Concord Grape': 0.71, 'Condensed Milk': 3.21, 'Cooked Ham': 1.33, 'Cookie Crisp': 4.0, 'Cookie Dough Ice Cream': 2.0, 'Cookies': 4.88, 'Coors': 0.42, 'Coors Light': 0.29, 'Coors N.A.': 0.18, 'Coriander': 0.23, 'Corn': 3.65, 'Corn Dog': 2.5, 'Corn Flakes': 3.57, 'Corn Flour': 3.61, 'Corn Oil': 8.0, 'Corn Pops': 3.77, 'Corn Syrup': 2.81, 'Corn Waffles': 2.74, 'Cornbread': 1.79, 'Corned Beef': 2.51, 'Corned Beef Hash': 1.64, 'Cornish Hens': 2.59, 'Cornmeal': 3.62, 'Cornstarch': 3.81, 'Corona': 0.42, 'Cottage Cheese': 0.98, 'Cottage Pie': 1.39, 'Cotton Candy': 6.43, 'Cotton Seeds': 5.06, 'Cottonseed Oil': 8.82, 'Count Chocula': 4.07, 'Courgette': 0.17, 'Couscous': 3.76, 'Couverture': 6.0, 'Cracker': 5.02, 'Cracklin Oat Bran': 4.02, 'Cranberries': 0.46, 'Cranberry Apple Juice': 0.67, 'Cranberry Grape Juice': 0.71, 'Cranberry Juice': 0.46, 'Crawfish': 0.82, 'Crayfish': 0.87, 'Cream': 2.42, 'Cream Cheese': 3.42, 'Cream Cheese with Herbs': 3.42, 'Cream of Asparagus Soup': 0.35, 'Cream of Broccoli Soup': 0.45, 'Cream of Celery Soup': 0.37, 'Cream of Chicken Soup': 0.48, 'Cream of Mushroom Soup': 0.39, 'Cream of Onion Soup': 0.44, 'Cream of Potato Soup': 0.3, 'Cream of Tartar': 2.58, 'Cream of Wheat': 3.64, 'Cream Puff': 3.34, 'Cream Sauce': 1.8, 'Cream Yogurt': 1.24, 'Creamed Spinach': 0.74, 'Creamy Chicken Noodle Soup': 0.23, 'Creamy Yogurt': 0.9, 'Creme Fraiche': 3.93, 'Crepes': 2.24, 'Cress': 0.32, 'Croissant': 4.06, 'Croquettes': 1.27, 'Crumb Cake': 4.41, 'Crumpet': 1.78, 'Crunchie McFlurry': 1.74, 'Crunchy Nut': 6.0, 'Crunchy Nut Cornflakes': 6.0, 'Crystal Light': 2.63, 'Crystallized Ginger': 3.35, 'Cubed Steak': 1.99, 'Cucumber': 0.16, 'Cucumber Juice': 0.1, 'Cumberland Sausage': 2.5, 'Cumin': 3.75, 'Cumin Seed': 3.75, 'Cupcake': 3.05, 'Cupcakes': 3.05, 'Curd': 0.98, 'Curly Fries': 3.11, 'Currant Juice': 0.48, 'Currants': 0.56, 'Curry': 3.25, 'Curry Ketchup': 1.24, 'Curry Sauce': 0.26, 'Custard': 1.22, 'Custard Apple': 1.01, 'Custard Powder': 3.37, 'Dairy Milk McFlurry': 1.86, 'Dal': 3.3, 'Dampfnudel': 2.74, 'Dandelion': 0.45, 'Danish Pastry': 3.74, 'Dark Beer': 0.46, 'Dark Rum': 2.16, 'Dates': 2.82, 'Deep Dish Pizza': 2.65, 'Deep-Fried Tofu': 2.71, 'Deviled Eggs': 2.01, 'Dextrose': 3.75, 'Diet Cherry Coke': 0.01, 'Diet Coke': 0.01, 'Diet Dr. Pepper': 0.0, 'Diet Pepsi': 0.0, 'Diet Sunkist': 0.0, 'Diet Yogurt': 0.54, 'Dill': 0.43, 'Dill Weed': 0.43, 'Dim Sum': 1.93, 'Dippin Dots': 2.24, 'Dominos Philly Cheese Steak Pizza': 2.24, 'Donut': 4.03, 'Donut/Doughnut': 4.21, 'Dosa': 0.66, 'Double Cheeseburger': 2.67, 'Double Rainbow': 2.57, 'Doughnut': 4.03, 'Dove': 2.13, 'Dr. Brownâ€™s': 0.53, 'Dr. Pepper': 0.27, 'Dragon Fruit': 0.6, 'Drambuie': 3.58, 'Dried Apricots': 2.41, 'Dried Cranberries': 3.08, 'Dried Figs': 2.49, 'Dried Fruit': 2.43, 'Dried Prunes': 1.07, 'Drumsticks': 2.55, 'Dry Red Wine': 0.85, 'Duck': 3.37, 'Duck Breast': 2.01, 'Duck Egg': 1.85, 'Duck Liver': 1.36, 'Dumpling Dough': 1.24, 'Dumplings': 1.24, 'Durian': 1.47, 'Durum Wheat Semolina': 3.97, 'Dutch Cheese': 3.93, 'Dutch Loaf': 2.68, 'Edam': 3.57, 'Edam Cheese': 3.57, 'Eel': 2.36, 'Egg': 0.97, 'Egg Cream': 0.94, 'Egg Nog': 0.88, 'Egg Noodles': 3.84, 'Egg Roll': 2.5, 'Egg White': 0.13, 'Egg Yolk': 3.22, 'Eggplant': 0.25, 'Eggy Bread': 1.96, 'Elderflower Cordial': 0.29, 'Emmental': 3.57, 'Emmentaler': 3.57, 'Empanada': 3.35, 'Emu': 1.52, 'Enchiladas': 1.68, 'Endive': 0.17, 'Energy-Drink': 0.87, 'English Muffin': 2.27, 'Esrom (Cheese)': 3.22, 'Evaporated Milk': 1.35, 'Evian': 0.0, 'Extra-Firm Tofu': 0.91, 'Fairy Cakes': 4.4, 'Fajita': 1.17, 'Falafel': 3.35, 'Fanta': 0.39, 'Fanta Zero': 0.0, 'Farfalle': 3.58, 'Feijoa': 0.55, 'Fennel': 0.31, 'Fennel Seed': 3.45, 'Fenugreek': 3.23, 'Ferrero Rocher': 5.76, 'Feta': 2.64, 'Feta Cream Cheese': 3.42, 'Fettuccine': 3.53, 'Fiber One': 2.67, 'Figs': 0.74, 'Filet Mignon': 2.07, 'Filet-o-Fish': 2.82, 'Firm Tofu': 0.7, 'Fish and Chips': 1.95, 'Fish Fingers': 2.9, 'Fish Sandwich': 2.73, 'Fish Sticks': 2.9, 'Five Alive': 0.35, 'Flageolet': 0.85, 'Flan': 1.45, 'Flank Steak': 1.94, 'Flapjack': 4.86, 'Flat Iron Steak': 1.37, 'Flatbread': 3.11, 'Flaxseed': 5.34, 'Flaxseed Oil': 8.84, 'Flounder': 0.86, 'Flour': 3.64, 'Flourless Chocolate Cake': 5.09, 'Focaccia': 2.49, 'Fol Epi': 3.88, 'Fontina': 3.89, 'Fortune Cookies': 2.14, 'Four Cheese Pizza': 2.21, 'Frangelico': 2.38, 'Frankfurters': 3.05, 'Freekeh': 5.2, 'French Cruller': 4.12, 'French Dressing': 0.6, 'French Fingerling Potatoes': 0.82, 'French Fries': 3.12, 'French Onion Soup': 0.23, 'French Vanilla Ice Cream': 2.01, 'Fresca': 0.0, 'Fresh Mozzarella': 2.8, 'Fried Bean Curd': 2.71, 'Fried Potatoes': 3.12, 'Fried Rice': 1.86, 'Fried Shrimp': 2.77, 'Friendlyâ€™s': 2.12, 'Froot Loops': 3.79, 'Frosted Cheerios': 3.93, 'Frosted Flakes': 3.67, 'Frosted Mini-Wheats': 3.53, 'Frosties': 3.67, 'Fructose': 3.68, 'Fruit Cake': 3.24, 'Fruit salad': 0.5, 'Fruit Yogurt': 0.97, 'Fruitopia': 1.1, 'Fruity Pebbles': 4.0, 'Full Throttle': 1.1, 'Funnel Cake': 3.07, 'Fusilli': 3.52, 'Fuze': 0.2, 'Fuze Tea': 0.25, 'Galia Melon': 0.23, 'Gamay': 0.78, 'Garlic': 1.49, 'Garlic Bread': 3.5, 'Garlic Cream Cheese': 3.42, 'Garlic Powder': 3.31, 'Garlic Salt': 0.0, 'Garlic Sausage': 1.69, 'Gatorade': 0.23, 'Gelatin': 3.35, 'Genesee Cream Ale': 0.46, 'German Chocolate Cake': 3.7, 'Ghee': 1.2, 'Gherkin': 0.14, 'Gin': 2.63, 'Ginger': 0.8, 'Ginger Ale': 0.35, 'Ginger Beer': 0.42, 'Ginger Tea': 0.0, 'Gingerbread': 3.56, 'Ginkgo Nuts': 1.82, 'Gjetost': 4.66, 'Glass Noodles': 1.92, 'Glenfiddich': 2.3, 'Glucose': 2.86, 'Glucose Syrup': 3.87, 'Gluten': 3.7, 'Gnocchi': 1.33, 'Goa Bean': 4.09, 'Goat Cheese': 3.64, 'Goat Cheese Pizza': 2.19, 'Goat Milk': 0.69, 'Golden Grahams': 4.0, 'Golden Mushroom Soup': 0.65, 'Goose': 3.05, 'Goose Fat': 8.98, 'Goose Liver': 1.33, 'Goose Meat': 2.38, 'Gorgonzola': 3.5, 'Gouda': 3.56, 'Gouda Cheese': 3.56, 'Goulash': 10.09, 'Gourd': 0.14, 'Grand Marnier': 2.53, 'Granola Bars': 4.52, 'Granulated Sugar': 3.87, 'Grape Jelly': 2.55, 'Grape Juice': 0.6, 'Grape Leaves': 0.93, 'Grape Seed Oil': 8.84, 'Grapefruit': 0.42, 'Grapefruit Juice': 0.46, 'Grape-Nuts': 3.62, 'Grapes': 0.69, 'Grated Parmesan': 4.31, 'Gravy': 0.53, 'Greek Dressing': 4.67, 'Greek Yogurt': 0.53, 'Green Beans': 0.31, 'Green Gram': 3.47, 'Green Lentil': 2.57, 'Green Olives': 1.15, 'Green Onion': 0.32, 'Greengage': 0.41, 'Grilled Cheese': 3.5, 'Grilled Cheese Sandwich': 2.88, 'Grilled Chicken Salad': 0.88, 'Grilled Pizza': 2.26, 'Grissini': 4.08, 'Ground Beef': 2.41, 'Ground Chuck': 2.5, 'Ground Cinnamon': 2.47, 'Ground Ginger': 3.35, 'Ground Pork': 2.63, 'Ground Round': 2.12, 'Grouper': 1.18, 'Gruyere': 4.13, 'Guava': 0.68, 'Guinea-Fowl': 1.58, 'Guinness': 0.35, 'Gumdrops': 3.21, 'Gummi Bears': 3.16, 'Haddock': 0.9, 'Hake': 0.71, 'Halibut': 1.11, 'Halloumi': 3.21, 'Ham': 1.45, 'Ham and Cheese Sandwich': 2.41, 'Ham Sandwich': 2.41, 'Ham Sausage': 1.64, 'Hamburger': 2.54, 'Hamburger Sauce': 3.83, 'Hanuta': 5.41, 'Harissa': 0.52, 'Havarti': 3.71, 'Hawaiian Pizza': 1.15, 'Hawaiian Punch': 0.31, 'Hazelnut': 6.28, 'Hazelnut Oil': 8.89, 'Hazelnuts': 6.28, 'Head Cheese': 1.57, 'Healthy Choice': 1.25, 'Heavy Cream': 3.45, 'Heineken': 0.35, 'Hemp Oil': 8.07, 'Herring': 2.03, 'Herring Oil': 9.02, 'Hershey Kisses': 4.71, 'Hi-C': 0.49, 'Hickory Ham': 1.88, 'Hickory Nuts': 6.57, 'Hog Maws': 1.57, 'Hoki': 1.21, 'Hollandaise Sauce': 5.35, 'Honey': 3.04, 'Honey Brown': 0.42, 'Honey Ham': 1.22, 'Honey Mustard Dressing': 4.64, 'Honey Nut Cheerios': 3.93, 'Honey Smacks': 3.7, 'Honeycomb': 3.97, 'Honeydew': 0.36, 'Horchata': 0.54, 'Horseradish': 0.48, 'Hot Chocolate': 0.89, 'Hot Dog': 2.69, 'Hot Dog Buns': 2.79, 'Hot Dogs': 2.78, 'Hot Fudge Sundae': 1.86, 'Hot Pepper': 3.18, 'Hot Sausage': 2.59, 'Hummus': 1.77, 'Hurricane High Gravity': 0.39, 'I can\\â€™t believe it\\â€™s not Butter': 3.57, 'Ice Cream Cake': 2.0, 'Ice Cream Sandwich': 2.37, 'Ice Cream Sundae': 1.42, 'Ice Milk': 1.59, 'Ice Tea': 0.27, 'Iced Tea': 0.27, 'Instant Ramen': 4.36, 'Iodized Salt': 0.0, 'IPA': 0.51, 'Irish Whiskey': 2.33, 'Italian BMT': 1.83, 'Italian Bread': 2.71, 'Italian Cheese': 3.97, 'Italian Dressing': 2.93, 'Italian Sausage': 1.49, 'Jack Danielâ€™s': 1.46, 'Jackfruit': 0.95, 'Jagermeister': 2.5, 'Jaggery': 3.83, 'Jalapeno': 0.13, 'Jambalaya': 1.0, 'Japanese Sweet Potatoes': 0.87, 'Jarlsberg': 3.52, 'Jelly': 2.78, 'Jelly Beans': 3.54, 'Jelly Belly': 3.54, 'Jerky': 4.1, 'Jif Peanut Butter': 5.8, 'Jim Beam': 2.22, 'Jolly Ranchers': 3.85, 'Jolt Cola': 0.44, 'Jordan Almonds': 4.29, 'Jujube': 0.79, 'Juniper': 0.45, 'Just Right': 3.91, 'Kahlua': 1.8, 'Kale': 0.49, 'Kamut': 3.37, 'Karamalz': 0.37, 'Kashi': 3.77, 'Kebab': 2.15, 'Kefir': 0.55, 'Kelloggs Corn Flakes': 3.57, 'Ketchup': 1.0, 'Key Lime Pie': 3.59, 'Keystone Ice': 0.4, 'Keystone Light': 0.29, 'Kidney Beans': 3.37, 'Kielbasa': 3.09, 'King Cake': 3.77, 'Kipper': 2.17, 'Kit Kat': 5.21, 'Kiwi': 0.61, 'Kix': 3.67, 'Knackwurst': 3.07, 'Koelsch': 0.43, 'Kohlrabi': 0.27, 'Kombucha': 0.13, 'Kool-Aid': 0.26, 'Krave': 3.72, 'Kumara': 0.86, 'Kumquat': 0.71, 'Labatt': 0.43, 'Lactose-free Milk': 0.52, 'Lacy Swiss Cheese': 3.21, 'Laffy Taffy': 3.72, 'Lager Beer': 0.43, 'Lamb': 2.02, 'Lamb Meat': 2.02, 'Land Shark': 0.42, 'Landjaeger': 3.52, 'Lard': 8.98, 'Lasagna': 1.32, 'Lasagne': 1.32, 'Lasagne Sheets': 2.71, 'Lassi': 0.75, 'Latkes': 1.89, 'Latte Macchiato': 0.57, 'Layer Cake': 4.02, 'Leek': 0.61, 'Leerdammer': 2.84, 'Leerdammer Cheese': 2.84, 'Lemon': 0.29, 'Lemon Cake': 3.52, 'Lemon Grass': 0.99, 'Lemon Juice': 0.21, 'Lemon Meringue Pie': 2.68, 'Lemon Pie Filling': 1.43, 'Lemonade': 0.5, 'Lentil Soup': 0.56, 'Lentils': 3.53, 'Lettuce': 0.15, 'Licorice': 3.75, 'Life Cereal': 3.75, 'LifeSavers': 5.0, 'Light Beer': 0.29, 'Lima Beans': 0.71, 'Lime': 0.3, 'Lime Juice': 0.21, 'Limeade': 1.28, 'Lindt Chocolate': 5.48, 'Ling': 1.09, 'Linguica': 2.82, 'Linguine': 3.57, 'Linseed Oil': 8.37, 'Liqueur': 2.5, 'Liquor': 2.5, 'Liquorice': 3.75, 'Liver Pate': 3.19, 'Liverwurst': 3.26, 'Lobster': 0.89, 'Lobster Bisque Soup': 1.0, 'Lollipop': 3.92, 'Lotus Seed': 0.89, 'Low Carb Pasta': 2.82, 'Lowenbrau': 0.45, 'Low-Fat Yogurt': 0.63, 'Lucky Charms': 4.06, 'Luncheon Meat': 1.17, 'Lychee': 0.66, 'Lychees': 0.66, 'M&Mâ€™s': 4.79, 'Maasdam Cheese': 3.44, 'Mac and Cheese': 3.7, 'Macadamia Nuts': 7.18, 'Macadamia Oil': 8.19, 'Macaroni': 3.7, 'Macaroni and Cheese': 3.7, 'Mackerel': 2.62, 'Madeira Cake': 3.94, 'Maggi': 1.04, 'Magnolia': 2.3, 'Magnum': 3.0, 'Magnum Almond': 3.15, 'Magnum Double Caramel': 3.55, 'Magnum Double Chocolate': 3.8, 'Magnum Gold': 3.41, 'Magnum White': 2.97, 'Malbec': 0.82, 'Malbec Wine': 0.82, 'Mallard Duck Meat': 2.11, 'Mallard Meat': 2.11, 'Malt Beer': 0.37, 'Malt Powder': 3.61, 'Malted Milk': 4.05, 'Maltesers': 4.98, 'Maltitol': 2.1, 'Maltodextrin': 3.75, 'Malt-O-Meal': 0.51, 'Maltose': 3.44, 'Manchego Cheese': 3.2, 'Mandarin Oranges': 0.53, 'Mango': 0.6, 'Mango Lassi': 0.66, 'Mangosteen': 0.73, 'Manicotti': 3.57, 'Maple Syrup': 2.7, 'Maracuya': 0.97, 'Maraschino Cherries': 1.65, 'Marble Cake': 3.39, 'Margarine': 7.17, 'Margherita Pizza': 2.75, 'Marjoram': 2.71, 'Marmite': 2.25, 'Marron': 2.1, 'Marrow Dumplings': 4.24, 'Mars Bar': 4.48, 'Marsala Wine': 1.0, 'Marshmallow Fluff': 6.66, 'Marshmallows': 3.18, 'Marzipan': 4.11, 'Mascarpone': 4.5, 'Mashed Potatoes': 0.89, 'Matzo Bread': 3.51, 'Mayonnaise': 6.92, 'McDonaldâ€™s Big Mac': 2.56, 'McDonaldâ€™s Cheeseburger': 2.63, 'McDonaldâ€™s Chicken Nuggets': 2.97, 'McDonaldâ€™s Double Cheeseburger': 2.82, 'McDonaldâ€™s Filet-o-Fish': 2.75, 'McDonaldâ€™s McChicken': 2.51, 'McDonaldâ€™s McDouble': 2.52, 'McDonaldâ€™s McMuffi Egg': 2.25, 'McDonaldâ€™s McRib': 2.65, 'McDonaldâ€™s Mighty Wings': 3.08, 'McFlurry': 1.53, 'McFlurry Oreo': 1.86, 'McRib': 2.65, 'Meat Pie': 2.42, 'Meatball Sandwich': 1.61, 'Meatball Soup': 0.49, 'Meatloaf': 0.89, 'Mello Yello': 0.49, 'Menhaden Oil': 9.11, 'Meringue': 2.85, 'Merlot': 0.83, 'Merlot Wine': 0.83, 'Mettwurst': 3.1, 'Michelob Amber Bock': 0.47, 'Michelob Lager': 0.44, 'Michelob Light': 0.32, 'Michelob Ultra': 0.27, 'Michelob Ultra Amber': 0.26, 'Michelob Ultra Lime Cactus': 0.27, 'Midori': 2.67, 'Mike and Ike': 3.6, 'Milk': 0.61, 'Milk Duds': 4.22, 'Milkfish': 1.9, 'Milkshake (dry)': 3.29, 'Milky Way': 4.49, 'Miller Chill': 0.31, 'Miller Genuine Draft': 0.4, 'Miller High Life': 0.4, 'Miller High Life Light': 0.31, 'Miller Lite': 0.27, 'Millet': 3.78, 'Millet Flour': 3.72, 'Millet Gruel': 0.46, 'Milo': 4.09, 'Milwaukeeâ€™s Best': 0.36, 'Milwaukeeâ€™s Best Light': 0.28, 'Minced Onion': 0.4, 'Minced Veal': 1.43, 'Minestrone': 0.34, 'Mini Milk': 1.2, 'Mini-Wheats': 3.53, 'Minneola': 0.64, 'Mint': 0.7, 'Mint Chocolate Chip Ice Cream': 2.39, 'Minute Maid': 0.46, 'Minute Maid Light': 0.02, 'Miso': 1.99, 'Mocca Yogurt': 1.0, 'Molasses': 2.9, 'Molson': 0.42, 'Monkey Bread': 2.9, 'Monkfish': 0.97, 'Monterey': 3.73, 'Monterey Jack Cheese': 3.73, 'Moose': 1.34, 'Moose Meat': 1.34, 'Mortadella': 3.11, 'Moscato Wine': 0.76, 'Mostaccioli': 1.84, 'Mozzarella': 2.8, 'Mozzarella Pizza': 2.49, 'Muenster Cheese': 3.68, 'Muesli': 3.36, 'Muffin': 2.96, 'Mug Root Beer': 0.42, 'Mulberries': 0.43, 'Mulled Wine': 1.96, 'Mullet': 1.5, 'Multi-Grain Bread': 2.65, 'Multigrain Cheerios': 3.8, 'Mung Beans': 0.12, 'Mushroom Pizza': 2.12, 'Mushroom Soup': 0.35, 'Mushrooms': 0.22, 'Muskmelon': 0.34, 'Mussel': 1.72, 'Mustard': 0.6, 'Mustard Greens': 0.27, 'Mustard Oil': 8.84, 'Mustard Sauce': 6.45, 'Mustard Seed': 5.08, 'Mutton': 2.34, 'Mutton Meat': 2.34, 'Naan': 3.1, 'Nachos with Cheese': 3.06, 'Napoli Pizza': 2.02, 'Natto': 2.12, 'Natural Ice': 0.44, 'Natural Light': 0.27, 'Navy Bean': 3.37, 'Nectar': 0.53, 'Nectarine': 0.44, 'Nestea': 0.21, 'Neufchatel': 2.53, 'New York Strip Steak': 1.99, 'New York Style Pizza': 1.69, 'Newcastle': 0.39, 'Non-alcoholic Beer': 0.37, 'Noni': 0.53, 'Nonpareils': 4.75, 'Noodle Soup': 0.34, 'Nori': 0.35, 'Norland Red Potatoes': 0.89, 'Nutella': 5.44, 'Nutmeg': 5.25, 'Nutri-Grain': 3.51, 'Oâ€™Doulâ€™s (N.A.)': 0.19, 'Oat Bran': 2.46, 'Oat Oil': 8.84, 'Oatibix': 4.21, 'Oatmeal': 3.75, 'Oatmeal Cookies': 4.5, 'Oatmeal Raisin Cookies': 4.35, 'Obatzda': 3.03, 'Octopus': 1.64, 'Okara': 0.77, 'Okra': 0.33, 'Old Milwaukee': 0.41, 'Old Milwaukee N.A.': 0.16, 'Olde English': 0.45, 'Olive Cream Cheese': 3.42, 'Olive Loaf': 2.32, 'Olive Oil': 8.84, 'Olive Spread': 5.5, 'Olives': 1.15, 'Omelette': 1.54, 'Onion': 0.4, 'Onion Powder': 3.41, 'Onion Rings': 4.11, 'Onion Soup': 0.23, 'Opera Cake': 3.2, 'Orange': 0.47, 'Orange Chicken': 2.59, 'Orange Juice': 0.46, 'Orange Peel': 0.97, 'Orange Sauce': 1.79, 'Orange Soda': 0.48, 'Orecchiette': 3.7, 'Oregano': 2.65, 'Organic Yogurt': 0.75, 'Orzo': 3.57, 'Ostrich': 1.45, 'Ostrich Meat': 1.45, 'Oven-Roasted Turkey Breast': 1.04, 'Oxtail Soup': 0.28, 'Pabst Blue Ribbon': 0.41, 'Paczki': 3.36, 'Pad Thai': 1.5, 'Paella': 1.56, 'Pale Ale': 0.42, 'Palm Kernel Oil': 8.82, 'Palm Oil': 8.82, 'Pan de Sal': 2.93, 'Pancake': 2.27, 'Pandesal': 2.93, 'Panettone': 3.6, 'Papaya': 0.43, 'Papaya Juice': 0.58, 'Paprika': 2.82, 'Paratha': 3.25, 'Parma Ham': 3.45, 'Parmesan': 4.31, 'Parsley': 0.36, 'Parsnip': 0.75, 'Parsnips': 0.75, 'Passion Fruit': 0.97, 'Passion Fruit Juice': 0.48, 'Pastrami': 1.33, 'Pavlova': 2.94, 'PayDay': 4.62, 'Pea Soup': 0.75, 'Peach': 0.39, 'Peach Cobbler': 0.65, 'Peach Juice': 0.54, 'Peach Nectar': 0.54, 'Peach Pie': 2.23, 'Peach Yogurt': 0.97, 'Peanut Bar': 5.33, 'Peanut Brittle': 1.83, 'Peanut Butter': 5.89, 'Peanut Butter Bars': 3.79, 'Peanut Butter Cookies': 4.75, 'Peanut Butter Sandwich': 4.08, 'Peanut Butter Toast Crunch': 4.31, 'Peanut Oil': 8.57, 'Peanuts': 5.67, 'Pear': 0.57, 'Pear Juice': 0.6, 'Pear Nectar': 0.6, 'Pearl Barley': 3.52, 'Peas': 0.81, 'Pecan': 6.91, 'Pecan Nuts': 6.91, 'Pecan Pie': 4.07, 'Pecans': 6.91, 'Pecorino': 3.87, 'Peking Duck': 2.25, 'Penne': 3.51, 'Penne Rigate': 3.7, 'Pepper': 0.27, 'Pepper Cheese': 1.0, 'Peppermint bark': 5.0, 'Peppermint Extract': 0.0, 'Pepperoni': 4.94, 'Pepperoni Pizza': 2.55, 'Pepsi': 0.44, 'Persimmon': 1.27, 'Pesto': 4.58, 'Pesto Cream Cheese': 3.42, 'Peter Pan Peanut Butter': 6.09, 'Pez': 4.27, 'Pheasant': 2.39, 'Pheasant Breast': 1.33, 'Pheasant Leg': 2.39, 'Pheasant Meat': 2.39, 'Philadelphia Cream Cheese': 3.42, 'Philly Cheese Steak': 2.5, 'Physalis': 0.49, 'Pibb Xtra': 0.4, 'Pickerel': 1.11, 'Pickled Herring': 2.62, 'Pide': 2.68, 'Pie': 2.37, 'Pierogi': 2.0, 'Pig Brain': 1.38, 'Pig Ear': 1.66, 'Pig Fat': 6.38, 'Pig Heart': 1.48, 'Pig Kidney': 1.51, 'Pig Lung': 0.99, 'Pigâ€™s Tail': 3.96, 'Pigâ€™s Trotter': 2.43, 'Pigeon': 1.42, 'Pike': 1.13, 'Pili Nuts': 7.19, 'Pilsner': 0.43, 'Pimento Loaf': 2.65, 'Pine Nuts': 6.73, 'Pineapple': 0.5, 'Pineapple Cream Cheese': 3.42, 'Pineapple Juice': 0.53, 'Pineapple Orange Juice': 0.5, 'Pineapple Upside-Down Cake': 3.19, 'Pink Grapefruit': 0.42, 'Pinot Gris': 0.83, 'Pinot Noir': 0.75, 'Pinto Beans': 3.47, 'Pistachios': 5.62, 'Pita Bread': 2.75, 'Pizza': 2.67, 'Pizza Dough': 2.28, 'Pizza Hut Stuffed Crust Pizza': 2.55, 'Pizza Hut Supreme Pizza': 2.48, 'Pizza Rolls': 2.47, 'Plaice': 0.91, 'Plain Yogurt': 0.61, 'Plantain': 1.22, 'Plantains': 1.22, 'Plum': 0.46, 'Plum Cake': 1.09, 'Plum Jam': 2.5, 'Plum Juice': 0.71, 'Plum Wine': 1.63, 'Polenta': 3.66, 'Polish Sausage': 3.01, 'Pollack': 1.11, 'Pomegranate': 0.83, 'Pomegranate Juice': 0.66, 'Pomelo': 0.38, 'Pop Rocks': 3.58, 'Popcorn': 5.82, 'Poppy Seed': 5.25, 'Poppy Seed Oil': 8.84, 'Poppy Seeds': 5.25, 'Poppy-Seed Cake': 3.94, 'Pork': 1.96, 'Pork Baby Back Ribs': 2.12, 'Pork Bacon': 4.07, 'Pork Belly': 5.18, 'Pork Blade Steak': 2.32, 'Pork Chop': 1.23, 'Pork Chops': 1.96, 'Pork Country-Style Ribs': 2.47, 'Pork Crown Roast': 2.12, 'Pork Cutlet': 1.31, 'Pork Cutlets': 1.31, 'Pork Leg': 2.01, 'Pork Liver': 1.65, 'Pork Loin': 2.04, 'Pork Meatloaf': 2.43, 'Pork Melt': 2.19, 'Pork Ragout': 0.73, 'Pork Rib Roast': 1.59, 'Pork Ribs': 2.92, 'Pork Roast': 2.47, 'Pork Roll': 3.02, 'Pork Sausage': 3.39, 'Pork Shank': 1.72, 'Pork Shoulder': 2.69, 'Pork Shoulder Blade': 2.32, 'Pork Steaks': 1.96, 'Pork Stomach': 2.5, 'Pork Tongue': 2.71, 'Port Wine': 1.6, 'Porter': 0.54, 'Porterhouse Steak': 2.47, 'Post Raisin Bran': 3.22, 'Post Shredded Wheat': 3.47, 'Potato': 0.77, 'Potato Bread': 2.66, 'Potato Dumpling': 1.24, 'Potato Fritter': 1.85, 'Potato Gratin': 1.32, 'Potato Pancakes': 2.68, 'Potato Salad': 1.43, 'Potato Soup': 0.8, 'Potato Starch': 3.31, 'Potato Sticks': 5.22, 'Potato Waffles': 1.67, 'Potato Wedges': 1.23, 'Potatoes au Gratin': 1.32, 'Poularde': 2.0, 'Poultry Seasoning': 3.07, 'Pound Cake': 3.9, 'Poutine': 2.27, 'Powdered Milk': 4.96, 'Powdered Sugar': 3.89, 'Powerade': 0.16, 'Prawn Crackers': 5.27, 'Pretzel': 3.38, 'Pretzel Roll': 3.38, 'Pretzel Sticks': 3.8, 'Prickly Pear': 0.41, 'Probiotic Yogurt': 0.8, 'Profiterole': 3.34, 'Prosciutto': 1.95, 'Prosecco': 0.66, 'Protein Powder': 4.11, 'Provolone': 3.51, 'Puff': 3.67, 'Puff Pastry': 5.58, 'Puffed Rice': 3.83, 'Puffed Wheat': 3.67, 'Pulled Pork Sandwich': 2.11, 'Pumpernickel': 2.5, 'Pumpkin': 0.26, 'Pumpkin Bread': 2.98, 'Pumpkin Cheesecake': 3.4, 'Pumpkin Pie': 2.43, 'Pumpkin Pie Spice': 3.42, 'Pumpkin Seed Oil': 8.8, 'Pumpkin Seeds': 5.6, 'Pumpkin Soup': 0.29, 'Punch': 0.62, 'Purple Majesty Potatoes': 0.72, 'Puy Lentils': 3.45, 'Quail': 2.27, 'Quail Breast': 1.23, 'Quaker Grits': 3.44, 'Quaker Oatmeal': 3.75, 'Quaker Oatmeal Squares': 4.0, 'Quark': 1.45, 'Quattro Formaggi Pizza': 2.48, 'Quince': 0.57, 'Quinoa': 3.68, 'RÃ¶sti': 1.38, 'Rabbit': 1.97, 'Rack of Pork': 2.41, 'Raclette Cheese': 3.57, 'Racoon': 2.55, 'Racoon Meat': 2.55, 'Radish Seeds': 0.43, 'Radishes': 0.16, 'Raisin Bran': 3.22, 'Raisin Bran Crunch': 3.55, 'Raisin Bread': 2.74, 'Raisin Nut Bran': 3.67, 'Raisins': 2.99, 'Rajma': 1.4, 'Rambutan': 0.82, 'Ramen': 4.47, 'Ranch Dressing': 5.1, 'Raspberries': 0.52, 'Raspberry Pie': 2.4, 'Ravioli': 0.77, 'Ready Brek': 3.59, 'Real Butter': 7.2, 'Red Beans': 1.24, 'Red Cabbage': 0.31, 'Red Gold Potatoes': 0.89, 'Red Kidney Bean': 3.37, 'Red Lentils': 3.29, 'Red Pepper': 2.51, 'Red Pepper Pizza': 1.92, 'Red Potatoes': 0.89, 'Red Snapper': 1.28, 'Red Velvet Cake': 3.67, 'Red Wine': 0.85, 'Red Wine Vinegar': 0.19, 'Red Wines': 0.85, 'Redbridge (Gluten-free)': 0.45, 'Redfish': 0.94, 'Reeses Peanut Butter Cups': 5.36, 'Refried Beans': 0.91, 'Reindeer': 2.0, 'Reindeer Meat': 2.0, 'Remoulade Sauce': 6.35, 'Reuben Sandwich': 2.08, 'Rhea': 1.6, 'Rhubarb': 0.21, 'Rhubarb Pie': 2.45, 'Rib Eye Steak': 2.17, 'Rice Bran Oil': 8.89, 'Rice Chex': 3.87, 'Rice Krispies': 3.94, 'Rice Milk': 0.49, 'Rice Pudding': 1.18, 'Ricotta': 1.74, 'Riesling': 0.8, 'Riesling Wine': 0.8, 'Rigatoni': 3.53, 'Ring Bologna': 2.86, 'Roast Beef': 1.87, 'Roast Dinner': 1.98, 'Roast Potatoes': 1.49, 'Roasted Almonds': 4.52, 'Roasted Soybeans': 4.71, 'Rock Sugar': 6.25, 'Rocky Road Ice Cream': 2.57, 'Roll': 3.16, 'Rolled Oats': 3.84, 'Rolling Rock': 0.37, 'Rolling Rock Light': 0.3, 'Rollmops': 1.71, 'Rolo': 4.74, 'Romano': 3.87, 'Root Beer': 0.41, 'Roquefort': 3.69, 'Rose Wine': 0.71, 'Rosemary': 1.31, 'Rosemary Potatoes': 0.93, 'Roti': 2.64, 'Rotini': 3.53, 'Round Steak': 1.82, 'Rum': 2.31, 'Rum Cake': 3.51, 'Rump Steak': 1.71, 'Rusk': 4.1, 'Russet Potatoes': 0.97, 'Russian Banana Potatoes': 0.67, 'Russian Dressing': 4.0, 'Rutabaga': 0.38, 'Rye Bran': 2.81, 'Rye Bread': 2.59, 'Sâ€™mores': 5.0, 'Sacher Torte': 3.52, 'Safflower Oil': 8.57, 'Safflower Seeds': 5.17, 'Saffron': 3.1, 'Sage': 3.15, 'Sago': 3.54, 'Salad Dressing': 4.49, 'Salami': 3.36, 'Salami Pizza': 2.55, 'Salmon': 2.06, 'Salmon Cream Cheese': 3.42, 'Salmon Oil': 9.11, 'Salt': 0.0, 'Salt Meat': 2.86, 'Salt Pork': 2.86, 'Salted Butter': 7.17, 'Sambal Oelek': 0.21, 'Sambuca': 3.33, 'Samosa': 2.14, 'Samuel Adams': 0.45, 'Sandwich': 3.04, 'Sandwich Bread': 2.51, 'Sandwich Cheese': 1.48, 'Sangria': 0.96, 'Sapodilla': 0.83, 'Sardine Oil': 9.02, 'Sardines': 2.08, 'Sauerkraut Juice': 0.14, 'Sausage': 2.3, 'Sausage Pizza': 2.46, 'Sausage Roll': 3.5, 'Sausage Rolls': 2.97, 'Sauvignon Blanc': 0.81, 'Savory': 2.72, 'Savoury Biscuits': 3.47, 'Slops': 1.11, 'Scampi': 0.84, 'Schnitzel': 1.56, 'Schwanâ€™s': 2.46, 'Schweppes Ginger Ale': 0.38, 'Scone': 3.62, 'Scooters': 3.67, 'Scotch': 2.22, 'Scotch Broth': 0.33, 'Sea Bass': 1.24, 'Sea Salt': 0.0, 'Seafood Pizza': 2.45, 'Semi-skimmed Milk': 0.5, 'Semolina': 3.4, 'Semolina Flour': 3.5, 'Semolina Pudding': 0.67, 'Serrano Ham': 3.0, 'Serrano Pepper': 0.32, 'Sesame Ginger Dressing': 4.64, 'Sesame Oil': 8.84, 'Sesame Paste': 5.95, 'Sesame Seeds': 5.73, 'Shad': 2.52, 'Shallots': 0.72, 'Shark': 1.3, 'Shea Oil': 8.84, 'Sheep Cheese': 3.64, 'Shells': 3.53, 'Shepherds Pie': 0.7, 'Sherry': 1.16, 'Shirataki Noodles': 0.18, 'Shiraz': 0.71, 'Shock Top': 0.47, 'Shock Top Raspberry Wheat': 0.5, 'Shortbread': 5.02, 'Shortcrust Pastry': 5.44, 'Shredded Coconut': 5.01, 'Shredded Wheat': 3.4, 'Shreddies': 3.51, 'Shrimp Cocktail': 4.64, 'Shrimp Pizza': 2.09, 'Sicilian Pizza': 2.41, 'Sierra Nevada Strong': 0.62, 'Silken Tofu': 0.55, 'Skim Milk': 0.35, 'Skim Milk Yogurt': 0.56, 'Skippy Peanut Butter': 5.94, 'Skirt Steak': 2.05, 'Skittles': 4.05, 'Sloe Gin': 3.32, 'Sloppy Joe': 0.71, 'Sloppy Joes': 1.54, 'Slurpee': 0.04, 'Slush Puppie': 0.5, 'Smart Start': 3.71, 'Smarties': 3.57, 'Smarties McFlurry': 1.98, 'Smelt': 1.24, 'Smoked Almonds': 5.75, 'Smoked Cheese': 4.1, 'Smoked Ham': 1.07, 'Smoked Salmon': 1.58, 'Smoked Sausage': 3.01, 'Smoked Turkey Breast': 1.04, 'Smoothie': 0.37, 'Smores': 5.0, 'Smuckers Strawberry Jam': 2.5, 'Snickers': 4.84, 'Snickers Ice Cream': 3.6, 'Soda': 0.53, 'Soda Bread': 2.9, 'Soft Cheese': 2.68, 'Soft Serve': 2.22, 'Soft Tofu': 0.61, 'Sole': 0.86, 'Solero': 1.0, 'Sorbitol': 3.75, 'SoufflÃ©': 2.04, 'Sour Cream': 1.81, 'Sour Cream Sauce': 0.6, 'Sour Patch Kids': 3.63, 'Sourdough Bread': 2.89, 'Soursop Fruit': 0.66, 'Souse': 1.57, 'Southern Comfort': 2.47, 'Soy Beans': 1.47, 'Soy Cheese': 2.35, 'Soy Mayonnaise': 3.22, 'Soy Milk': 0.45, 'Soy Noodles': 2.16, 'Soy Nut Butter': 5.62, 'Soy Nuts': 4.71, 'Soy Oil': 8.82, 'Soy Protein Powder': 3.38, 'Soy Sauce': 0.67, 'Soy Yogurt': 0.66, 'Soya Cheese': 2.35, 'Soybean Oil': 8.89, 'Soybeans': 1.47, 'Soynut Butter': 5.62, 'Spaetzle': 3.68, 'Spaghetti': 3.7, 'Spaghetti Bolognese': 1.32, 'Spam': 3.15, 'Spanakopita': 2.46, 'Spare Ribs': 2.38, 'Spareribs': 2.38, 'Sparkling Wine': 1.9, 'Sparks': 0.74, 'Special K': 3.77, 'Special K Chocolatey Delight': 3.88, 'Special K Protein Plus': 3.75, 'Special K Red Berries': 3.45, 'Speculoos': 4.69, 'Spelt': 3.38, 'Spelt Bran': 1.77, 'Spelt Semolina': 3.6, 'Spice Cake': 3.32, 'Spicy Italian': 2.19, 'Spinach': 0.23, 'Spinach Feta Pizza': 2.42, 'Spinach Pizza': 2.34, 'Spinach Tortellini': 3.14, 'Spirelli': 3.67, 'Sponge Cake': 2.89, 'Spring Roll': 2.5, 'Spring Rolls': 2.5, 'Sprinkles': 5.0, 'Sprite': 0.37, 'Sprite Zero': 0.0, 'Spritz Cookies': 5.0, 'Squash': 0.45, 'Squid': 0.92, 'Squirrel': 1.73, 'Squirrel Meat': 1.73, 'Squirt': 0.44, 'St. Pauli Girl': 0.42, 'Standing Rib Roast': 3.33, 'Star Fruit': 0.31, 'Starch': 3.81, 'Starfruit': 0.31, 'Steel Reserve': 0.63, 'Stevia': 0.0, 'Stew Beef': 1.91, 'Stilton Cheese': 3.93, 'Stout': 0.51, 'Stout Beer': 0.51, 'Stracciatella Yogurt': 1.39, 'Strawberries': 0.32, 'Strawberry Cheesecake': 3.27, 'Strawberry Ice Cream': 2.36, 'Strawberry Jam': 2.5, 'Strawberry Jelly': 2.5, 'Strawberry Milkshake': 1.13, 'Strawberry Pie': 2.3, 'Strawberry Preserves': 2.78, 'Strawberry Rhubarb Pie': 2.81, 'Strawberry Sundae': 1.58, 'Strawberry Yogurt': 1.0, 'String Cheese': 2.5, 'Strip Steak': 1.17, 'Strong Beer': 0.55, 'Stuffed Crust Pizza': 2.55, 'Sturgeon': 1.35, 'Subway Club Sandwich': 1.31, 'Succotash': 1.15, 'Sucrose': 3.87, 'Sugar': 4.05, 'Sugar Peas': 0.42, 'Sugar Puffs': 3.79, 'Summer Sausage': 2.98, 'Sunbutter': 6.17, 'Sundae': 2.15, 'Sunflower Butter': 6.17, 'Sunflower Oil': 8.84, 'Sunflower Seeds': 5.84, 'Sunkist': 0.25, 'Surge': 0.48, 'Sushi': 1.5, 'Sweet and Sour Sauce': 1.79, 'Sweet Chestnut': 1.94, 'Sweet Peas': 0.48, 'Sweet Potato': 0.92, 'Sweet Potato Pie': 2.6, 'Sweet Red Wine': 0.81, 'Sweet Rolls': 3.33, 'Sweet White Wine': 0.82, 'Sweet Wines': 0.83, 'Sweetened Condensed Milk': 3.21, 'Sweetener': 3.6, 'Swiss Cheese': 3.8, 'Swiss Roll': 4.39, 'Swordfish': 1.72, 'TaB': 0.0, 'Tabasco': 0.7, 'Taco': 2.17, 'Tagliatelle': 3.7, 'Take 5': 4.76, 'Tamarind': 2.39, 'Tandoori Chicken': 1.13, 'Tang': 3.81, 'Tangerine': 0.53, 'Tangerine Juice': 0.43, 'Tap Water': 0.0, 'Tapenade': 2.33, 'Taro': 1.12, 'Tarragon': 2.95, 'Tarte FlambÃ©e': 2.53, 'Tarte Tatin': 2.1, 'T-Bone Steak': 2.02, 'T-Bone-Steak': 2.21, 'Tea': 0.01, 'Tempeh': 1.93, 'Tequila': 1.1, 'Teriyaki Sauce': 0.89, 'Textured Soy Protein': 5.71, 'Textured Vegetable Protein': 3.33, 'Thai Curry Paste': 1.55, 'Thai Soup': 0.6, 'Thin Crust Pizza': 2.61, 'Thyme': 2.76, 'Tilsit': 3.4, 'Tilt': 0.64, 'Tiramisu': 2.83, 'Tiramisu Cake': 2.91, 'Toast': 2.61, 'Toasties': 3.61, 'Toblerone': 5.25, 'Tofu': 0.76, 'Tomato': 0.18, 'Tomato Juice': 0.17, 'Tomato Paste': 0.82, 'Tomato Puree': 0.38, 'Tomato Rice Soup': 0.47, 'Tomato Sauce': 0.24, 'Tomato Seed Oil': 8.84, 'Tomato Soup': 0.3, 'Tongue': 2.84, 'Tonic Water': 0.35, 'Tortellini': 2.91, 'Tortilla': 2.37, 'Tortilla Bread': 2.65, 'Tortilla Chips': 4.99, 'Tortilla Wrap': 2.71, 'Treacle Tart': 3.69, 'Tres Leches Cake': 2.46, 'Trifle': 1.8, 'Triggerfish': 0.93, 'Triple Sec': 1.53, 'Trix': 4.0, 'Trout': 1.9, 'Tuna': 0.86, 'Tuna Pizza': 2.54, 'Tuna Salad': 1.87, 'Turbot': 1.22, 'Turkey': 1.04, 'Turkey Breast': 1.04, 'Turkey Cutlet': 1.89, 'Turkey Drumsticks': 2.08, 'Turkey Giblets': 1.73, 'Turkey Ham': 1.26, 'Turkey Heart': 1.74, 'Turkey Hill': 2.71, 'Turkey Legs': 2.08, 'Turkey Liver': 1.89, 'Turkey Salami': 1.52, 'Turkey Steak': 1.89, 'Turkey Stomach': 1.48, 'Turkey Wings': 2.21, 'Turmeric': 3.54, 'Turnip Greens': 0.2, 'Turnips': 0.28, 'Twix': 4.95, 'Tzatziki': 1.17, 'Unsalted Butter': 7.17, 'Vanilla Bean': 2.5, 'Vanilla Coke': 0.45, 'Vanilla Cone': 1.62, 'Vanilla Extract': 2.88, 'Vanilla Ice Cream': 2.01, 'Vanilla Milkshake': 1.49, 'Vanilla Sugar': 3.57, 'Vanilla Yogurt': 1.01, 'Veal': 2.82, 'Veal Breast': 2.82, 'Veal Heart': 1.86, 'Veal Kidney': 1.63, 'Veal Leg': 2.11, 'Veal Roast Beef': 1.75, 'Veal Shank': 1.77, 'Veal Shoulder': 1.83, 'Veal Sirloin': 2.04, 'Veal Tenderloin': 2.17, 'Veal Tongue': 2.02, 'Vegemite': 1.8, 'Vegetable Beef Soup': 0.31, 'Vegetable Broth': 0.05, 'Vegetable Cream Cheese': 3.42, 'Vegetable Juice': 0.21, 'Vegetable Oil': 8.0, 'Vegetable Pizza': 2.56, 'Vegetable Shortening': 8.84, 'Vegetable Soup': 0.28, 'Vegetable Stock': 0.05, 'Vegetarian Pizza': 2.56, 'Veggie Burger': 1.81, 'Veggie Delight': 1.38, 'Veggie Patty': 3.9, 'Veggie Pizza': 2.31, 'Venison': 1.64, 'Venison Sirloin': 1.58, 'Vermicelli': 3.68, 'Vermouth': 1.3, 'Victoria Sponge Cake': 2.57, 'Vinaigrette': 1.2, 'Vinegar': 0.18, 'Vodka': 2.31, 'Volvic': 0.0, 'Waffles': 3.12, 'Wahoo': 1.67, 'Walnut Cream Cheese': 3.42, 'Walnut Oil': 8.89, 'Walnuts': 6.54, 'Wasabi': 1.09, 'Water': 0.0, 'Watermelon': 0.3, 'Wedding Cake': 3.81, 'Wedding Soup': 0.53, 'Weetabix': 3.58, 'Weet-Bix': 3.53, 'Weetos': 3.78, 'Weisswurst': 3.13, 'Wendyâ€™s Baconator': 3.04, 'Wendyâ€™s Jr. Bacon Cheeseburger': 2.61, 'Wendyâ€™s Jr. Cheeseburger': 2.25, 'Wendyâ€™s Son of Baconator': 3.21, 'Wheat Beer': 0.45, 'Wheat Bran': 2.16, 'Wheat Germ': 3.82, 'Wheat Germ Oil': 9.29, 'Wheat Gluten': 3.25, 'Wheat Semolina': 3.6, 'Wheat Starch': 3.51, 'Wheaties': 3.67, 'Whipped Cream': 2.57, 'Whisky': 2.5, 'White American': 1.48, 'White Beans': 3.36, 'White Bread': 2.38, 'White Cheddar': 4.03, 'White Grape Juice': 0.75, 'White Pepper': 2.96, 'White Pizza': 2.46, 'White Potatoes': 0.94, 'White Wine': 0.82, 'White Zinfandel': 0.88, 'Whitefish': 1.72, 'Whiting': 1.16, 'Whole Grain Noodles': 3.47, 'Whole Grain Spaghetti': 3.51, 'Whole Grain Wheat': 3.39, 'Whole Milk': 0.61, 'Whole Wheat Bread': 2.47, 'Whole Wheat Flour': 3.4, 'Wholegrain Oat': 3.75, 'Whoopie Pie': 4.0, 'Whopper': 2.31, 'Wild Boar': 1.6, 'Wild Boar Meat': 1.6, 'Wild Duck': 2.11, 'Wild Honey': 2.86, 'Wine': 0.83, 'Winter Squash': 0.34, 'Wisconsin Cheese': 3.89, 'Worcestershire Sauce': 0.78, 'Xylitol': 2.4, 'Yam': 1.18, 'Yam Bean': 0.38, 'Yams': 1.16, 'Yeast (dry)': 3.25, 'Yellow Lentils': 3.04, 'Yellow Tail Wine': 0.71, 'Yerba Mate': 0.62, 'Yogurt': 0.61, 'Yogurt Corner': 1.19, 'Yogurt Dressing': 0.45, 'Yoplait Boston Cream Pie': 0.9, 'Yoplait French Vanilla': 1.0, 'Yoplait Greek Blueberry': 1.0, 'Yoplait Greek Coconut': 1.0, 'Yoplait Greek Strawberry': 1.0, 'Yoplait Greek Vanilla': 1.0, 'Yoplait Harvest Peach': 1.0, 'Yoplait Key Lime Pie': 1.0, 'Yoplait Mango': 1.0, 'Yoplait Mixed Berry': 1.0, 'Yoplait Pina Colada': 1.0, 'Yoplait Strawberry': 1.0, 'Yoplait Strawberry Banana': 1.0, 'Yoplait Strawberry Cheesecake': 1.0, 'Yorkshire Pudding': 5.53, 'Young Gouda': 3.56, 'Yuba': 1.76, 'Yukon Gold Potatoes': 0.82, 'Zander': 0.84, 'Zesty Italian Dressing': 2.67, 'Zinfandel': 0.88, 'Zinger': 2.56, 'Zinger Burger': 2.56, 'Ziti': 3.52, 'Zucchini': 0.17, 'None': 0.0, 'none': 0.0}
                cal = 0.0
                try:
                    for i in range(0,8):  
                        cal += (quantity[i]*((calories[item[i]])))
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


