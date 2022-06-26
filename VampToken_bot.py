from operator import indexOf
from queue import Empty
import splinter, requests, nextcord, secrets, asyncio, time, TwitterBot, TelegramBot, FTMScanBot
from enum import Enum
credentials = secrets.get_credentials()

class PostType(Enum):
    Empty = 0
    JackPot = 1
    MorbinTime = 2
    WarningTime = 3
class VampToken_bot(nextcord.Client):
    def __init__(self):
        super().__init__()
        self.iTime_to_morb = 0
        self.post_type = PostType.Empty
        self.sMessage = ""
        self.iChannel = int(credentials["DiscordChannel"])
        self.morb_trigger = 100000
        self.max_morb_countdown = 99999 # minutes before warning must occur
        self.last_tx = {}
        self.loop.create_task(self.main_loop())
    '''
    This sends a message to Discords API
    '''
    async def post(self, message):
        try:
            await dBot.get_channel(self.iChannel).send(message)
        except:
            "unsuccessful post"
    async def post_image(self, message, image):
        try:
            await dBot.get_channel(self.iChannel).send(message, image)
        except: 
            "unseccessful post"

    async def on_ready(self):
        try:
            await asyncio.sleep(4)
            print(dBot.user)
        except:
            pass
        pass


    '''
    The Main loop waits until discord is successfully logged in before
    beginning. then checks what type of message should be shared if it
    exists, then adds the posting of those messages to asyncio's loop
    afterwards sleeping until it is time to check for a new post.
    
    '''
    async def main_loop(self):
        await self.on_ready()
        while True:
            try:
                await self.check_morbin_time()
                print("next step")
                
                if self.post_type != PostType.Empty:
                    messages = await self.create_post_of_type()
                    self.loop.create_task(self.post_twitter(messages))
                    self.loop.create_task(self.post_telegram(messages))
                    self.loop.create_task(self.send_post(messages))
            except Exception as e:
                print(e)
                self.post_type = PostType.Empty
            finally:

                
                wait_time = 200 # catch in case last_tx isn't initialized
                try:
                    if (self.last_post_time - time.time()) > 15:
                        #print("time diff", self.last_tx['jackpot_time']-time.time())
                        wait_time = (float(self.last_tx["jackpot_time"] - time.time())//120+1 )
                except:
                    pass
                finally:
                    print("Time until next check: ", wait_time)
                    await asyncio.sleep(wait_time)

    '''
    Creates the messages to be shared
    Returns the created messages
    '''
    async def create_post_of_type(self):
        lMessage = []
        match self.post_type:
            case PostType.WarningTime:
                jackpot_time = int(self.last_tx["jackpot_time"] - time.time())//60+2#time.time()) // 60
                lMessage.append(f"Heads up! \n{self.last_tx['address']}\n is in the lead at {self.last_tx['jackpot_amount_dollar']:.2f}$ Jackpot will be awarded in {jackpot_time} minutes!")

            case PostType.MorbinTime:
                lMessage.append(f"ITS MORBIN TIME! FTM used to buy back VAMP {self.morbtime['ftm_buyback']:.4f} Amount of VAMP Burned: {self.buyback['morb']:.4f}.")
                lMessage.append(f"MorbinTime has occurred {self.morbtime['count']} Total VAMP burned {self.buyback['total_morb']:.4f}. Total FTM used: {self.morbtime['total_ftm']:.4f}")
                lMessage.append(f"Another {self.morbtime['jackpot_ftm']:.8f} FTM ({self.morbtime['jackpot_dollar']:.2f}$) has been seeded into the jackpot!")
                
            case PostType.JackPot:
                lMessage.append(f"WE HAVE A JACKPOT WINNER!\n {self.jackpot['address']}\n congratulations on winning {self.jackpot['ftm_award']:.4f}" )
                lMessage.append(f"Another {self.jackpot['ftm_balance']:.2f} FTM ({self.jackpot['dollar_balance']}$) has been seeded into the jackpot!")
                lMessage.append(f"The jackpot has been won {self.jackpot['count']} times. Total FTM dispersed: {self.jackpot['total_ftm']} Total Dollars Won: {self.jackpot['total_dollar']:.2f}$")
                lMessage.append(f"{self.jackpot['ftm_buyback']} FTM was used to burn {self.buyback['morb']} VAMP." )
                lMessage.append(f"Total VAMP burned: {self.buyback['total_morb']} using {self.jackpot['total_ftm']} FTM")
                
            case PostType.Empty:
                return []
        return lMessage
    '''
    Posts to Discord
    '''
    async def send_post(self, msgs):
        for msg in msgs:
            self.loop.create_task(self.post(msg))
    '''
    Tells TelegramBot.py to post
    '''
    async def post_telegram(self, msgs):
        try:
            telegram_bot= TelegramBot.TelegramBot()
            await telegram_bot.getUpdates()
            for msg in msgs:
                await telegram_bot.post(msg)
        except Exception as e:
            print("Something is wrong with the telegram bot: ", str(e))
        
    '''
    Tells TwitterBot.py to post
    '''
    async def post_twitter(self, msgs):
        try:
            with splinter.Browser() as browser:
                twitter_bot = TwitterBot.TwitterBot()
                await twitter_bot.login(browser)
                await asyncio.sleep(5)
                for msg in msgs:
                    await twitter_bot.post(msg)
                    await asyncio.sleep(10)
        except Exception as e:
            print("Something is wrong with the Twitter bot \n", str(e))
 
        pass

    '''
    Fetches information from FTMScanBot compares it and sets post_type to 
    the type of post needed to be distributed
    '''
    async def check_morbin_time(self):
        self.last_tx = await FTMScanBot.get_jack_pot_time()
        self.jackpot = await FTMScanBot.get_jackpot_award()
        self.buyback = await FTMScanBot.get_buy_back_morbin_time()
        self.morbtime = await FTMScanBot.get_morbinTime()
        await self.fetch_winning_blocks()
        self.post_type = PostType.Empty
        self.iTime_to_morb = self.last_tx["timeStamp"] // 60
        
        if  self.morbtime["block"] != last_morbtime_block:
            self.post_type = PostType.MorbinTime

        elif last_jackpot_award != self.jackpot["block"]:
            self.post_type = PostType.JackPot

        elif self.iTime_to_morb < time.time() // 60+10:           
            self.post_type = PostType.WarningTime
        print("post_type: ", self.post_type)
        secrets.write_winning_block(self.morbtime["block"],self.jackpot["block"])
        self.loop.create_task(self.fetch_winning_blocks())
    '''
    This will fetch the last winning blocks from winningblock.log
    '''
    async def fetch_winning_blocks(self):
        global last_jackpot_award, last_morbtime_block
        new_blocks = secrets.get_last_winning_block()
        last_jackpot_award = new_blocks[1]
        last_morbtime_block = new_blocks[0]

dBot = VampToken_bot()

#print(', '.join("%s: %s" % item for item in attrs.items()))
dBot.run(credentials['DiscordAPIKey'])