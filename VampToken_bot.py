import splinter,  nextcord, creds, asyncio, time, TwitterBot, TelegramBot, FTMScanBot
from enum import Enum

dead_address = "0x000000000000000000000000000000000000dead"
isMorbTimeEnabled = True
isJackpotEnabled = True
credentials = creds.get_credentials()
class PostType(Enum):
    Empty = 0
    JackPot = 1
    MorbinTime = 2
    WarningTime = 3
class DisplayType(Enum):
    Leader = 1
    FTM = 2
    Dollar = 0
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
        self.displayType = DisplayType.Leader
        self.loop.create_task(self.main_loop())
        self.stamp =time.time()-400
        
        '''
    The Main loop waits until discord is successfully logged in before
    beginning. then checks what type of message should be shared if it
    exists, then adds the posting of those messages to asyncio's loop
    afterwards sleeping until it is time to check for a new post.
    
    '''
    async def main_loop(self):
        await self.on_ready()
        self.loop.create_task(self.rotate_display())
        #self.loop.create_task(self.jackpot_loop())
        while True:
            try:
                wait_time = 2
                self.post_type = await self.perform_checks()

                print("next step", self.post_type)
                
                if self.post_type != None or self.post_type != PostType.Empty:
                    messages = self.create_post_of_type()
                    print("finished messages", messages)
                    #self.loop.create_task(self.post_twitter(messages))
                    #self.loop.create_task(self.post_telegram(messages))
                    self.loop.create_task(self.send_post(messages))
                    print("finished creating message tasks")
            except Exception as e:
                print("main loop failed due to ",e)
            finally:
                await asyncio.sleep(wait_time)

    async def on_ready(self):
        try:
            await asyncio.sleep(4)
            #await self.fetch_winning_blocks()
            self.fetch_winning_blocks()
            self.last_tx = await FTMScanBot.get_time_extended()
            # print(dBot.user)
        except Exception as e:
            print("Discord bot was unable to log in.")
            print(e)
    # async def jackpot_loop():
    #     while True:
    #         try:

    #             print()
    #         except Exception as e:
    #             print("Jackpot loop failed")
    #             print(e)
    #     pass
    async def rotate_display(self):
        
        while True:
            try:
                if self.displayType == DisplayType.Leader:
                    await self.display_winner()
                if self.displayType == DisplayType.Dollar:
                    await self.display_dollar()
                if self.displayType == DisplayType.FTM:
                    await self.display_FTM()
                print(self.displayType)
                self.displayType = DisplayType((self.displayType.value + 1) % 3)
                await asyncio.sleep(5)
            except Exception as e:
                print("unable to rotate status")
                print(e)
            else:
                print(self.displayType.value)
    '''**********************************************Messaging*******************************************'''
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

    '''
    Creates the messages to be shared
    Returns the created messages
    '''
    def create_post_of_type(self):
        lMessage = []
        isMinutes = "minutes"
        if self.post_type ==  PostType.WarningTime:
            jackpot_time = int(self.last_tx["jackpot_time"] - time.time()) /60 
            if jackpot_time < 1:
                jackpot_time *= 60
                isMinutes = "seconds"
            jackpot_time = round(jackpot_time)
            
            lMessage.append(f"Heads up! \n{self.last_tx['address']}\n is in the lead at {self.last_tx['jackpot_amount_dollar']:.2f}$ Jackpot will be awarded in {jackpot_time} {isMinutes}!")
            if self.last_tx['address'] == dead_address:
                lMessage.clear()
                lMessage.append(f"No one has claimed the jackpot worth {self.last_tx['jackpot_amount_dollar']:.2f}$")
        if self.post_type ==  PostType.MorbinTime:
            print("MorbinTime message")
            lMessage.append(f"ITS MORBIN TIME! {round(self.morbTime['ftm_buyback'])} FTM used to buyback and burn {round(self.morb_buyback['morb'])} VAMP.")
            lMessage.append(f"{round(self.morb_buyback['morb'])} VAMP has been destroyed forever. Total VAMP burned so far {self.morb_buyback['total_morb']:2f} VAMP")
            #lMessage.append(f"MorbinTime has occurred {self.morbtime['count']} Total VAMP burned {self.buyback['total_morb']:.4f}. Total FTM used: {self.morbtime['total_ftm']:.4f}")
            lMessage.append(f"Another {self.morbTime['jackpot_ftm']:.4f} FTM ({self.morbTime['jackpot_dollar']:.2f}$) has been seeded into the jackpot!")
            
        if self.post_type ==  PostType.JackPot:
            print("Jackpot Message")
            lMessage.append(f"WE HAVE A JACKPOT WINNER!\n {self.jackpot['address']}\n congratulations on winning {self.jackpot['ftm_award']:.4f}$" )
            lMessage.append(f"Another {self.jackpot['ftm_balance']:.2f} FTM ({self.jackpot['dollar_balance']}$) has been seeded into the jackpot!")
            lMessage.append(f"The jackpot has been won {self.jackpot['count']} times. Total FTM dispersed: {self.jackpot['total_ftm']} Total Dollars Won: {self.jackpot['total_dollar']:.2f}$")
            if self.jackpot_buyback is not None:
                lMessage.append(f"{self.jackpot['ftm_buyback']} FTM was used to burn {self.jackpot_buyback['burned_morb']} VAMP." )
                lMessage.append(f"Total VAMP burned: {self.jackpot_buyback['total_burned_morb']}")
            
        if self.post_type ==  PostType.Empty or self.post_type == None:
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
            with splinter.Browser('firefox', headless=True) as browser:
                twitter_bot = TwitterBot.TwitterBot()
                await twitter_bot.login(browser)
                await asyncio.sleep(5)
                for msg in msgs:
                    await twitter_bot.post(msg)
                    await asyncio.sleep(10)
        except Exception as e:
            creds.log(f"Firefox Failed trying Chrome - {time.localtime()}")
            try:
                with splinter.Browser('chrome', headless=True):
                    twitter_bot = TwitterBot.TwitterBot()
                    await twitter_bot.login(browser)
                    await asyncio.sleep(5)
                    for msg in msgs:
                        await twitter_bot.post(msg)
                        await asyncio.sleep(10)
            except:
                creds.log(f"Chrome failed stopping Twitter bot - {time.localtime()}")
                
 
        pass

    '''***************************************************State Changing****************************************************'''
    async def display_winner(self):
        try:
            name = self.last_tx["address"]
            
            if name == dead_address:
                name = "Unclaimed Pot"
            print("current leader", name)
            await self.change_presence(activity=nextcord.Game(name=name))
        except Exception as e:
            print("failed to set gaming status")
            print(e)

    async def display_dollar(self):
        try:
            dollar = self.last_tx["jackpot_amount_dollar"]
            print("current_dollar: ", dollar)
            await self.change_presence(activity=nextcord.Game(name=f"{dollar:.2f}$"))
        except Exception as e:
            print("failed to display dollars")
            print(e)

    async def display_FTM(self):
        try:
            ftm = self.last_tx["jackpot_amount_FTM"]
            print("current_ftm: ", ftm)
            await self.change_presence(activity=nextcord.Game(name=f"{ftm:.2f} FTM"))
        except Exception as e:
            print("failed to display fantom")
            print(e)

                            
    '''******************************************************Checks********************************************************'''
    '''
    performs the checks that will set the PostType
    '''
    async def perform_checks(self):
        try:
            self.post_type = PostType.Empty
            if await self.check_morbin_time():
                print("MorbinTime")
                
                return PostType.MorbinTime
            elif await self.check_jackpot_time():
                print("JackpotTIme")
                
                return PostType.JackPot
            elif await self.check_time_to_warn():
                print("warningtime")
                return PostType.WarningTime
        except Exception as e:
            print("performing checks failed")
            print(e)
        

    '''
    Fetches information from FTMScanBot compares it and sets post_type to 
    the type of post needed to be distributed
    see if it is morbin time, return yes if 1 new transaction has occured
    replace information in morbtime and morb_buyback
    '''
    async def check_morbin_time(self):
        try:
            previous_morbTime = self.last_morbtime_block
            self.morbTime = await FTMScanBot.get_morbinTime()
            if previous_morbTime != self.morbTime["block"]:
                self.morb_buyback = await FTMScanBot.get_buy_back_morbin_time()
                self.last_morbtime_block = self.morbTime["block"]
                await self.finish_morbin_time()
                return True
                
            print("it is not morbin time")
            return False
        except Exception as e:
            print("check_morbin_time failed because", e)
            return False
    '''

    Fetches and sets Jackpot Buyback variables
    checks if previous jackpot buyback is the same as the current

            print("self.last_tx=={}",self.last_tx == {})
            if self.last_tx == {}:
                self.last_tx = await FTMScanBot.get_time_extended()   
                print("\n",self.last_tx)
                return False
            previous_tx = self.last_tx["timestamp"]
            self.last_tx = await FTMScanBot.get_time_extended()
    '''
    async def check_jackpot_time(self):
        try:
            print("checking Jackpot")
            self.jackpot = await FTMScanBot.get_jackpot()
            previous_jackpot = self.last_jackpot_award
            print(previous_jackpot, self.jackpot["block"])
            if self.jackpot["block"] != previous_jackpot:
                print("Jackpot!")
                self.jackpot_buyback = await FTMScanBot.get_jackpot_buyback()
                self.last_jackpot_award = self.jackpot["block"]
                await self.finish_morbin_time()
                print("finished morbintime")
                return True
            print("jackpot was not activated")
            return False
        except Exception as e:
            print("check jackpot failed because ", e)
            return False
    '''
    fetches the current leader of the jackpot. sets the information and returns true if:
    1. a leader changes (once per 3 ish minutes) or
    2. a reducing rate of one half ie buyer buys at 10 minute mark. then it warns at 10 5 2.5 1.25 .6125 etc terminating at the 
    10 second mark.
    This may need to use a seperate function that con be called from morbin/jackpot time to reset the timer
    if self.last_tx != prev :     
    #reset value
    stamp = self.last_tx["jackpottime"] - self.last_tx["timestamp"] // 2
    else 
    stamp = stamp + ((self.last_tx["timestamp"]- stamp) // 2)

    '''
    async def check_time_to_warn(self):
        try:
            print("checkWarning", self.last_tx)
            if self.last_tx == {}:
                self.last_tx = await FTMScanBot.get_time_extended()   
                print("\n",self.last_tx)
                return False
            previous_tx = self.last_tx["timestamp"]
            self.last_tx = await FTMScanBot.get_time_extended()
            if time.time() > self.stamp and time.time()  < self.last_tx['jackpot_time']:
                print("time is past Stamp , resetting self.stamp")
                if previous_tx != self.last_tx["timestamp"]:
                    self.stamp = self.last_tx["timestamp"]
                self.stamp += ((self.last_tx["jackpot_time"] - self.stamp ) //2)

                return True
            
            
            print("not time to warn")
            return False
        except Exception as e:
            print("warning time failed because of ", e)
            return False
    # async def check_jackpot_extended(self):
    #     self.last_tx = await FTMScanBot.get_time_extended()
    #     print("warnBool",self.bwarn_time)
    #     if self.last_tx != None or self.bwarn_time == False:
    #         self.bwarn_time = True
    #         time_to_pot = (self.last_tx["jackpot_time"] - time.time())
    #         print("time_to_pot",time_to_pot)
    #         await self.time_to_warn( time_to_pot // 2)
    '''
    Warning Functions

    '''
    # async def check_time_to_warn(self):
    #     if self.jackpot["jackpot_time"] -self.jackpot['timestamp'] // 2  > self.jackpot['jackpot_time'] - time.time():
    #         await self.time_to_warn(self.jackpot['jackpot_time'] - time.time())

    # async def time_to_warn(self,_time):

    #         print("time_to_warn", _time//2)
    #         if _time < 1:
    #             self.post_type = PostType.Empty
    #             self.bwarn_time = False
    #             return 
    #         print("Time",_time)
    #         await asyncio.sleep(_time)
    #         print("check here post time check")
    #         self.post_type = PostType.WarningTime
    #         self.loop.create_task(self.finish_morbin_time())
    #         self.loop.create_task(self.time_to_warn(_time // 2))

    async def finish_morbin_time(self):
        try:
            creds.write_winning_block(self.last_jackpot_award,self.last_morbtime_block)
            self.fetch_winning_blocks()
        except Exception as e:
            print("failed to finish morbin time because", e)

    '''
    This will fetch the last winning blocks from winningblock.log
    '''
    def fetch_winning_blocks(self):
        new_blocks = creds.get_last_previous_block()
        self.last_jackpot_award = new_blocks[0]
        self.last_morbtime_block = new_blocks[1]
        print("last award: ",self.last_jackpot_award)
        print("last Morb: ", self.last_morbtime_block)


