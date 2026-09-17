# Pay Transaction Model
# Chá»©a cÃ¡c thÃ´ng tin vá» giao dá»‹ch thanh toÃ¡n cá»§a hoÃ¡ Ä‘Æ¡n(invoice)
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from infrastructure.databases.base import Base
from sqlalchemy.orm import relationship
class PayTranModel(Base):
    __tablename__ = 'pay_trans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('sell_invoices.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)

    # invoice = relationship("InvoiceModel", back_populates="payments")

    def __init__(self, invoice_id, amount, payment_method):
        self.invoice_id = invoice_id
        self.amount = amount
        self.payment_method = payment_method
