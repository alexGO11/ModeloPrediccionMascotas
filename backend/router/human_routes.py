from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

import requests
import pandas as pd
import numpy as np
import json
import traceback
import geopandas as gpd
from sqlalchemy import select, and_
from shapely.geometry import mapping
from datetime import datetime, timedelta, timezone

from config.db_connection import engine
from model.human import human
from scripts.process_human_data import prepare_human_data

from shapely.geometry import mapping, Point
import geopandas as gpd

human_routes = APIRouter()

# Function to build from DataFrame el Geojson
def build_geojson(df):
    shapefile_path = "data/codigos_postales.shp"
    gdf = gpd.read_file(shapefile_path)

    # Rename column to make Merge
    gdf = gdf.rename(columns={"COD_POSTAL": "post_code"})
    gdf["post_code"] = gdf["post_code"].astype(str)
    df["post_code"] = df["post_code"].astype(str)

    # Group by postal code and count cases
    cases_per_cp = df.groupby("post_code").size().reset_index(name="cases")

    # Geometry merge with cases by postal code
    merged = gdf.merge(cases_per_cp, on="post_code", how="inner")

    # Geojson Structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for _, row in merged.iterrows():
        # Calculate centroid
        centroid = row["geometry"].centroid

        feature = {
            "type": "Feature",
            "geometry": mapping(Point(centroid.x, centroid.y)),  # We use centroid
            "properties": {
                "post_code": row["post_code"],
                "cases": row["cases"]
            }
        }
        geojson["features"].append(feature)

    return geojson

# Endpoint to add human data to the database
@human_routes.post("/add_human_data")
async def add_human_data(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        df_filtered = prepare_human_data(df)

        with engine.connect() as conn:
            for index, row in df_filtered.iterrows():
                query = human.insert().values(
                    id=str(index),
                    post_code=row['post_code'],
                    disease=row['disease'],
                    date=row['date']
                )
                conn.execute(query)
                conn.commit()
                
        return JSONResponse(content={"message": "Human data added successfully"}, status_code=200)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Endpoint to get human data from the database
@human_routes.post("/get_human_data")
async def get_human_data(request: Request):
    try:
        raw_body = await request.body()
        
        try:
            params = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "El cuerpo no es JSON válido"}, status_code=400)
        
        start_date = datetime.now(timezone.utc)
        end_date = datetime.strptime("2022-01-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
        interval = params["interval"]
        disease = params["disease"]
        
        results = []
        
        with engine.connect() as conn:
            current_date = start_date

            # Tour all dates with temporary jumps = to the interval
            while current_date >= end_date:
                next_date = current_date - timedelta(days=interval)

                query = select(human).where(
                    and_(
                        human.c.date <= current_date,
                        human.c.date > next_date,
                        human.c.disease == disease
                    )
                )

                result = conn.execute(query)
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                df["post_code"] = df["post_code"].fillna(0).astype(int).astype(str).str.zfill(5)
                print(f"HUMAN_ROUTES| Datos obtenidos para el intervalo {next_date} - {current_date}: {len(df)} registros")
                # If there is data, apply the Getis-Uord algorithm and the results are added to the list
                if not df.empty:
                    
                    geojson = build_geojson(df)
                    print("HUMAN_ROUTES| GeoJSON generado")
                    print(f"HUMAN_ROUTES| GeoJSON contiene {len(geojson['features'])} features")
                    # The results are added to the geojsons list
                    results.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "geojson": geojson
                    })

                current_date = next_date
        
        return JSONResponse(content=results, status_code=200)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)