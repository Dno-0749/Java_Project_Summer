from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Float
from infrastructure.databases.base import Base
class SellProductModel(Base):
    __tablename__ = 'sell_products'
    
    # Sell Product Model
    # Chá»©a cÃ¡c thÃ´ng tin vá» sáº£n pháº©m bÃ¡n ra trong hoÃ¡ Ä‘Æ¡n(invoice)
    id = Column(Integer, primary_key=True)
    product_name = Column(String(100))
    description = Column(String(255))
    product_code = Column(String(100), unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
