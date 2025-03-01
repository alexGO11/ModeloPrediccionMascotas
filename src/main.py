import argparse
from datetime import datetime, timedelta
import subprocess
import sys
import os
import pandas as pd
from tqdm import tqdm

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from database.services.database_service import DatabaseService
from database.models import PostCode, AdjacentPostcode, Test

def correct_pc(value):
    if not isinstance(value, str) and len(value) == 5:
        raise argparse.ArgumentTypeError("Postal code must have 5 digits")
    return value


def update_database():
    db_service = DatabaseService()

    df_insertion = pd.read_csv("data/processed/process_data.csv", na_values=[""])
    df_insertion_grouped = pd.read_csv("data/processed/grouped_pc.csv")

    print("Inserting tests in database...")
    for index, row in tqdm(df_insertion.iterrows(), total=len(df_insertion), desc="Insertando tests"):
        date_done = row['Date']
        desease = row['Name test']
        value_test = row['Value test']
        pet_sex = row['Pet sex'] if not pd.isna(row["Pet sex"]) else None
        pet_age = int(row['Pet age']) if not pd.isna(row["Pet age"]) else None
        city = row['City'] if not pd.isna(row["City"]) else None
        post_code = row['Postal code']

        tqdm.write(f"Valores: {index}, {post_code}, {date_done}, {desease}, {value_test}, {pet_age}, {city}, {pet_sex}")
        test = Test(index, post_code, date_done,desease, value_test, city, pet_age, pet_sex)
        db_service.insert_test(test)
    
    print("Inserting post codes in database...")
    for index, row in tqdm(df_insertion_grouped.iterrows(), total=len(df_insertion_grouped), desc="Insertando códigos postales"):
        post_code_n = row["Postal code"]
        n_positives = row["n_positives"]

        pc = PostCode(post_code_n, n_positives)
        db_service.insert_post_code(pc)

def main():
    parser = argparse.ArgumentParser(prog="GetisOrd script", description="GetisOrd python script to execute different pet cases")

    # Opciones (flags)
    parser.add_argument("-a", "--all-cases", help="Run GetisOrd with all pet cases ignoring place and date")
    parser.add_argument(
        "-d", 
        "--date", 
        nargs=2, 
        metavar=("DATE", "N_MONTHS"),
        help="Specify the date in format (YYYY-MM-DD) and how many months from now on you want to calculate")
    parser.add_argument(
        "-p",
        "--postal-code",
        type=correct_pc,
        help="Specify a postal code"
    )
    parser.add_argument(
        "-u",
        "--update-database",
        action="store_true",
        help="Forces the app to update sql database from processed_data.csv")

    # Parsear argumentos
    args = parser.parse_args()

    if not args.date and not args.postal_code:
        args.all_cases = True  
    if args.all_cases:
        subprocess.run(["python", "getisordGlobal.py"])

    if args.date:
        try:
            fecha_str, meses_str = args.date
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")  # Convertir a fecha
            meses = int(meses_str)  # Convertir a entero
            nueva_fecha = fecha + timedelta(days=meses * 30)  # Aproximar meses a días
            print(f"Fecha original: {fecha.strftime('%Y-%m-%d')}")
            print(f"Meses añadidos: {meses}")
            print(f"Nueva fecha: {nueva_fecha.strftime('%Y-%m-%d')}")
        except ValueError as e:
            print(f"Error al procesar --date: {e}")

    # Procesar --postal-code
    if args.postal_code:
        subprocess.run(["python", "getisordPerPC.py"])

    # Procesar --postal-code
    if args.update_database:
        update_database()

if __name__ == "__main__":
    main()