from flask import Flask, render_template, request, redirect, url_for
import boto3
import uuid
from datetime import datetime

# === AWS Configuration ===
AWS_REGION = 'us-east-1'
USER_TABLE = 'moviemagic_users'
BOOKING_TABLE = 'moviemagic_bookings'
SERVICES_TABLE = 'moviemagic_services'  # <- Added services table
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:moviemagic_Topic'

# === Initialize Flask App ===
app = Flask(__name__)

# === AWS Resources (IAM Role via EC2) ===
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)

# === Reference DynamoDB Tables ===
user_table = dynamodb.Table(USER_TABLE)
booking_table = dynamodb.Table(BOOKING_TABLE)
services_table = dynamodb.Table(SERVICES_TABLE)  # <- Added reference

# === Routes ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/dashboard')
def dashboard():
    try:
        # Scan the services table to show movies
        response = services_table.scan()
        movies = response.get('Items', [])
    except Exception as e:
        print("DynamoDB Scan Error:", e)
        movies = []

    return render_template('dashboard.html', movies=movies)

@app.route('/details')
def details():
    movie = request.args.get('movie')
    theater = request.args.get('theater')
    city = request.args.get('city')
    cost = request.args.get('cost')
    return render_template('details.html', movie=movie, theater=theater, city=city, cost=cost)

@app.route('/seats')
def seats():
    return render_template('seats.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        user_email = request.form['email']
        movie = request.form['movie']
        theater = request.form['theater']
        city = request.form['city']
        seats = request.form['seats']
        cost = request.form['cost']

        booking_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Save booking to DynamoDB
        try:
            booking_table.put_item(
                Item={
                    'user_email': user_email,
                    'booking_id': booking_id,
                    'movie': movie,
                    'theater': theater,
                    'city': city,
                    'seats': seats,
                    'cost': cost,
                    'timestamp': timestamp
                }
            )
        except Exception as e:
            print("DynamoDB Error:", e)
            return "Database error. Try again later.", 500

        # Send confirmation via SNS
        message = (
            f"🎟 Booking Confirmed - Movie Magic\n"
            f"Movie: {movie}\n"
            f"Theater: {theater}\n"
            f"City: {city}\n"
            f"Seats: {seats}\n"
            f"Cost: ₹{cost}\n"
            f"Email: {user_email}"
        )

        try:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="Your Movie Magic Booking"
            )
        except Exception as e:
            print("SNS Error:", e)

        return redirect(url_for(
            'success',
            email=user_email,
            movie=movie,
            theater=theater,
            city=city,
            cost=cost,
            seats=seats
        ))

    return render_template('payment.html')

@app.route('/success')
def success():
    return render_template(
        'success.html',
        email=request.args.get('email'),
        movie=request.args.get('movie'),
        theater=request.args.get('theater'),
        city=request.args.get('city'),
        cost=request.args.get('cost'),
        seats=request.args.get('seats')
    )

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)