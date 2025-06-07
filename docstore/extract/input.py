import json
import openai
import requests
import logging

from bs4 import BeautifulSoup
from docstore.extract.models import EcoiHtmlProperties, OpenAIRequest
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EcoiSearchIds:

    def __init__(self, base_url: str = "https://www.ecoi.net/en/document-search/search-v2"):
        self.base_url = base_url

    def parse_ids(self, html: str) -> List[str]:

        soup = BeautifulSoup(html, 'html.parser')

        # Find all elements with class 'graphbutton-link' 
        # and having the attribute 'data-permalink-target'
        permalink_targets = []
        for link in soup.select('.graphbutton-link[data-permalink-target]'):
            target = link.get('data-permalink-target')
            if target:
                permalink_targets.append(target)

        return permalink_targets

    def search(self, min_date: str, max_date: str) -> List:

        ids = []
        page = 1
        n_pages = None
        n_hits = None
        logging.info(f"Requesting {self.base_url} ({min_date}, {max_date})")
        while True:
            logging.info(f"Requesting page {page}")
            result = requests.get(
                self.base_url,
                params={
                    "lower_origPublicationDate": min_date,
                    "upper_origPublicationDate": max_date,
                    "page": page
                }
            )
            payload = result.json()

            if page == 1:
                n_pages = payload["pages"]
                n_hits = payload["hits"]
                logging.info(f"Expected number of pages: {n_pages}, Expected hits: {n_hits}")

            current_ids = self.parse_ids(payload["content"])
            ids += current_ids
            logging.info(f"Page {page} returned {len(current_ids)} IDs, Total collected: {len(ids)}")


            if page >= n_pages:
                break

            page += 1

        assert len(ids) == n_hits, "Mismatch between expected and actual number of IDs"
        logging.info(f"Search completed successfully. Total IDs collected: {len(ids)}")

        return ids


class HtmlReader:

    def __init__(self, base_url: str = "https://www.ecoi.net/en/document"):
        self.base_url = base_url

    def get_page(self, doc_id: int) -> str:

        return f"{self.base_url}/{doc_id}.html"

    def get_html(self, doc_id: int, extract_class: str = None) -> str:

        response = requests.get(self.get_page(doc_id))
        soup = BeautifulSoup(response.text, "html.parser")

        if "Access error" in str(soup.title):
            return

        if extract_class is not None:
            soup = soup.find("div", class_=extract_class)
        
        return soup

class OpenAIExtractor:

    def __init__(
            self, 
            model: str = "gpt-4.1-nano", 
            api_key_file: str = ""
        ):
        self.model = model
        self.api_key_file = api_key_file
        self.schema = EcoiHtmlProperties.model_json_schema()
        self.text = self.get_text()

        self.get_client()

    def get_client(self):
        with open(self.api_key_file, "r") as f:
            api_key = f.read().replace("\n", "")

        self.client = openai.OpenAI(api_key=api_key)

    def get_text(self) -> Dict[str, Dict[str, Any]]:

        if "additionalProperties" not in self.schema:
            self.schema["additionalProperties"] = False

        return {
            "format": {
                "type": "json_schema",
                "name": "html_info",
                "schema": self.schema,
                "strict": True,
            }
        }

    def input(self, html) -> List[Dict[str, Any]]:

        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": html
                    }
                ]
            }
        ]

    def extract_properties(self, html: str) -> Dict[str, Any]:

        request = OpenAIRequest(
            model=self.model,
            input=self.input(html),
            text=self.text
        )

        params = request.model_dump()
        response = self.client.responses.create(**params)
        output =  response.model_dump()["output"][0]
    
        if "content" in output:
            if len(output["content"]):
                content = output["content"][0]
                if "text" in content:
                    content = json.loads(content["text"])
                    return content
                
        return {}

        
