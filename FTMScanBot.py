import requests, creds, time, asyncio
#testnetURL = "https://testnet.FTMScan.com/address/api?"
morb_token = ""
empty_token = ""
credentials=creds.get_credentials()
decimal_place = 10**18

Debug=False

last_winning_block= creds.get_last_previous_block()
testNetUrlDebug = "https://testnetFTMScan.com/api?"
testnetURL = "https://api.FTMScan.com/api?"


testnet_token = "0x13139038956C8a931dCF891A4199F5e7eFa320f9"
morb_token = "0x815351731EAB60e617ec4AcfaA927dc3f657B216"

empty_token = "0x0000000000000000000000000000000000000000"
jackpot_min_amt_changed = "0xaf059ee9d42c1ffcd90b59907d307cfab29e5d2ecf6402a5174ad8d4ec4e401b"
jackpot_time_extended = "0xa8162f194f354dc15e429cc707c82c54a8a66cd6415e8e71670f4f404caccc00"
bought_morbius = "0x0000000000000000000000006913f60a53f5408df3175b306dd943e83b3a284e"
its_morbin_time = "0xe6e35173318ce029f42a2f07d65a76cfae9604c672a3c8160109fe4886bdfcbc"
buy_back_for_morbin_time = "0x5e78eb00bb758809ccd7dd288bf7450dd825f4661703d21faa7e3cc392fb571b"
jackpot_award = "0xbb60574db333fcc16f66d64cf8f428581daaf704cf6a01e321d264b6cc0793e6"
jackpot_buyback = "0xe829b1159d9d807a90e22e34bb4facfffdb5c01d978bf32a7b6a7787851aaa81"
ftm_api_key = credentials["FTMScanAPIKey"]
decimal_place = 10 ** 18


#if Debug:
    #testnetUrl = testNetUrlDebug
    #morb_token = testnet_token

async def get_jackpot_buyback():
    jackpot_buyback_result = {}
    print("get_jackpot_buyback")
    jackpot_buyback_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&sort=desc&topic0={jackpot_buyback}&apikey={ftm_api_key}"
    
    jackpot_buyback_json = requests.get(jackpot_buyback_get_request).json()
    jackpot_buyback_data = await parse_hex(jackpot_buyback_json['result'][len(jackpot_buyback_json['result'])-1]['data'].split('x')[1])
    jackpot_buyback_result['burned_morb'] = float.fromhex(jackpot_buyback_data[0]) /float(decimal_place)
    jackpot_buyback_result['total_burned_morb'] = float.fromhex(jackpot_buyback_data[1]) / float(decimal_place)
    print('jackpot_buyback',jackpot_buyback_result)
    return jackpot_buyback_result
    
async def get_time_extended():
   
    Time_to_morb_result = {}
    jackpot_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&sort=desc&topic0={jackpot_time_extended}&apikey={ftm_api_key}"
    
    jackpot_json = requests.get(jackpot_get_request).json()
    jackpot_data = await parse_hex(jackpot_json['result'][len(jackpot_json['result'])-1]['data'].split('x')[1])
    Time_to_morb_result["last_block"] = jackpot_json['result'][0]["blockNumber"]
    iTStamp = jackpot_json["result"][0]["timeStamp"]
    print(jackpot_json)
    Time_to_morb_result["timestamp"]                = int(float.fromhex(iTStamp.split('x')[1]))
    Time_to_morb_result["address"]                  ="0x"+jackpot_data[0][-40:]
    Time_to_morb_result["jackpot_amount_FTM"]       = float.fromhex(jackpot_data[2]) /float(decimal_place)
    Time_to_morb_result["jackpot_amount_dollar"]    = float.fromhex(jackpot_data[3]) / float(decimal_place)
    Time_to_morb_result["jackpot_time"]             = int(float.fromhex(jackpot_data[4]))
    return Time_to_morb_result

