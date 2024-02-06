from flask import current_app as app
from paralympics.schemas import RegionSchema, EventSchema
from flask import request
# flask --app paralympics run --debug

# Flask-Marshmallow Schemas
regions_schema = RegionSchema(many=True)
region_schema = RegionSchema()
events_schema = EventSchema(many=True)
event_schema = EventSchema()

from paralympics import db
from paralympics.models import Region

@app.get("/regions")
def get_regions():
    """Returns a list of NOC region codes and their details in JSON."""
    # Select all the regions using Flask-SQLAlchemy
    all_regions = db.session.execute(db.select(Region)).scalars()
    # Get the data using Marshmallow schema (returns JSON)
    result = regions_schema.dump(all_regions)
    # Return the data
    return result

@app.get('/regions/<code>')
def get_region(code):
    """ Returns one region in JSON.

    :param code: The NOC code of the region to return
    :param type code: str
    :returns: JSON
    """
    # Query structure shown at https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/queries/#select
    region = db.session.execute(db.select(Region).filter_by(NOC=code)).scalar_one()
    # Dump the data using the Marshmallow region schema; '.dump()' returns JSON.
    result = region_schema.dump(region)
    # Return the data in the HTTP response
    return result


from paralympics.models import Event

@app.get("/events/<event_id>")
def get_event(event_id):
    """ Returns the event with the given id JSON.

    :param event_id: The id of the event to return
    :param type event_id: int
    :returns: JSON
    """
    event = db.session.execute(db.select(Event).filter_by(id=event_id)).scalar_one()
    result = event_schema.dump(event)
    return result

# POST method
@app.post('/events')
def add_event():
    """ Adds a new event.
    
    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow 
    event_schema.load()

    :returns: JSON"""
    ev_json = request.get_json()
    event = event_schema.load(ev_json)
    db.session.add(event)
    db.session.commit()
    return {"message": f"Event added with id= {event.id}"}
# POST a new region to http://127.0.0.1:5000/regions For
# HTTPie: `http POST 127.0.0.1:5000/regions NOC=ZZZ region=ZedZedZed`

#Delete method
@app.delete('/events/<int:event_id>')
def delete_event(event_id):
    """ Deletes an event.
    
    Gets the event from the database and deletes it.

    :returns: JSON"""
    event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    db.session.delete(event)
    db.session.commit()
    return {"message": f"Event deleted with id= {event_id}"}
#DELETE the "ZZZ" region using URL http://127.0.0.1:5000/regions/ZZZ. For
# HTTPie: `http DELETE 127.0.0.1:5000/regions/ZZZ`


# Update a route
from flask import make_response

@app.patch("/events/<event_id>")
def event_update(event_id):
    """Updates changed fields for the event.

    """
    # Find the event in the database
    existing_event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    # Get the updated details from the json sent in the HTTP patch request
    event_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes from the json
    event_updated = event_schema.load(event_json, instance=existing_event, partial=True)
    # Commit the changes to the database
    db.session.add(event_updated)
    db.session.commit()
    # Return json showing the updated record
    updated_event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    result = event_schema.jsonify(updated_event)
    response = make_response(result, 200)
    response.headers["Content-Type"] = "application/json"
    return response