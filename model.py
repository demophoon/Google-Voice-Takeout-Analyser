#!/usr/bin/env python
# encoding: utf-8

import json

import dateutil.parser

from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from textblob import TextBlob

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    phone = Column(String, unique=True)

    messages = relationship("Message", back_populates='message_to')

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return '<Contact %s (%s)>' % (self.phone, self.name)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    sent = Column(DateTime)
    from_id = Column(Integer, ForeignKey('contacts.id'))
    polarity = Column(Float)
    subjectivity = Column(Float)
    nouns = Column(String)

    message_to = relationship("Contact", back_populates='messages')

    def __init__(self, message, from_id, to, sent):
        self.message = message
        self.from_id = from_id
        self.to = to
        self.sent = sent

    def __repr__(self):
        return '<Message %s>' % (self.message)

if __name__ == '__main__':
    engine = create_engine('sqlite:///texts.sqlite')
    Base.metadata.create_all(engine)
    Session = sessionmaker(autoflush=False)
    Session.configure(bind=engine)
    session = Session()

    contacts = []
    messages = []

    f = open('output.json', 'r')
    conversations = json.loads(f.read())
    for messages in conversations:
        for message in messages:
            if message['number'] not in contacts:
                contact = Contact(message['sender'], message['number'])
                session.add(contact)
                session.flush()
                contacts.append(message['number'])
            tb = TextBlob(message['content'])
            m = Message(
                message['content'],
                contact.id,
                message['to'],
                dateutil.parser.parse(message['timestamp']),
            )
            m.polarity = tb.sentiment.polarity
            m.subjectivity = tb.sentiment.subjectivity
            session.add(m)
            print "%s: Polarity / Subjectivity: (%s / %s)" % (
                m,
                tb.sentiment.polarity,
                tb.sentiment.subjectivity,
            )
        session.flush()
        session.commit()
    print "Done."
