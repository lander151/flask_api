import geojson
from flask import jsonify
from geoalchemy2.shape import to_shape


def formatted_results(data):
    return {
        'id': data.id,
        'country': data.country,
        'region': data.region,
        'province': data.province,
        'county': data.county,
        'cityName': data.city,
        'geom': get_geom(data.geom),
        'geometry': get_lat_lon(data.geom)
    }


def get_lat_lon(geom):
    shp_geom = to_shape(geom)
    centroid = shp_geom.centroid
    return centroid.y, centroid.x


def get_geom(geom):
    shp_geom = to_shape(geom)

    return geojson.Feature(geometry=shp_geom, properties={})
