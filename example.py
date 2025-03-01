from client import RekaAIClient

def main():
    try:
        client = RekaAIClient()
        try:
            response = client.send_message(
                "make me a joke",
                image_file="image.png",
                image_usage=False
            )
            print("Response:", response)
        except Exception as e:
            print("Error", str(e))

    except Exception as e:
        print("Fatal error:", str(e))

if __name__ == "__main__":
    main() 