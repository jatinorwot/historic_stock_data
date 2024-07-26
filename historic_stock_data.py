from smartApi.smartConnect import SmartConnect
import pandas as pd
import logging
import time
from datetime import datetime, timedelta



############## ENTER THE DETAILS BELOW AS DIRECTED ##################

api_key = 'your_api_key_here'
username = 'your_username_here'
pwd = 'your_passwd_here'
token="your_token_here"


exchange= "NSE"         ######### SPECIFY YOUR EXCHANGE #########
symboltoken= "2885"     ########### YOUR SYMBOL TOKEN ##########
interval= "THREE_MINUTE"    ########TIME INTERVAL FOR THE CANDLE ########
fromdate= "2024-06-25 09:00"   #### FROM AND TO DATE  ,DATE PATTERN: " YYYY-MM-YY HH:MM " #######
todate= "2024-06-25 10:17"    ####### TO DATE, PATTERN SAME AS ABOVE ###########

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

smartApi = SmartConnect(api_key)
try:
    token = token
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

def generate_session(client_id, password, totp):
    try:
        data = smartApi.generateSession(client_id, password, totp)
        if 'data' in data and 'jwtToken' in data['data']:
            session_token = data['data']['jwtToken']
            logger.info("Session generated successfully")
            return session_token
        else:
            logger.error("Failed to generate session")
            if 'message' in data:
                logger.error(f"Error message: {data['message']}")
            raise Exception("Session generation failed")
    except Exception as e:
        logger.error(f"Error during session generation: {e}")
        raise e

session_token = None
retry_count = 3

for attempt in range(retry_count):
    try:
        session_token = generate_session(username, pwd, totp)
        if session_token:
            break
    except Exception as e:
        logger.error(f"Attempt {attempt + 1} failed: {e}")
        if attempt < retry_count - 1:
            logger.info("Retrying...")
            time.sleep(5)  # wait before retrying
        else:
            logger.error("All attempts to generate session failed.")


            raise e



historicParam = {
    "exchange": exchange,
    "symboltoken": symboltoken,
    "interval": interval,
    "fromdate": fromdate,
    "todate": todate
}

# Fetch the candle data
try:
    candle_data = smartApi.getCandleData(historicParam)
except Exception as e:
    print("Historic API failed: {}".format(e))
    exit()

columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
df = pd.DataFrame(candle_data['data'], columns=columns)

csv_file = 'candle_data.csv'

df.to_csv(csv_file, index=False)



print(f"Candle data saved to {csv_file}")


