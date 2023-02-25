from VampToken_bot import VampToken_bot
import creds
def main():
    dBot = VampToken_bot()
    credentials = creds.get_credentials()
    dBot.run(credentials['DiscordAPIKey'])
if __name__ == "__main__":
    main()