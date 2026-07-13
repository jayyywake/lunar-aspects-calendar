import ephem
import math
import datetime
from ics import Calendar, Event

def get_ecliptic_lon(body, date):
    """Calculates the Tropical Zodiac longitude (0-360) for a celestial body."""
    body.compute(date)
    ecl = ephem.Ecliptic(body)
    return math.degrees(ecl.lon)
    
def get_angular_separation(lon1, lon2):
    """Calculates the absolute shortest distance between two degrees on a circle."""
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff

def generate_lunar_aspects():
    cal = Calendar()
    
    # Start exactly at the top of the current hour
    today = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    
    # Traditional visible planets
    planets = {
        'Sun': ephem.Sun(),
        'Mercury': ephem.Mercury(),
        'Venus': ephem.Venus(),
        'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn': ephem.Saturn()
    }
    
    # The major Ptolemaic aspects
    aspects = {
        0: "Conjunction",
        60: "Sextile",
        90: "Square",
        120: "Trine",
        180: "Opposition"
    }
    
    # 30-day rolling window (checking every hour = 720 checks per planet)
    # This keeps the file small and Apple Calendar fast.
    for i in range(30 * 24):
        current_time = today + datetime.timedelta(hours=i)
        next_time = current_time + datetime.timedelta(hours=1)
        
        moon_lon_now = get_ecliptic_lon(ephem.Moon(), current_time)
        moon_lon_next = get_ecliptic_lon(ephem.Moon(), next_time)
        
        for p_name, p_body in planets.items():
            p_lon_now = get_ecliptic_lon(p_body, current_time)
            p_lon_next = get_ecliptic_lon(p_body, next_time)
            
            sep_now = get_angular_separation(moon_lon_now, p_lon_now)
            sep_next = get_angular_separation(moon_lon_next, p_lon_next)
            
            # Check if the angular separation crosses an exact aspect degree 
            # within this specific 1-hour window
            for aspect_deg, aspect_name in aspects.items():
                if (sep_now <= aspect_deg and sep_next >= aspect_deg) or \
                   (sep_now >= aspect_deg and sep_next <= aspect_deg):
                    
                    e = Event()
                    # Clean, emoji-free text as requested previously
                    e.name = f"Moon {aspect_name} {p_name}"
                    e.begin = current_time
                    e.end = next_time 
                    cal.events.add(e)
                    
    with open("lunar_aspects.ics", "w") as f:
        f.writelines(cal.serialize_iter())

if __name__ == "__main__":
    generate_lunar_aspects()
