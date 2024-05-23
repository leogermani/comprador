from app import db,app
from datetime import datetime

class User(db.Model):
    phone = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    thread_id = db.Column(db.String(50), unique=True, nullable=False)
    last_message_received = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.name}>'

    @classmethod
    def find_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()

    @classmethod
    def create_user(cls, phone, thread_id, name=''):
        new_user = cls(phone=phone, thread_id=thread_id, name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def update_name(self, new_name):
        self.name = new_name
        db.session.commit()

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    quote_items = db.relationship('QuoteItem', backref='quote', lazy=True)

    @staticmethod
    def create_new_quote():
        new_quote = Quote()
        db.session.add(new_quote)
        db.session.commit()
        return new_quote.id

    def get_quote_items(self):
        return QuoteItem.query.filter_by(quote_id=self.id).all()

    @staticmethod
    def list_all_quotes():
        return Quote.query.all()

class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(200), nullable=False)

    @staticmethod
    def add_item_to_quote(quote_id, quantity, item_name):
        new_item = QuoteItem(quote_id=quote_id, quantity=quantity, item_name=item_name)
        db.session.add(new_item)
        db.session.commit()
        return new_item.id


if __name__ == "__main__":

    # Run this file directly to create the database tables.
    print ("Creating database tables...")
    with app.app_context():
        db.create_all()
    print( "Done!")