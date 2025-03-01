import os
import json
import base64
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from encrypt import EncryptionManager

class RekaAIClient:
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "accept": "*/*",
            "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://chat.reka.ai",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://chat.reka.ai/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        }
        self._setup_session()

    def _setup_session(self) -> None:
        try:
            load_dotenv()
            proxy_string = os.getenv('PROXY')
            if proxy_string:
                self.session.proxies = {
                    "http": f"http://{proxy_string}",
                    "https": f"http://{proxy_string}"
                }
        except Exception as e:
            raise Exception(f"Failed to setup session: {str(e)}")

    def _prepare_request_data(self, human_text: str, image_file: Optional[str] = None, 
                            image_usage: bool = False) -> Dict[str, Any]:
        try:
            encryption_manager = EncryptionManager()
            imported_key = encryption_manager.import_key()
            derived_key = encryption_manager.derive_key(imported_key)
            encrypted_output = encryption_manager.encrypt(derived_key, human_text)

            conversation_history = []
            if image_usage and image_file:
                try:
                    with open(image_file, "rb") as f:
                        base64image = base64.b64encode(f.read()).decode('utf-8')
                    conversation_history.append({
                        "type": "human",
                        "text": human_text,
                        "media_url": f"data:image/png;base64,{base64image}",
                        "media_type": "image"
                    })
                except Exception as e:
                    raise Exception(f"Failed to process image file: {str(e)}")
            else:
                conversation_history.append({"type": "human", "text": human_text})

            return {
                "conversation_history": conversation_history,
                "stream": True,
                "model_name": "reka-flash",
                "random_seed": encrypted_output
            }
        except Exception as e:
            raise Exception(f"Failed to prepare request data: {str(e)}")

    def send_message(self, human_text: str, image_file: Optional[str] = None, 
                    image_usage: bool = False) -> str:
        try:
            data = self._prepare_request_data(human_text, image_file, image_usage)
            response = self.session.post(
                "https://chat.reka.ai/bff/chat",
                headers=self.headers,
                data=json.dumps(data, separators=(",", ":"))
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code: {response.status_code}")

            response.encoding = 'utf-8'
            try:
                value = json.loads(str(response.text.split('data: ')[-1][:-1]))
                return value["text"]
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                raise Exception(f"Failed to parse API response: {str(e)}")
                
        except requests.RequestException as e:
            raise Exception(f"Network request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}") 