async def get_jackpot():
    print("get_jackpot_award()")
    try:
        jackpot_award_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&topic0={jackpot_award}&apikey={ftm_api_key}"
        print(jackpot_award_get_request)
        jackpot_award_json = requests.get(jackpot_award_get_request).json()['result']
        jackpot_award_json = jackpot_award_json[len(jackpot_award_json)-1]
        jackpotAward_result = {}
        jackpot_award_data = await parse_hex(jackpot_award_json['data'].split('x')[1])
        print(jackpot_award_json)
        jackpotAward_result["address"] = "0x"+jackpot_award_data[0][-40:]                        #
        jackpotAward_result["block"] = jackpot_award_json["blockNumber"]
        jackpotAward_result["ftm_award"]            = float.fromhex(jackpot_award_data[1])  / float(decimal_place)
        jackpotAward_result["ftm_buyback"]          = float.fromhex(jackpot_award_data[2])  / float(decimal_place)
        jackpotAward_result["count"]                = int(float.fromhex(jackpot_award_data[3]) )
        jackpotAward_result["total_ftm"]            = float.fromhex(jackpot_award_data[4])  / float(decimal_place)
        jackpotAward_result["total_dollar"]         = float.fromhex(jackpot_award_data[5])      /float(decimal_place)
        jackpotAward_result["total_ftm_burned"]     = float.fromhex(jackpot_award_data[6])  / float(decimal_place)
        jackpotAward_result["ftm_balance"]          = float.fromhex(jackpot_award_data[7]) / float(decimal_place)
        jackpotAward_result["dollar_balance"]       = float.fromhex(jackpot_award_data[8]) / float(decimal_place)
        jackpotAward_result["timestamp"]          = int(float.fromhex(jackpot_award_data[9]))
        print("jackpot award: ",jackpotAward_result)
        return jackpotAward_result
    except:
        return None

async def get_prev_jackpot():
    print("get_jackpot_award()")
    try:
        jackpot_award_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&topic0={jackpot_award}&apikey={ftm_api_key}"
        print(jackpot_award_get_request)
        jackpot_award_json = requests.get(jackpot_award_get_request).json()['result']
        jackpot_award_json = jackpot_award_json[len(jackpot_award_json)-2]
        jackpotAward_result = {}
        jackpot_award_data = await parse_hex(jackpot_award_json['data'].split('x')[1])
        print(jackpot_award_json)
        jackpotAward_result["address"] = "0x"+jackpot_award_data[0][-40:]                        #
        jackpotAward_result["block"] = jackpot_award_json["blockNumber"]
        jackpotAward_result["ftm_award"]            = float.fromhex(jackpot_award_data[1])  / float(decimal_place)
        jackpotAward_result["ftm_buyback"]          = float.fromhex(jackpot_award_data[2])  / float(decimal_place)
        jackpotAward_result["count"]                = int(float.fromhex(jackpot_award_data[3]) )
        jackpotAward_result["total_ftm"]            = float.fromhex(jackpot_award_data[4])  / float(decimal_place)
        jackpotAward_result["total_dollar"]         = float.fromhex(jackpot_award_data[5])      /float(decimal_place)
        jackpotAward_result["total_ftm_burned"]     = float.fromhex(jackpot_award_data[6])  / float(decimal_place)
        jackpotAward_result["ftm_balance"]          = float.fromhex(jackpot_award_data[7]) / float(decimal_place)
        jackpotAward_result["dollar_balance"]       = float.fromhex(jackpot_award_data[8]) / float(decimal_place)
        jackpotAward_result["timestamp"]          = int(float.fromhex(jackpot_award_data[9]))
        print("jackpot award: ",jackpotAward_result)
        return jackpotAward_result
    except:
        return None
