# cat > ~/s3-image-api/database.py << 'EOF'
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

DB_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ImageHistory(Base):
    __tablename__ = "image_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # 1. 테이블 생성
    init_db()
    print("✅ 테이블 생성 완료")

    # 2. 데이터 삽입 테스트
    db = SessionLocal()
    try:
        test_record = ImageHistory(
            user_id="test_user",
            filename="test.jpg",
            url="https://example.com/test.jpg",
            size=1024
        )
        db.add(test_record)
        db.commit()
        db.refresh(test_record)
        print(f"✅ 삽입 완료: id={test_record.id}, filename={test_record.filename}")

        # 3. 조회 테스트
        records = db.query(ImageHistory).all()
        print(f"✅ 전체 레코드 수: {len(records)}개")
        for r in records:
            print(f"   - [{r.id}] {r.user_id} | {r.filename} | {r.uploaded_at}")

    finally:
        db.close()
        
# EOF