import argparse
from datetime import datetime, timedelta
import subprocess
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from database.services.database_service import DatabaseService
from database.models.post_code import PostCode

def correct_pc(value):
    if not isinstance(value, str) and len(value) == 5:
        raise argparse.ArgumentTypeError("Postal code must have 5 digits")
    return value


def prueba():
    # Crear una instancia del servicio de base de datos
    db_service = DatabaseService()

    # Insertar un código postal
    new_post_code = PostCode(post_code=28002, n_cases=15, estimation_pets=200)
    db_service.insert_post_code(new_post_code)

    # Obtener todos los códigos postales
    post_codes = db_service.get_all_post_codes()
    for pc in post_codes:
        print(pc)

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
        prueba()

if __name__ == "__main__":
    main()