#!/usr/bin/env python
# encoding: utf-8

import json

import dateutil.parser

from sqlalchemy import (
    Column,
    Table,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from textblob import TextBlob

Base = declarative_base()

noun_phrase_to_message_table = Table(
    'noun_phrase_to_message_table',
    Base.metadata,
    Column('noun_phrase_id', Integer, ForeignKey('noun_phrases.id')),
    Column('message_id', Integer, ForeignKey('messages.id')),
)


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String, unique=True)

    messages = relationship("Message", back_populates='message_to')

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return '<Contact %s (%s)>' % (self.phone, self.name)


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    sent = Column(DateTime)
    from_id = Column(Integer, ForeignKey('contacts.id'))
    to = Column(String)
    polarity = Column(Float)
    subjectivity = Column(Float)

    message_to = relationship("Contact", back_populates='messages')
    nouns = relationship(
        "NounPhrase",
        secondary=noun_phrase_to_message_table,
        backref='messages',
    )

    def __init__(self, message, from_id, to, sent):
        self.message = message
        self.from_id = from_id
        self.to = to
        self.sent = sent

    def __repr__(self):
        return '<Message %s>' % (self.message, )


class NounPhrase(Base):
    __tablename__ = 'noun_phrases'

    id = Column(Integer, primary_key=True)
    phrase = Column(String)

    def __init__(self, phrase):
        self.phrase = phrase

    def __repr__(self):
        return "<Noun Phrase %s>" % (self.phrase, )


def import_data():
    session = create_session()

    contacts = {}
    nouns = {}
    messages = []

    f = open('output.json', 'r')
    conversations = json.loads(f.read())
    for messages in conversations:
        for message in messages:
            if message['number'] not in contacts:
                contact = Contact(message['sender'], message['number'])
                session.add(contact)
                session.flush()
                contacts[message['number']] = contact
            tb = TextBlob(message['content'])
            final_nouns = []
            for noun in tb.noun_phrases:
                if noun not in nouns:
                    n = NounPhrase(noun)
                    session.add(n)
                    session.flush()
                    nouns[noun] = n
                final_nouns.append(nouns[noun])
            m = Message(
                message['content'],
                contacts[message['number']].id,
                message['to'],
                dateutil.parser.parse(message['timestamp']),
            )
            m.polarity = tb.sentiment.polarity
            m.subjectivity = tb.sentiment.subjectivity
            m.nouns = final_nouns
            session.add(m)
            print "%s: Polarity / Subjectivity: (%s / %s), Nouns: %s" % (
                m,
                tb.sentiment.polarity,
                tb.sentiment.subjectivity,
                tb.noun_phrases,
            )
        session.flush()
        session.commit()
    print "Done."


def create_session():
    engine = create_engine('sqlite:///texts.sqlite')
    Base.metadata.create_all(engine)
    Session = sessionmaker(autoflush=False)
    Session.configure(bind=engine)
    return Session()
