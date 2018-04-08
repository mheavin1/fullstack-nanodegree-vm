from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, Item

engine = create_engine('sqlite:///sportscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# categories
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

category2 = Category(name="Basketball")
session.add(category2)
session.commit()

category3 = Category(name="Baseball")
session.add(category3)
session.commit()

category4 = Category(name="Rock Climbing")
session.add(category4)
session.commit()


# items
item1 = Item(description="A left and right shinguard",
             title="Shinguards", category=category1)
session.add(item1)
session.commit()


item2 = Item(description="Learn how to flop like the pros in Bundesliga",
             title="Flopping Manual", category=category1)
session.add(item2)
session.commit()

item3 = Item(description="Official league basketball",
             title="Basketball", category=category2)
session.add(item3)
session.commit()

item4 = Item(description="Outdoor use basketball",
             title="Basketball", category=category2)
session.add(item4)
session.commit()

item5 = Item(description="Official youth baseball bat",
             title="Baseball Bat", category=category3)
session.add(item5)
session.commit()

item6 = Item(description="Adult size baseball glove",
             title="Baseball Glove", category=category3)
session.add(item6)
session.commit()

item7 = Item(description="Rock climbing shoes",
             title="Climbing Shoes", category=category1)
session.add(item7)
session.commit()


item8 = Item(description="Aluminum carabiner for climbing",
             title="Carabiner", category=category1)
session.add(item8)
session.commit()
