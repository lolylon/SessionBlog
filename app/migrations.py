from app import db
from app.models.post import Post

def upgrade_database():
    with db.engine.connect() as conn:

        conn.execute(db.text("ALTER TABLE post ADD COLUMN sentiment_pos FLOAT DEFAULT 0.0"))
        
        conn.execute(db.text("ALTER TABLE post ADD COLUMN sentiment_neg FLOAT DEFAULT 0.0"))
        
        conn.execute(db.text("ALTER TABLE post ADD COLUMN sentiment_neu FLOAT DEFAULT 0.0"))
        
        conn.execute(db.text("ALTER TABLE post ADD COLUMN sentiment_compound FLOAT DEFAULT 0.0"))
        
        conn.commit()

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade_database()
        print("Database migration completed successfully!")