async def get_morbinTime():
    print("get_morbinTime()")
    try:    
        morbinTime_result = {}
        morbin_time_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&topic0={its_morbin_time}&apikey={ftm_api_key}"
        
        morbin_time_json = requests.get(morbin_time_get_request).json()['result']
        morbin_time_json = morbin_time_json[len(morbin_time_json)-1]
        print(morbin_time_json)
        morbinTime_result["block"] = morbin_time_json["blockNumber"]
        morbin_time_data = await parse_hex(morbin_time_json['data'].split('x')[1])
        morbinTime_result["ftm_buyback"]    = float.fromhex(morbin_time_data[0]) / float(decimal_place)
        morbinTime_result["count"]          = int(float.fromhex(morbin_time_data[1]))
        morbinTime_result["total_ftm"]      = float.fromhex(morbin_time_data[2]) / float(decimal_place)
        morbinTime_result["jackpot_ftm"]    = float.fromhex(morbin_time_data[3]) / float(decimal_place)
        morbinTime_result["jackpot_dollar"] = float.fromhex(morbin_time_data[4]) / float(decimal_place)
        morbinTime_result["timestamp"]      = int(float.fromhex(morbin_time_data[5]))
        print("morbinTime result",morbinTime_result)
        return morbinTime_result
    except:
        print("failed to get morbinTime()")
        return None

async def get_prev_morbinTime():
    print("get_morbinTime()")
    try:    
        morbinTime_result = {}
        morbin_time_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&topic0={its_morbin_time}&apikey={ftm_api_key}"
        
        morbin_time_json = requests.get(morbin_time_get_request).json()['result']
        morbin_time_json = morbin_time_json[len(morbin_time_json)-2]
        print(morbin_time_json)
        morbinTime_result["block"] = morbin_time_json["blockNumber"]
        morbin_time_data = await parse_hex(morbin_time_json['data'].split('x')[1])
        morbinTime_result["ftm_buyback"]    = float.fromhex(morbin_time_data[0]) / float(decimal_place)
        morbinTime_result["count"]          = int(float.fromhex(morbin_time_data[1]))
        morbinTime_result["total_ftm"]      = float.fromhex(morbin_time_data[2]) / float(decimal_place)
        morbinTime_result["jackpot_ftm"]    = float.fromhex(morbin_time_data[3]) / float(decimal_place)
        morbinTime_result["jackpot_dollar"] = float.fromhex(morbin_time_data[4]) / float(decimal_place)
        morbinTime_result["timestamp"]      = int(float.fromhex(morbin_time_data[5]))
        print("morbinTime result",morbinTime_result)
        return morbinTime_result
    except:
        print("failed to get prev_morbinTime()")
        return None

async def get_buy_back_morbin_time():
    try:
        print("get_buy_back_morbin_time")
        buyback_morbin_time_get_request = f"{testnetURL}module=logs&action=getLogs&fromblock=0&toblock=90000000&address={morb_token}&topic0={buy_back_for_morbin_time}&apikey={ftm_api_key}"
        print("buyback", buy_back_for_morbin_time)
        morbBuyBack_result = {}
        buyback_morbin_time_json = requests.get(buyback_morbin_time_get_request).json()['result']
        print("second section")
        
        buyback_morbin_time_json = buyback_morbin_time_json[len(buyback_morbin_time_json)-1]
        morbin_time_data = await parse_hex(buyback_morbin_time_json['data'].split('x')[1])
        morbBuyBack_result["morb"]              = float.fromhex(morbin_time_data[0]) / float(decimal_place)
        morbBuyBack_result["total_morb"]        = float.fromhex(morbin_time_data[1]) / float(decimal_place)
        print("morbBuyBack_result",morbBuyBack_result)
        return morbBuyBack_result
    except:
        print("failed to get buy back")
        return None

async def parse_hex(hex):
        print("parse_hex")
        data_count = 0
        hex_data_table = list()
        while data_count < len(hex)//64:
            hex_data_table.append(hex[(data_count)*64:(data_count+1)*64])
            data_count += 1
        return hex_data_table
