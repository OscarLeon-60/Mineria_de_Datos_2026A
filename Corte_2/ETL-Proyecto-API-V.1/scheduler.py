import schedule
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_etl():
    logging.info("Ejecutando ETL...")
    subprocess.run(["python", "etl/extractor.py"], check=True)

run_etl()
schedule.every(1).hours.do(run_etl)

while True:
    schedule.run_pending()
    time.sleep(60)
