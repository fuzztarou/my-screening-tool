from config.config import Config

def main():

    # Initialize configuration
    conf = Config()
    print("Hello from jq-screening!")
    print(f"Email: {conf.MY_EMAIL}")
    print(f"JPX Password: {conf.JPX_PASSWORD}")

if __name__ == "__main__":
        main()
